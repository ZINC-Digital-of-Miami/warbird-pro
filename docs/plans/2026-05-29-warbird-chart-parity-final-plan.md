# Warbird Pro — Chart Parity Final Multiphase Plan

**Date:** 2026-05-29
**Status:** ACTIVE — Phase 0 accepted
**Artifact path:** `docs/plans/2026-05-29-warbird-chart-parity-final-plan.md`
**Governing authority:** `agents/skills/chart-parity-authority/SKILL.md` (v2.4.1)
**Correction proposal:** `docs/packet_plan_v2.4.1_correction_proposal.md`
**Repo:** `/Volumes/Satechi Hub/warbird-pro` on `main`

> This plan converts the full locally imported PR #14 authority into executable
> future phases. It does NOT execute those phases. Implementation begins only
> after Kirk and Codex QA accept this plan.

---

## 1. Authority Map

### Files Read (in order)

| # | File | Purpose |
|---|------|---------|
| 1 | `AGENTS.md` | Repo rules, hard constraints, governance precedence |
| 2 | `docs/handoffs/2026-05-29-devin-chart-parity-launch-packet.md` | Launch packet for this plan-build run |
| 3 | `docs/plans/2026-05-29-warbird-chart-parity-build-playbook.md` | Plan-build brief and Codex QA gate |
| 4 | `.devin/rules/01-project-overview.md` | Project overview with chart parity authority reference |
| 5 | `.devin/rules/08-chart-parity-authority.md` | Chart parity rule — PR status, non-negotiables, closeout |
| 6 | `.devin/rules/09-review-sonic-feedback.md` | Sonic/review workflow, self-heal loop, no auto-mutation |
| 7 | `.devin/rules/10-session-insights.md` | Session Insights retrospective, 13c8 standing lesson |
| 8 | `.devin/knowledge-blueprint.md` | Devin Knowledge set for Warbird |
| 9 | `docs/handoffs/2026-05-29-devin-session-13c8-retrospective.md` | Session 13c8 failure patterns and corrective actions |
| 10 | `agents/skills/chart-parity-authority/SKILL.md` | **PRIMARY AUTHORITY** — v2.4.1 locked rulings (read top-to-bottom) |
| 11 | `docs/packet_plan_v2.4.1_correction_proposal.md` | Corrected change-set, resolved decisions, testing plan |

### PR SHAs

| PR | Branch | Head SHA | Status |
|----|--------|----------|--------|
| #14 | `devin/1780027391-chart-parity-authority-skill` | `b9bfab46` | Closed — partial-import only. Accepted locally: SKILL.md, correction proposal, manifest/README updates. NOT merged. |
| #11 | `devin/1779988864-warbird-command-center` | `9cca2d78` | Closed — source inventory only. NOT merged. NOT a merge candidate. |

### Source-of-Truth Precedence (highest first)

1. Kirk's live verbal/chat rulings (current session)
2. `agents/skills/chart-parity-authority/SKILL.md` v2.4.1
3. `docs/packet_plan_v2.4.1_correction_proposal.md`
4. `AGENTS.md` (repo-wide governance)
5. `indicators/warbird-pro-v9.pine` (visual/logic authority — read-only)
6. `engine/fib_engine.py` on PR #11 branch (computation authority — cherry-pick only)
7. `components/charts/LiveMesChart.tsx` on main (chart behavior source)
8. `docs/DEVIN_PLATFORM_PLAN.md` (superseded planning snapshot — reference only)

---

## 2. Full Coverage Map

Every section/ruling in `agents/skills/chart-parity-authority/SKILL.md` mapped to a phase, artifact, or explicit deferral.

| SKILL.md Section | Ruling Summary | Phase | Artifact |
|---|---|---|---|
| Chart Stack | LWC renderer, port LiveMesChart.tsx exact, strip autofib-v16 | Phase 1 | `dashboard/index.html`, `dashboard/chart.js` |
| Fib System | `engine/fib_engine.py` sole engine, visuals from Pine, bounded draw | Phase 2 | Fib rendering code, AT-1 evidence |
| Moving Averages | EMA21+EMA9 from indicator, add 200 SMA white 2pt | Phase 2 | MA overlay code |
| V9 Transfer Directive | Transfer EXACT indicator to LWC dashboard | Phase 2 | Full indicator port evidence |
| Layout (Locked) | Correlations → Chart+Cards → Pressure → Nexus | Phase 3 | Layout CSS/HTML, screenshot proof |
| Cards Panel | Entry Signal, Entry Price, SL, TP1, TP2, AI Analysis, Win Rate (if real) | Phase 3 | Cards panel code |
| Volume / Pressure | Databento trades A/B/N, quality gate, LOW→WAIT | Phase 4 | Pressure bar code, AT-2/AT-3 evidence |
| Correlations Row | NQ/6E/CL/ZN, 1h Databento Historical API pull, isolated timing | Phase 5 | Correlations row code |
| Git Protocol | main only, cherry-pick engine/ from PR #11, discard PR #11 frontend | All phases | Git log evidence |
| AI Analysis | Gemini (not OpenRouter), real-time data analysis + S&P/Fed/Mag7 news | Phase 6 | `engine/ai_analysis.py` |
| Error Patterns | 12 documented anti-patterns | All phases | Error checklist in closeout |
| Canonical TF | 5m default, 1m/3m/5m/15m, cards update with TF, correlations always 1h | Phase 3 | TF switching code |
| Acceptance Tests | AT-1 (bounded fibs), AT-2 (trades A/B/N), AT-3 (LOW→WAIT) | Phase 7 | AT evidence packets |
| Mandatory Doc Sync | All docs updated in same commit when ruling changes | Phase 8 | Doc sync evidence |

### Correction Proposal Sections Mapped

| Proposal Section | Phase |
|---|---|
| 1. TradingView chart stack | Phase 1 |
| 2. Correlations cadence 1h | Phase 5 |
| 3. Remove volume histogram + wrong cards | Phase 3 |
| 4. Databento trades schema + A/B/N | Phase 4 |
| 5. Trades-side delta + confidence gate | Phase 4 |
| 6. Fibonacci — use exact engine | Phase 2 |
| 6c. Visible ladder = 13 | Phase 2 |
| 7. Accuracy audit — claims vs reality | Phase 6 (AI), Phase 8 (docs) |
| 8. Corrected change-set summary | All phases |
| 9. Testing plan | Phase 7 |
| 10. Decisions (all resolved) | N/A — no open questions |
| 11. Packet version history | Phase 8 (doc sync) |

---

## 3. PR #11 Keep/Discard Map

PR #11 (`devin/1779988864-warbird-command-center`) is source inventory only. Its dashboard frontend is DISCARDED. Cherry-pick targets are engine-only.

