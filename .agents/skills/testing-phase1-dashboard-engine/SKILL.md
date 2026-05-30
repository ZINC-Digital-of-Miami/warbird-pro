---
name: testing-phase1-dashboard-engine
description: Test the Phase 1 dashboard (LWC v5 chart scaffold) and engine modules (DuckDB init, seed, trade log, fib engine) end-to-end. Use when verifying dashboard rendering, engine schema, or data pipeline changes.
---

## Overview

Phase 1 includes two testable surfaces:
1. **Dashboard** (`dashboard/index.html`, `chart.js`, `style.css`) — static HTML+JS chart using Lightweight Charts v5 via CDN
2. **Engine** (`engine/`) — Python modules for DuckDB schema, symbol seeding, trade logging, fib computation

## Prerequisites

- Python 3.12+ with `duckdb`, `pytest`, `pytest-cov` installed
- `PYTHONPATH` must include the repo root for engine module imports
- No npm build step needed for dashboard (plain HTML)

## Running Engine Tests

```bash
cd /path/to/warbird-pro
PYTHONPATH=$(pwd) python -m pytest tests/engine/ -v --tb=short
```

Expected: 55 tests pass in ~1s.

## Verifying DuckDB Init

```bash
rm -f data/warbird_trades.duckdb
PYTHONPATH=$(pwd) python engine/init_db.py
```

Expected output:
- "Tables created: 43"
- "Total: 43 tables across 10 groups"
- All tables marked `[ok]`, zero `[MISSING]`

## Verifying Symbol Seeding

```bash
PYTHONPATH=$(pwd) python engine/seed_duckdb.py
```

Expected: "Seeded 20 active symbols" (17 Databento + 3 FRED)

## Verifying SHORT Trade PnL Fix

```bash
PYTHONPATH=$(pwd) python -c "
from engine.trade_log import record_trade, close_trade, TradeEntry
import duckdb, os
from engine.config import TRADE_LOG_DB

entry = TradeEntry(direction='SHORT', entry_price=5400.0, timeframe='5m')
tid = record_trade(entry)
close_trade(tid, exit_price=5390.0, result='WIN')

conn = duckdb.connect(os.path.abspath(TRADE_LOG_DB))
row = conn.execute('SELECT pnl_pts FROM trades WHERE id = ?', [tid]).fetchone()
conn.close()
print(f'pnl_pts = {row[0]}')  # Should be +10.0
"
```

**Key:** PnL for SHORT = entry_price - exit_price. Positive when price drops.

## Dashboard Browser Testing

1. Open `file:///path/to/warbird-pro/dashboard/index.html` in Chrome
2. Verify:
   - Dark theme background (gradient #131722 to #0d1117)
   - Chart area is EMPTY on initial load (zero fake data)
   - Correlations row at top: NQ, 6E, CL, ZN with "--" values
   - Cards panel (320px sidebar): Entry Signal="WAIT", prices="--"
   - Legend bar: "200 SMA", "Bull" (cyan box), "Bear" (red box)
   - Pressure bar below chart
   - Nexus placeholder at bottom: "Nexus ML RSI (Phase 5)"

3. Test data APIs via browser console:
   ```js
   // Push single bar (up candle = cyan)
   globalThis.pushBar({time: 1716000000, open: 5400, high: 5410, low: 5395, close: 5405});
   // Push down candle (red)
   globalThis.pushBar({time: 1716000300, open: 5405, high: 5420, low: 5390, close: 5398});
   ```
   Expected: 2 candles appear — cyan up (#26C6DA), red down (#FF0000), white wicks

4. Test batch load:
   ```js
   globalThis.loadBars([...arrayOf10Bars...]);
   ```
   Expected: All bars rendered with correct time axis

## Common Pitfalls

- **ModuleNotFoundError for engine**: Set `PYTHONPATH=$(pwd)` before running Python commands
- **TRADE_LOG_DB path**: The trade log uses `data/warbird_trades.duckdb` (same as DUCKDB_PATH), not a separate file
- **file:// URL in Chrome**: Make sure to type the full `file:///` prefix in the address bar. Chrome may treat it as a Google search if the URL is malformed.
- **Supabase grep false positives**: `seed_duckdb.py` references `supabase/seed.sql` as a file path — these are NOT supabase client imports. Grep for `import.*supabase` or `from supabase` to check for actual library usage.
- **Zero fake data policy**: Dashboard must initialize empty. No Math.random(), no generateSampleData(), no hardcoded OHLCV bars. Chart awaits real WebSocket data via pushBar()/loadBars() APIs.

## Devin Secrets Needed

None required for Phase 1 testing. All tests run locally with no external API calls.
