# Hard Rules

## Data

- **Local-first data policy:** FRED, macro, news, options, and cross-asset data are now allowed since the system is local and not constrained by TradingView
- Approved sources: Pine/TV exports, Databento ES market-data, FRED, news feeds, any data accessible locally
- Data quality matters: all sources must be manifest-backed with honest labeling
- Databento rows are market data — never label as `TRADINGVIEW_INDICATOR_CSV`

## Pine

- NEVER edit `indicators/warbird-pro-v9.pine` without explicit approval in the current session
- NEVER edit Nexus Pine files without explicit approval
- NEVER push Pine changes to TradingView Pine Editor without explicit approval
- Fib anchor ownership, ladder math, and trade-state label semantics are protected scope
- Never reintroduce the pivot-window `fibHtfSnapshot` variant — banned due to wide-fib regressions
- Only 10 output slots remain before 64-call hard cap — price every new `plot()` or `alertcondition()`

## TradingView Safety (CDP-Down Protocol)

If ANY TradingView MCP call fails because CDP is unresponsive: **STOP IMMEDIATELY**. Report "CDP is not responding. I'm stopped. Waiting for instructions." Do NOT attempt recovery. Banned: `tv_launch`, `tv_health_check` as probe, `launch_tv_debug_mac.sh`, process kills.

## Cloud / Database

- Cloud Supabase is runtime/support only — no raw trials, labels, or research datasets
- DuckDB for all local data, trade recording, and modeling
- No Prisma, Drizzle, or ORM
- Local PG17 `warbird` warehouse is legacy/reference only

## Modeling

- Past testing results (including 15m/5m/1h baselines from 2026-04-27) are skewed and should NOT be relied upon
- Model selection (AutoGluon families, hyperparameters) is TBD — do not assume the full-zoo config is active
- Deep research on models, data sources, and architecture is required before committing to any training approach