| Surface | Decision | Phase | Notes |
|---|---|---|---|
| `engine/fib_engine.py` | **KEEP — cherry-pick** | Phase 1 | Sole fib computation engine. Used AS-IS. No modifications. |
| `engine/trade_log.py` | **KEEP — cherry-pick** | Phase 1 | DuckDB trade log schema (trades, trade_tags, indicator_state). Fix PnL bug for SHORT trades (Devin Review finding). |
| `engine/databento_feed.py` | **KEEP — cherry-pick** | Phase 1.5 | Databento Live subscription. Add trades-schema path in Phase 4. Add client-presence lifecycle. |
| `engine/bar_store.py` | **KEEP — cherry-pick** | Phase 1.5 | Multi-TF bar aggregation (1m→1/3/5/15m/1h/4h). Fix thread-safety issues flagged by Codacy. |
| `engine/server.py` | **KEEP — cherry-pick** | Phase 1.5 | FastAPI on port 3100 + WebSocket push. Add client-presence-aware lifecycle (COLD/WARM states). |
| `engine/config.py` | INSPECT, conditional | Phase 1.5 | Review for Databento key handling. Add approved schemas/symbols allowlist. |
| `engine/indicators.py` | INSPECT, conditional | Phase 2 | Contains candle-body proxy at :438-447. Replace with real trades-side delta in Phase 4. |
| `engine/trigger_engine.py` | INSPECT, conditional | Phase 4 | Contains LOW→WAIT gate logic at :211-217. Verify and test. |
| `engine/ai_analysis.py` | INSPECT, conditional | Phase 6 | Currently uses OpenRouter. Must switch to Gemini per Kirk's ruling. |
| `engine/nexus.py` | INSPECT, conditional | Phase 5 | Nexus ML RSI / AMF oscillator. Port minus TradingView-centric items. |
| `engine/pressure.py` | INSPECT, conditional | Phase 4 | Pressure bar computation. Verify weights: volume delta 30%, RSI 25%, momentum 20%, TTM squeeze 25%. |
| `dashboard/index.html` | **DISCARD** | — | LWC-based frontend. Rebuild from LiveMesChart.tsx exact settings. |
| `dashboard/app.js` | **DISCARD** | — | Contains wrong cards (Fib Structure, System), volume histogram, 15m conviction label. |
| `dashboard/style.css` | **DISCARD** | — | Rebuild layout from SKILL.md locked layout diagram. |
| `dashboard/nexus.js` | **DISCARD** | — | Rebuild Nexus sub-chart rendering. |
| `dashboard/correlations.js` | **DISCARD** | — | Rebuild correlations row rendering. |
| `docs/DASHBOARD_PLAN.md` | **DISCARD** | — | Superseded by this plan. |

### Approval Required Before Reuse

Any PR #11 surface not listed as "KEEP — cherry-pick" above requires Kirk's explicit approval before being brought to main. The conditional-keep items will be evaluated during their respective phases — if the code is clean enough to use, it gets used; if not, it gets rewritten to match SKILL.md exactly.

---

## 4. DuckDB Schema Inventory

All tables created in Phase 1 via `engine/init_db.py` at `data/warbird_trades.duckdb` (gitignored, initialized on first use). Tables are created empty and populated in their respective phases.

### Group 1 — MES OHLCV Bars (7 tables)

**Populated by:** Phase 1 (seeded from local batch files), Phase 1.5 (live data)
**Dashboard surface:** Chart rendering, TF switching, fib/MA computation

| Table | Schema |
|---|---|
| `mes_1m` | `ts TIMESTAMPTZ PRIMARY KEY, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume BIGINT` |
| `mes_3m` | same as `mes_1m` |
| `mes_5m` | same as `mes_1m` |
| `mes_15m` | same as `mes_1m` |
| `mes_1h` | same as `mes_1m` |
| `mes_4h` | same as `mes_1m` |
| `mes_1d` | same as `mes_1m` |

Note: Supabase has 5 tables (1m/15m/1h/4h/1d). DuckDB needs 7 because SKILL.md requires 1m/3m/5m/15m for TF switching plus 1h/4h/1d for correlations and daily bias context. The `engine/bar_store.py` already aggregates 1m → all higher TFs.

### Group 2 — Trades-Side Volume (2 tables)

**Populated by:** Phase 1 (seeded from local MES ES Trades zip), Phase 4 (live trades)
**Dashboard surface:** Pressure bar, confidence gate (AT-2, AT-3)

| Table | Schema |
|---|---|
| `trades_raw` | `ts TIMESTAMPTZ, price DOUBLE, size INTEGER, side TEXT CHECK(side IN ('B','A','N'))` |
| `trades_volume` | `ts TIMESTAMPTZ, timeframe TEXT CHECK(timeframe IN ('1m','3m','5m','15m')), buy_vol BIGINT, sell_vol BIGINT, unknown_vol BIGINT, delta BIGINT, total_vol BIGINT, confidence TEXT CHECK(confidence IN ('HIGH','LOW')), PRIMARY KEY(ts, timeframe)` |

The `trades_volume` table is TF-aware — single table with a timeframe column, not per-TF tables. Confidence is derived: `unknown_vol / total_vol > 0.30 → LOW`. When LOW, force WAIT (AT-3).

### Group 3 — Correlations (1 table)

**Populated by:** Phase 1 (seeded from local parquet), Phase 5 (1h Databento Historical API pulls)
**Dashboard surface:** Correlations row (4 symbols, 1h isolated timing)

| Table | Schema |
|---|---|
| `cross_asset_1h` | `ts TIMESTAMPTZ, symbol_code TEXT, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume BIGINT, PRIMARY KEY(ts, symbol_code)` |

Locked to NQ, 6E, CL, ZN only. Updated every 1h via Databento Historical API `ohlcv-1h` pull — NOT live streaming. Correlations row does NOT change with chart TF switching (always 1h, isolated).

### Group 4 — FRED/Economic Data (11 tables)

**Populated by:** Phase 6 (FRED API ingestion scripts)
**Dashboard surface:** AI Analysis card context

| Table | Schema |
|---|---|
| `series_catalog` | `series_id TEXT PRIMARY KEY, name TEXT, category TEXT, frequency TEXT, is_active BOOLEAN` |
| `econ_rates_1d` | `ts TIMESTAMPTZ, series_id TEXT, value DOUBLE, PRIMARY KEY(ts, series_id)` |
| `econ_yields_1d` | same as `econ_rates_1d` |
| `econ_fx_1d` | same as `econ_rates_1d` |
| `econ_vol_1d` | same as `econ_rates_1d` |
| `econ_inflation_1d` | same as `econ_rates_1d` |
| `econ_labor_1d` | same as `econ_rates_1d` |
| `econ_activity_1d` | same as `econ_rates_1d` |
| `econ_money_1d` | same as `econ_rates_1d` |
| `econ_commodities_1d` | same as `econ_rates_1d` |
| `econ_indexes_1d` | same as `econ_rates_1d` |

Seed `series_catalog` with the 40+ active FRED series from `supabase/seed.sql` (FEDFUNDS, DFF, SOFR, DGS2/5/10/30, T10Y2Y, T10Y3M, DTWEXBGS, DEXUSEU, DEXJPUS, VIXCLS, OVXCLS, CPIAUCSL, CPILFESL, etc.)

### Group 5 — News & Events (8 tables)

**Populated by:** Phase 6 (news ingestion scripts — FinancialData.net 1-min, Finnhub 15-min, Newsfilter 15-min, Google Finance)
**Dashboard surface:** AI Analysis card news context

| Table | Schema |
|---|---|
| `econ_news_topics` | `topic_code TEXT PRIMARY KEY, topic_label TEXT, topic_family TEXT, econ_category TEXT, topic_tags TEXT[], description TEXT, is_active BOOLEAN` |
| `news_articles` | `id INTEGER PRIMARY KEY, provider TEXT, article_key TEXT UNIQUE, title TEXT, summary TEXT, url TEXT, publisher_domain TEXT, published_at TIMESTAMPTZ, published_minute TIMESTAMPTZ, normalized_title TEXT, dedupe_key TEXT UNIQUE, body_word_count INTEGER DEFAULT 0, related_symbols TEXT[], topic_codes TEXT[], benchmark_fit_score DOUBLE, fetched_at TIMESTAMPTZ DEFAULT now()` |
| `news_article_segments` | `id INTEGER PRIMARY KEY, article_id INTEGER REFERENCES news_articles(id), segment TEXT, matched_keywords TEXT[], matched_symbols TEXT[]` |
| `news_article_assessments` | `id INTEGER PRIMARY KEY, provider TEXT, dedupe_key TEXT, article_key TEXT, topic_code TEXT, source_quality_score DOUBLE, market_relevance_score DOUBLE, macro_specificity_score DOUBLE, technical_specificity_score DOUBLE, cross_asset_context_score DOUBLE, watchlist_relevance_score DOUBLE, reasoning_confidence DOUBLE, benchmark_fit_score DOUBLE, scoring_version TEXT DEFAULT 'reuters_benchmark_v1', scored_at TIMESTAMPTZ DEFAULT now()` |
| `econ_calendar` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, event_name TEXT, actual DOUBLE, forecast DOUBLE, previous DOUBLE, impact TEXT, currency TEXT` |
| `news_signals` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, signal_type TEXT, direction TEXT, confidence DOUBLE, source_headline TEXT` |
| `geopolitical_risk_1d` | `ts TIMESTAMPTZ PRIMARY KEY, gpr_daily DOUBLE, gpr_threats DOUBLE, gpr_acts DOUBLE, country TEXT` |
| `trump_effect_1d` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, event_type TEXT, title TEXT, summary TEXT, market_impact TEXT, sector TEXT, source TEXT, source_url TEXT` |

Seed `econ_news_topics` with the 11 S&P-focused topics from `config/news_raw_contract.json`. Use the existing scoring contract (`reuters_benchmark_v1` weights, trusted/blocked/premier domain lists) for article assessment.

### News Sources

| Source | Frequency | API Key | Cost |
|---|---|---|---|
| FinancialData.net | 1-min polling | `8cd0dd568c735d919df2d861b936c2d9` (free tier, expires 2026-06-27) | Free |
| Google Finance News | 1-5 min (Kirk's watchlist at `.INX:INDEXSP`) | Kirk's Google account | Free |
| Finnhub | 15-min polling | Existing key (in Supabase vault, migrate to `.env`) | Free tier |
| Newsfilter | 15-min polling | Existing key (in Supabase vault, migrate to `.env`) | Free tier |

All news API keys stored in `.env` (NOT committed — add to `.gitignore`). FinancialData.net is a new provider not currently in the codebase.

### Group 6 — Trade Log (3 tables)

**Populated by:** Phase 1 (cherry-pick `engine/trade_log.py` from PR #11)
**Dashboard surface:** Trade recording, pattern learning, Win Rate card (if real data exists)

| Table | Schema |
|---|---|
| `trades` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, symbol TEXT DEFAULT 'MES', direction TEXT, entry_price DOUBLE, stop_loss DOUBLE, tp1 DOUBLE, tp2 DOUBLE, exit_price DOUBLE, exit_reason TEXT, pnl DOUBLE, status TEXT` |
| `trade_tags` | `id INTEGER PRIMARY KEY, trade_id INTEGER REFERENCES trades(id), tag TEXT` |
| `indicator_state` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, timeframe TEXT, state_json TEXT` |

Note: `engine/trade_log.py` from PR #11 has a PnL bug for SHORT trades (Devin Review finding). Fix during Phase 1 cherry-pick.

### Group 7 — Symbols Registry (1 table)

**Populated by:** Phase 1 (seeded from `supabase/seed.sql` active symbols)
**Dashboard surface:** Reference table for all symbol lookups

| Table | Schema |
|---|---|
| `symbols` | `code TEXT PRIMARY KEY, display_name TEXT, short_name TEXT, description TEXT, tick_size DOUBLE, data_source TEXT, dataset TEXT, databento_symbol TEXT, is_active BOOLEAN` |

Seed with 17 active Databento futures + 3 active FRED symbols. Do NOT seed inactive symbols. The `is_active` flag is the billing guardrail.

### Group 8 — Volatility State (1 table)

**Populated by:** Phase 6 (computed from econ data)
**Dashboard surface:** AI Analysis risk context, `warbird_risk` GARCH input

| Table | Schema |
|---|---|
| `vol_states` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, state_name TEXT, regime_label TEXT, days_into_regime INTEGER, vix_level DOUBLE, vix_percentile_20d DOUBLE` |

### Group 9 — Warbird Signal Chain (8 tables)

**Populated by:** Phase 3-4 (engine computes locally, persists for AI to read)
**Dashboard surface:** AI Analysis card reads latest state; signal chain drives GO/WAIT/NO_GO

| Table | Schema |
|---|---|
| `warbird_daily_bias` | `ts TIMESTAMPTZ PRIMARY KEY, symbol_code TEXT DEFAULT 'MES', bias TEXT CHECK(bias IN ('BULL','BEAR','NEUTRAL')), close_price DOUBLE, ma_200 DOUBLE, price_vs_200d_ma DOUBLE, distance_pct DOUBLE, slope_200d_ma DOUBLE, sessions_on_side INTEGER, daily_return DOUBLE, daily_range_vs_avg DOUBLE` |
| `warbird_structure_4h` | `ts TIMESTAMPTZ PRIMARY KEY, symbol_code TEXT DEFAULT 'MES', bias_4h TEXT CHECK(bias_4h IN ('BULL','BEAR','NEUTRAL')), agrees_with_daily BOOLEAN DEFAULT FALSE, trend_score DOUBLE, swing_high DOUBLE, swing_low DOUBLE, structural_note TEXT` |
| `warbird_forecasts_1h` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, symbol_code TEXT DEFAULT 'MES', bias_1h TEXT, target_price_1h DOUBLE, target_price_4h DOUBLE, confidence DOUBLE, current_price DOUBLE, model_version TEXT, feature_snapshot TEXT` |
| `warbird_triggers_15m` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, forecast_id INTEGER, symbol_code TEXT DEFAULT 'MES', direction TEXT, decision TEXT CHECK(decision IN ('GO','WAIT','NO_GO')), fib_level DOUBLE, entry_price DOUBLE, stop_loss DOUBLE, tp1 DOUBLE, tp2 DOUBLE, volume_confirmation BOOLEAN DEFAULT FALSE, volume_ratio DOUBLE, no_trade_reason TEXT` |
| `warbird_conviction` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, forecast_id INTEGER, trigger_id INTEGER, symbol_code TEXT DEFAULT 'MES', level TEXT CHECK(level IN ('MAXIMUM','HIGH','MODERATE','LOW','NO_TRADE')), counter_trend BOOLEAN DEFAULT FALSE, all_layers_agree BOOLEAN DEFAULT FALSE, runner_eligible BOOLEAN DEFAULT FALSE, daily_bias TEXT, bias_4h TEXT, bias_1h TEXT, trigger_decision TEXT` |
| `warbird_setups` | `id INTEGER PRIMARY KEY, setup_key TEXT UNIQUE, ts TIMESTAMPTZ, symbol_code TEXT DEFAULT 'MES', forecast_id INTEGER, trigger_id INTEGER, conviction_id INTEGER, direction TEXT, status TEXT CHECK(status IN ('ACTIVE','TP1_HIT','TP2_HIT','RUNNER_ACTIVE','RUNNER_EXITED','STOPPED','EXPIRED')), conviction_level TEXT, entry_price DOUBLE, stop_loss DOUBLE, tp1 DOUBLE, tp2 DOUBLE, volume_confirmation BOOLEAN DEFAULT FALSE, trigger_bar_ts TIMESTAMPTZ, tp1_hit_at TIMESTAMPTZ, tp2_hit_at TIMESTAMPTZ, stopped_at TIMESTAMPTZ, expires_at TIMESTAMPTZ, notes TEXT` |
| `warbird_setup_events` | `id INTEGER PRIMARY KEY, setup_id INTEGER, ts TIMESTAMPTZ, event_type TEXT CHECK(event_type IN ('TRIGGERED','TP1_HIT','TP2_HIT','RUNNER_STARTED','RUNNER_EXITED','STOPPED','EXPIRED')), price DOUBLE, note TEXT, metadata TEXT` |
| `warbird_risk` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, forecast_id INTEGER, symbol_code TEXT DEFAULT 'MES', garch_sigma DOUBLE, garch_vol_ratio DOUBLE, zone_1_upper DOUBLE, zone_1_lower DOUBLE, zone_2_upper DOUBLE, zone_2_lower DOUBLE, gpr_level DOUBLE, trump_effect_active BOOLEAN, vix_level DOUBLE, vix_percentile_20d DOUBLE, vol_state_name TEXT, regime_label TEXT DEFAULT 'trump_2', days_into_regime INTEGER` |

These were previously incorrectly listed as "skip — Vercel cron output." The local engine computes them, but the AI analysis card needs to READ the latest persisted state. The full signal chain flows: daily bias → structure 4H → forecast → trigger → conviction → setup → risk → AI analysis.

### Group 10 — AI Analysis Output (1 table)

**Populated by:** Phase 6 (Gemini analysis runs on each bar close while dashboard is open)
**Dashboard surface:** AI Analysis card audit trail

| Table | Schema |
|---|---|
| `ai_analysis_log` | `id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, model TEXT, analysis_text TEXT, data_sources_used TEXT, screenshot_available BOOLEAN DEFAULT FALSE` |

Screenshot ingestion is PLANNED but unverified per SKILL.md. Do not claim until pipeline exists.

### Tables NOT Needed in DuckDB

| Supabase Table | Reason |
|---|---|
| `warbird_forecasts_1h` (Supabase version) | Replaced by local engine computation → DuckDB Group 9 |
| `options_stats_1d` | Not in SKILL.md dashboard scope |
| `options_ohlcv_1d` | Not in SKILL.md dashboard scope |
| `cross_asset_1d` | Dashboard only needs 1h for correlations |

---

## 5. Databento Subscription Guardrails

**Subscription:** Standard $179/mo CME (GLBX.MDP3)
**Confirmed free:** `ohlcv-1m` on Standard plan (per `lib/ingestion/databento.ts` line 3)
**Cost-gated:** Historical API beyond free monthly budget; trades schema (verify live streaming inclusion)

### Hard Rules

1. **NEVER query inactive symbols.** Only `is_active = true` from the `symbols` table. Kirk got a massive bill from inactive ones (`supabase/seed.sql` line 3). The engine's `DATABENTO_APPROVED_SYMBOLS` allowlist is the enforcement mechanism.

2. **NEVER pull historical data that already exists locally.** Phase 1 seeds DuckDB from local batch files on disk — zero API cost:
   - `data/MES 1m 2010 GLBX-20260503-N6U6W7EDKU.zip` (ohlcv-1m, 2010→2026)
   - `data/MES 1m 2019 2026 GLBX-20260503-J9H7XNXFBT.zip` (ohlcv-1m, 2019→2026)
   - `Historical Data/Databento/raw/databento_futures_ohlcv_1h.parquet` (cross-asset 1h, 2010→2025)
   - `data/MES ES Trades GLBX-20260508-SAGMRP8P3H.zip` (trades, 2025-05→2026-05)

3. **Historical API is gap-fill only.** On dashboard open, calculate gap since last DuckDB bar and only request the delta. If gap < 6h, auto-pull. If gap > 6h < 24h, pull with cost warning logged. If gap > 24h, refuse and warn Kirk. If gap > 7 days, refuse entirely — requires Kirk approval to backfill.

4. **Correlations use Databento Historical API `ohlcv-1h` pulls — not live streaming.** Every 1 hour while the dashboard is open, pull the latest 1h bar for NQ.c.0, 6E.c.0, CL.c.0, ZN.c.0 via Historical API `get_range`. This is 4 bars per hour — minimal cost. Do NOT subscribe to live `ohlcv-1m` for correlation symbols and aggregate locally.

5. **`trades` schema is cost-gated.** Two paths:
   - **Path A (default):** Use the 1-year local trades download for historical pressure bar + seed DuckDB. Live pressure uses `ohlcv-1m` total volume only (no A/B/N side classification). AT-2 and AT-3 tested against historical data only.
   - **Path B (Kirk approval required):** If Kirk confirms trades live streaming is included in the $179/mo subscription, subscribe to `trades` schema for MES.v.0 alongside `ohlcv-1m`. Full A/B/N side classification, real delta, AT-2 and AT-3 pass on live data.

6. **Engine config allowlist.** Phase 1 produces `engine/config.py` with:

```python
DATABENTO_APPROVED_SCHEMAS = {"ohlcv-1m", "ohlcv-1h"}  # trades added after Kirk confirms
DATABENTO_APPROVED_SYMBOLS = {
    "MES.v.0",   # Primary chart instrument (continuous front-month)
    "NQ.c.0",    # Correlations
    "6E.c.0",    # Correlations
    "CL.c.0",    # Correlations
    "ZN.c.0",    # Correlations
}
DATABENTO_DATASET = "GLBX.MDP3"
```

Every Databento API call must validate against these allowlists. No exceptions.

7. **Subscription-only data.** NOTHING gets pulled from Databento that is not covered by the Standard $179/mo CME subscription. Any addition to the allowlists requires Kirk approval.

8. **Front-month contract roll.** `active_mes_contract()` in `scripts/live-feed.py` auto-detects front-month MES symbol (CME roll schedule: 8 days before 3rd Friday of quarterly month). The engine must use this same logic.

---

## 6. Engine Lifecycle — On-Demand Architecture

The engine is demand-driven. Everything spins up when the dashboard is opened and tears down when it is closed. No persistent background daemon.

### States

| State | Description | Resource Usage |
|---|---|---|
| **COLD** | FastAPI server listening on :3100. No Databento connection, no computation, no polling. | Near-zero CPU/memory |
| **WARMING** | First WebSocket client connected. Loading historical bars from DuckDB, opening Databento Live subscription, starting computation engines, pulling gap-fill if needed. | Moderate (startup burst) |
| **WARM** | Fully live. Databento streaming, all engines computing per-bar, WebSocket pushing updates. | Active CPU/memory proportional to TF cadence |
| **COOLDOWN** | Last WebSocket client disconnected. 60-second grace period before teardown (in case of accidental tab close / immediate reopen). | Same as WARM during grace period |

### Lifecycle Sequence

```
Dashboard opened (browser navigates to localhost:3100)
  → Browser loads static HTML/JS/CSS from FastAPI
  → Browser opens WebSocket to FastAPI
  → Server detects first client → transition COLD → WARMING
  → Load historical bars from DuckDB → chart renders immediately
  → Calculate gap since last DuckDB bar timestamp
    → If gap < 6h: Historical API gap-fill (auto)
    → If gap > 6h: warn, apply cost cap rules
  → Open Databento Live subscription (ohlcv-1m for MES.v.0, FREE)
  → Start bar aggregation (1m → 3m/5m/15m/1h/4h/1d)
  → Start fib/MA/pressure/nexus/trigger compute engines
  → Start news polling (FinancialData.net 1-min, Finnhub/Newsfilter 15-min)
  → Start correlations 1h timer (Databento Historical API ohlcv-1h pull)
  → Start AI analysis on bar-close events (Gemini)
  → Transition WARMING → WARM
  → Push initial_state message to client
  → Per-bar: compute all TF-coupled surfaces → push bar_update via WebSocket

Dashboard closed (browser tab closed)
  → WebSocket disconnects
  → Server detects zero clients → transition WARM → COOLDOWN
  → 60-second grace period
  → If no reconnect within 60s: transition COOLDOWN → COLD
    → Close Databento Live subscription
    → Cancel all compute loops, news polling, correlations timer
    → Flush pending state to DuckDB
    → Release memory
  → If reconnect within 60s: transition COOLDOWN → WARM (no restart needed)
```

### Initial State on Connect

When a client connects, the server pushes an `initial_state` message:

```json
{
  "type": "initial_state",
  "status": "warming_up",
  "historical_bars": { "5m": ["...from DuckDB..."] },
  "last_known_fibs": {},
  "last_known_cards": {},
  "last_known_pressure": {},
  "last_known_nexus": {},
  "live_eta_seconds": 5
}
```

When the engine is fully warm:

```json
{
  "type": "engine_status",
  "status": "live",
  "databento_connected": true,
  "news_polling_active": true,
  "correlations_timer_active": true,
  "current_tf": "5m",
  "last_bar_ts": "2026-05-29T14:35:00Z"
}
```

---

## 7. Real-Time Update Architecture — TF-Coupled Full-State Recompute

This is an ultra-fast trading dashboard. 5m canonical TF with 1m/3m/5m/15m chart TFs. When the TF changes, EVERYTHING except correlations recomputes.

### TF-Coupled Surfaces

| Surface | TF-Coupled? | Recompute Trigger |
|---|---|---|
| Chart (candlesticks) | YES | Every bar close at current TF |
| Fibs (bounded anchored lines) | YES | Every bar close — lookback windows (8/13/21/34/55 bars) are relative to current TF |
| MAs (EMA21, EMA9, SMA200) | YES | Every bar close at current TF |
| Pressure bar (thin slim, blue-to-red) | YES | Every bar close — trades-side delta aggregated at current TF's bar boundaries |
| Nexus ML RSI (sub-chart) | YES | Every bar close — AMF oscillator recomputes on current TF's bars |
| Trigger engine (GO/WAIT/NO_GO) | YES | Every bar close — zone proximity, rejection wick, engulfing use current TF candles |
| Cards panel (Entry Signal, Price, SL, TP1, TP2, AI, Win Rate) | YES | Every bar close at current TF |
| Correlations row (NQ/6E/CL/ZN) | **NO** | Always 1h, isolated timer. NEVER changes with chart TF. |

### WebSocket Message Contract

**Per-bar update** (sent every bar close at current TF):

```json
{
  "type": "bar_update",
  "timeframe": "5m",
  "bar": { "ts": "...", "open": 0, "high": 0, "low": 0, "close": 0, "volume": 0 },
  "fibs": { "levels": [], "draw_left_bar": "...", "draw_right_bar": "..." },
  "mas": { "ema21": 0, "ema9": 0, "sma200": 0 },
  "pressure": { "value": 0, "color": "#...", "components": {} },
  "nexus": { "rsi": 0, "amf": 0 },
  "trigger": { "decision": "GO|WAIT|NO_GO", "entry": 0, "sl": 0, "tp1": 0, "tp2": 0 },
  "cards": { "entry_signal": "...", "entry_price": 0, "sl": 0, "tp1": 0, "tp2": 0, "confidence": "HIGH|LOW" },
  "volume": { "buy_vol": 0, "sell_vol": 0, "unknown_vol": 0, "delta": 0, "confidence": "HIGH|LOW" }
}
```

**TF switch** (sent when user changes chart timeframe):

```json
{
  "type": "tf_switch",
  "new_tf": "1m",
  "full_state": {
    "bars": ["...all bars for new TF from DuckDB..."],
    "fibs": {},
    "mas": {},
    "pressure": {},
    "nexus": {},
    "trigger": {},
    "cards": {}
  }
}
```

**Correlations update** (sent every 1h, independent of chart TF):

```json
{
  "type": "correlations_update",
  "symbols": {
    "NQ": { "ts": "...", "open": 0, "high": 0, "low": 0, "close": 0, "change_pct": 0 },
    "6E": {},
    "CL": {},
    "ZN": {}
  }
}
```

### Per-Bar Pipeline

On 1m TF, this runs every 60 seconds. On 5m, every 300 seconds.

```
Databento 1m bar arrives
  → bar_store aggregates to current TF bucket
  → IF current TF bucket closes:
    → Write bar to DuckDB
    → Fib engine recomputes (lookbacks relative to current TF)
    → MA engine recomputes (EMA21, EMA9, SMA200 on current TF bars)
    → Pressure recomputes (trades-side delta at current TF boundaries)
    → Nexus recomputes (AMF oscillator on current TF bars)
    → Trigger engine evaluates (GO/WAIT/NO_GO on current TF candles)
    → Cards update
    → Serialize full state → WebSocket push → LWC re-renders ALL surfaces
```

---

## 8. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL MACHINE                                 │
│                                                                  │
│  ┌──────────────┐     ┌──────────────────────┐                  │
│  │ Databento     │     │ engine/               │                 │
│  │ Live API      │────▶│ databento_feed.py     │                 │
│  │ (ohlcv-1m,    │     │ bar_store.py          │                 │
│  │  trades*)     │     │ fib_engine.py         │                 │
│  └──────────────┘     │ trigger_engine.py     │                 │
│                        │ pressure.py           │                 │
│  ┌──────────────┐     │ nexus.py              │                 │
│  │ Databento     │     │ ai_analysis.py        │                 │
│  │ Historical    │────▶│ server.py (FastAPI)   │                 │
│  │ (ohlcv-1h     │     └──────────┬───────────┘                 │
│  │  correlations)│                │                              │
│  └──────────────┘                │ WebSocket                    │
│                                   ▼                              │
│  ┌──────────────┐     ┌──────────────────────┐                  │
│  │ DuckDB        │◀───│ dashboard/            │                  │
│  │ data/warbird  │     │ index.html            │                 │
│  │ _trades.duckdb│     │ (LWC v5, plain HTML/  │                 │
│  └──────────────┘     │  JS/CSS, no React)    │                 │
│                        └──────────────────────┘                  │
│  ┌──────────────┐                                               │
│  │ News APIs     │     (FinancialData.net 1-min,                │
│  │ FRED API      │      Finnhub/Newsfilter 15-min,              │
│  │ Google Finance│      FRED daily)                              │
│  └──────────────┘                                               │
│                                                                  │
│  NO Supabase in the local dashboard data path.                  │
│  NO Next.js / Vercel in the local dashboard.                    │
│  Vercel dashboard continues using Supabase until Phase 9.       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Phase Sequence

### Phase 0: Plan Acceptance (THIS PHASE)

- **Entry criteria:** This plan exists as an artifact
- **Allowed files:** `docs/plans/` only
- **Forbidden files:** Everything else
- **Expected artifacts:** This plan file
- **Verification:** `test -f docs/plans/2026-05-29-warbird-chart-parity-final-plan.md`
- **Codex QA gate:** Kirk and Codex QA review this plan
- **Stop condition:** Kirk rejects the plan or requests changes
- **Approval required:** Kirk accepts the plan before Phase 1 begins

### Phase 1: DuckDB Init + Chart Scaffold + Engine Cherry-Pick

- **Entry criteria:** Phase 0 accepted by Kirk
- **Allowed files:** `engine/fib_engine.py`, `engine/trade_log.py`, `engine/init_db.py` (new), `engine/seed_duckdb.py` (new), `engine/config.py` (new), `dashboard/index.html` (new), `dashboard/chart.js` (new), `dashboard/style.css` (new), `data/`, `.gitignore`
- **Forbidden files:** `indicators/`, Pine, Supabase, Vercel config
- **Tasks:**
  1. Cherry-pick `engine/fib_engine.py` from PR #11 to main — byte-identical copy, verify with `git diff`
  2. Cherry-pick `engine/trade_log.py` from PR #11 — fix PnL bug for SHORT trades
  3. Create `engine/init_db.py` — initializes ALL DuckDB tables (Groups 1-10, ~35 tables) at `data/warbird_trades.duckdb` on first use
  4. Create `engine/seed_duckdb.py` — reads local batch files (`.zip`, `.parquet`) and populates DuckDB bar tables, `trades_raw`, `cross_asset_1h`, `symbols`. Zero Databento API cost.
  5. Create `engine/config.py` — Databento allowlists, engine lifecycle config, API key references
  6. Create `data/` directory, add `data/*.duckdb` and `data/*.zip` to `.gitignore`
  7. Port exact `LiveMesChart.tsx` chart settings into `dashboard/index.html` + `dashboard/chart.js`: theme, bar spacing, rightOffset, watermark, crosshair, candle colors. Strip V16FibLinesPrimitive + autofib-v16.
  8. Create basic `dashboard/style.css` with locked layout skeleton
  9. Seed `symbols` table with 17 active Databento + 3 active FRED from `supabase/seed.sql`
- **Expected artifacts:** `engine/fib_engine.py`, `engine/trade_log.py`, `engine/init_db.py`, `engine/seed_duckdb.py`, `engine/config.py`, `dashboard/index.html`, `dashboard/chart.js`, `dashboard/style.css`, `data/` directory, Phase 1 closeout packet, schema inventory
- **Verification:** `python engine/init_db.py` creates DuckDB with all tables; `python engine/seed_duckdb.py` populates bars from local files; `git diff --check`
- **Codex QA gate:** Verify fib engine is byte-identical to PR #11 version; verify DuckDB schema matches this plan's inventory
- **Stop condition:** Fib engine differs from PR #11; DuckDB init fails; seed script errors
- **Approval required:** Kirk accepts Phase 1 closeout

### Phase 1.5: Local Data Pipeline + Engine Lifecycle

- **Entry criteria:** Phase 1 closeout accepted; Kirk confirms Databento subscription includes required schemas; Databento API key provisioned in `.env`
- **Allowed files:** `engine/databento_feed.py`, `engine/bar_store.py`, `engine/server.py`, `engine/lifecycle.py` (new), `dashboard/` files
- **Forbidden files:** `indicators/`, Pine, Supabase
- **Tasks:**
  1. Cherry-pick `engine/databento_feed.py` from PR #11 — add client-presence lifecycle (connect on WARMING, disconnect on COLD)
  2. Cherry-pick `engine/bar_store.py` from PR #11 — fix thread-safety issues; verify multi-TF aggregation (1m → 3m/5m/15m/1h/4h/1d)
  3. Cherry-pick `engine/server.py` from PR #11 — add WebSocket client-presence tracking, COLD/WARMING/WARM/COOLDOWN state machine, 60-second cooldown grace period
  4. Create `engine/lifecycle.py` — centralized lifecycle manager: start/stop Databento, compute engines, news polling, correlations timer based on client count
  5. Wire Databento Live (`ohlcv-1m`) → `bar_store` → DuckDB bar tables + WebSocket push
  6. Wire chart: LWC receives data via `series.setData()` for initial load (from DuckDB) and `series.update()` for live ticks (from WebSocket)
  7. Implement Historical API gap-fill with cost cap rules (< 6h auto, > 6h warn, > 24h refuse)
  8. Implement Databento Live → Historical API fallback with auto-reconnect (exponential backoff, 3 attempts)
  9. Implement front-month contract roll detection using `active_mes_contract()` logic
  10. Implement bar validation: price > 0, high >= low, not weekend
- **Expected artifacts:** Working Databento → DuckDB → WebSocket → LWC pipeline; engine lifecycle state machine; Phase 1.5 closeout packet
- **Verification:** Open dashboard → chart renders from DuckDB → live bars start flowing → close dashboard → engine goes COLD → reopen → engine resumes; `pytest tests/engine/` (bar aggregation); no Supabase imports in local dashboard data path
- **Codex QA gate:** Verify zero Supabase references in engine/dashboard; verify lifecycle transitions
- **Stop condition:** Databento connection fails; bars don't render; lifecycle doesn't tear down
- **Approval required:** Kirk accepts Phase 1.5 closeout

### Phase 2: Indicator Transfer (Fibs + MAs)

- **Entry criteria:** Phase 1.5 closeout accepted; chart renders live bars
- **Allowed files:** `dashboard/` (fib rendering, MA overlay), `engine/` (fib/MA integration)
- **Forbidden files:** `indicators/`, Pine, `engine/fib_engine.py` (no modifications)
- **Tasks:**
  1. Port ALL fib visuals from `indicators/warbird-pro-v9.pine` (lines 68-70, 226-261, 805-870): colors, widths, styles, ladder, zone fill, labels
  2. Implement BOUNDED anchored fib draw: `x1=drawLeftBar`, `x2=rightBar`, `extend.none`. No horizon lines.
  3. 13 visible levels, -.236 hidden (same as indicator, `warbird-pro-v9.pine:837 visible=false`)
  4. Golden zone fill between .382-.618
  5. Fib colors: .382/.618 = RED `#cc0000` solid w2; pivot (.500) = white dashed; 1.000 = white dotted; targets (1.236, 1.618, 2.000, 2.236) = teal `#0097A7`
  6. Port EMA21 + EMA9 smoothing from indicator — exact settings, no duplicate EMA21
  7. Add 200 SMA (white, 2pt thick) — the ONLY MA addition
  8. Fib engine lookback windows (8/13/21/34/55 bars) must be relative to current TF's bars. TF switch triggers full fib recompute.
- **Expected artifacts:** Fib rendering code, MA overlay code, AT-1 evidence (bounded fib draw parity), Phase 2 closeout
- **Verification:** Browser screenshot comparing indicator fibs vs dashboard fibs; AT-1 passes at all 4 TFs (1m, 3m, 5m, 15m)
- **Codex QA gate:** Verify fib count = 13 visible; verify bounded draw (no horizon lines); verify no fib engine modifications
- **Stop condition:** AT-1 fails at any TF; fib engine was modified; horizon lines detected
- **Approval required:** Kirk accepts AT-1 evidence

### Phase 3: Layout + Cards + TF Switching

- **Entry criteria:** Phase 2 closeout accepted; fibs and MAs render correctly
- **Allowed files:** `dashboard/` (layout, cards panel, TF switching UI)
- **Forbidden files:** `indicators/`, Pine
- **Tasks:**
  1. Implement locked layout from SKILL.md:
     - Correlations row: FULL WIDTH, above everything
     - Chart + Cards panel: 2-column grid, cards sidebar (320px) WITHIN chart row ONLY
     - Pressure bar: FULL WIDTH below BOTH chart and cards, THIN SLIM blue-to-red gradient, zero padding
     - Nexus: FULL WIDTH below pressure bar
     - Cards panel does NOT extend past chart canvas
  2. Implement cards panel: Entry Signal (GO/WAIT/NO_GO), Entry Price, SL, TP1, TP2, AI Analysis (placeholder until Phase 6), Win Rate (only if real data exists)
  3. NO Fib Structure card. NO System card. NO Volume Intelligence card. NO Conviction card.
  4. Implement TF switching UI: buttons for 1m/3m/5m/15m, 5m default
  5. TF switch triggers FULL STATE RECOMPUTE: fibs, MAs, pressure, nexus, trigger, cards — not just chart re-render
  6. Cards update on EVERY bar close at current TF
  7. Font: Inter for chart, JetBrains Mono for data
- **Expected artifacts:** Layout code matching SKILL.md diagram, cards panel, TF switching, Phase 3 closeout, screenshot proof
- **Verification:** Browser screenshot matching SKILL.md ASCII layout; TF switch smoke test (5m→1m, verify all surfaces update)
- **Codex QA gate:** Verify layout matches SKILL.md diagram exactly; verify no wrong cards; verify TF switch cascades to all surfaces
- **Stop condition:** Layout drifts from SKILL.md; wrong cards appear; TF switch doesn't cascade
- **Approval required:** Kirk accepts layout screenshot

### Phase 4: Trades-Side Volume + Pressure Bar + Confidence Gate

- **Entry criteria:** Phase 3 closeout accepted; layout locked
- **Allowed files:** `engine/databento_feed.py` (add trades schema), `engine/pressure.py`, `engine/trigger_engine.py`, `engine/indicators.py`, `dashboard/` (pressure bar rendering)
- **Forbidden files:** `indicators/`, Pine
- **Tasks:**
  1. Add `trades` schema path to `engine/databento_feed.py` (if Kirk approves Path B — live trades). Otherwise use local historical trades data for development/testing.
  2. Aggregate trades by side field: B=buy, A=sell, N=unknown → per-bar buckets at current TF
  3. Compute real trades-side delta: `delta = buy_vol - sell_vol`
  4. Replace candle-body proxy at `engine/indicators.py:438-447` with real delta
  5. Implement confidence gate: `unknown_vol / total_vol > 0.30 → LOW`
  6. In `engine/trigger_engine.py`: if `confidence == "LOW" and decision == "GO"` → force `decision = "WAIT"`
  7. Render pressure bar: THIN SLIM full-width, blue-to-red gradient, zero padding. NOT a full indicator row.
  8. Pressure bar weights: volume delta (30%), RSI (25%), momentum (20%), TTM squeeze (25%)
  9. Pressure bar recomputes at current TF's bar boundaries (TF-coupled)
  10. Write unit test: LOW-confidence + high-score → WAIT (never GO)
- **Expected artifacts:** Pressure bar code, confidence gate code, AT-2 evidence, AT-3 evidence, Phase 4 closeout
- **Verification:** AT-2 passes (pressure from trades A/B/N) at all 4 TFs; AT-3 passes (LOW→WAIT) at all 4 TFs; `pytest tests/engine/`
- **Codex QA gate:** Verify no candle-body proxy remains; verify LOW→WAIT gate; verify pressure bar is thin/slim
- **Stop condition:** AT-2 or AT-3 fails; pressure bar is bulky; candle proxy still used
- **Approval required:** Kirk accepts AT-2 and AT-3 evidence

### Phase 5: Correlations Row + Nexus

- **Entry criteria:** Phase 4 closeout accepted
- **Allowed files:** `engine/nexus.py`, `engine/correlations.py` (new), `dashboard/` (correlations row, nexus sub-chart)
- **Forbidden files:** `indicators/`, Pine
- **Tasks:**
  1. Implement correlations row: 4 Databento futures (NQ.c.0, 6E.c.0, CL.c.0, ZN.c.0)
  2. Correlations update via Databento Historical API `ohlcv-1h` pull every 1 hour — NOT live streaming, NOT mixed with chart TF
  3. Correlations row renders FULL WIDTH above everything
  4. Correlations row does NOT change with chart TF switching (always 1h, isolated)
  5. Port Nexus ML RSI (AMF oscillator) from `engine/nexus.py` / Pine v1.2.6
  6. Nexus renders as FULL WIDTH sub-chart below pressure bar
  7. Nexus IS TF-coupled — recomputes on current TF's bars when TF switches
  8. Only poll correlations while dashboard is open (on-demand lifecycle)
- **Expected artifacts:** Correlations row code, Nexus sub-chart code, Phase 5 closeout, screenshot proof
- **Verification:** Correlations show 4 symbols updating every 1h; Nexus renders below pressure bar; TF switch recomputes Nexus but NOT correlations
- **Codex QA gate:** Verify correlations timing is 1h only; verify correlations don't change with TF; verify Nexus is TF-coupled
- **Stop condition:** Correlations use wrong timing; Nexus doesn't recompute on TF switch
- **Approval required:** Kirk accepts correlations + Nexus screenshot

### Phase 6: AI Analysis + News Ingestion + Economic Data

- **Entry criteria:** Phase 5 closeout accepted; Gemini API key provisioned; FinancialData.net API key provisioned; Finnhub + Newsfilter keys migrated from Supabase vault to `.env`
- **Allowed files:** `engine/ai_analysis.py`, `engine/news_poller.py` (new), `engine/econ_ingestion.py` (new), `dashboard/` (AI card rendering)
- **Forbidden files:** `indicators/`, Pine
- **Tasks:**
  1. Switch `engine/ai_analysis.py` from OpenRouter to Gemini
  2. Gemini analyzes: real-time structure/volume/correlations/nexus/pressure bar data + latest news + economic context
  3. AI output: short, high impact, dense, credible. Not verbose.
  4. Chart screenshot ingestion: PLANNED but unverified. Do not claim until pipeline exists.
  5. Create `engine/news_poller.py`: polls FinancialData.net (1-min), Finnhub (15-min), Newsfilter (15-min). Google Finance method TBD (RSS/scraping — requires Kirk input on method).
  6. News poller only runs while dashboard is open (on-demand lifecycle)
  7. On startup, news poller does immediate catch-up pull before starting regular cycle
  8. Write articles to `news_articles` table with deduplication via `dedupe_key`
  9. Score articles using `reuters_benchmark_v1` weights from `config/news_raw_contract.json`
  10. Create `engine/econ_ingestion.py`: pulls FRED data daily, writes to 10 econ domain tables
  11. Port GPR, Trump Effect ingestion from existing `scripts/backfill-gpr.py` pattern
  12. Populate `warbird_daily_bias` and signal chain tables (Group 9) from engine computation
  13. AI card displays latest analysis with recency indicator ("last update: Xm ago")
  14. AI fires on bar-close events only (not continuously), only while dashboard is open
  15. Also covers: S&P news, Fed reports, Mag 7 industry news/releases/financials/IPOs
- **Expected artifacts:** AI analysis code (Gemini), news poller code, econ ingestion code, Phase 6 closeout, schema inventory
- **Verification:** AI card renders with real Gemini output; news articles flow into DuckDB; FRED data populates econ tables; `pytest tests/engine/`
- **Codex QA gate:** Verify Gemini (not OpenRouter); verify news deduplication; verify no fake claims about screenshot analysis
- **Stop condition:** Gemini API errors; news poller crashes; AI output is verbose/uncredible
- **Approval required:** Kirk accepts AI card output quality

### Phase 7: Acceptance Tests + Integration QA

- **Entry criteria:** Phase 6 closeout accepted; all surfaces rendering
- **Allowed files:** `tests/`, `docs/evidence/`
- **Forbidden files:** `indicators/`, Pine
- **Tasks:**
  1. **AT-1:** Bounded fib draw window parity — fib computation uses `engine/fib_engine.py` ONLY, 13 visible levels (same as indicator), -.236 hidden. Must pass at all 4 TFs (1m, 3m, 5m, 15m).
  2. **AT-2:** Pressure derived from trades side A/B/N. Must pass at all 4 TFs.
  3. **AT-3:** Confidence-gating on unknown-side volume (LOW confidence → force WAIT, never GO). Must pass at all 4 TFs.
  4. **AT-4 (new):** On-demand lifecycle — COLD → WARM on dashboard open, WARM → COLD on close after 60s cooldown. Verify CPU/memory drops to near-zero in COLD state.
  5. Browser smoke: open dashboard, verify chart renders from DuckDB history, verify live data starts flowing, switch 5m→1m, verify ALL surfaces update (chart, fibs, MAs, pressure, nexus, cards).
  6. Latency test: on 1m TF, verify full state push (bar + fibs + MAs + pressure + nexus + trigger + cards) arrives and renders within reasonable time after bar close.
  7. Correlations isolation: verify correlations stay on 1h regardless of chart TF.
  8. Full error patterns checklist (16 items) — every item must pass.
  9. `npm run lint` + `npm run build` (Next.js/Vercel side must stay green — we haven't demoted it yet)
  10. `pytest tests/engine/` — all engine tests pass
- **Expected artifacts:** AT-1/2/3/4 evidence packets with screenshots and test logs, browser smoke recording, Phase 7 closeout
- **Verification:** All ATs pass at all TFs; no error patterns detected
- **Codex QA gate:** Independent AT verification, error pattern review
- **Stop condition:** Any AT fails
- **Approval required:** Kirk accepts AT results
