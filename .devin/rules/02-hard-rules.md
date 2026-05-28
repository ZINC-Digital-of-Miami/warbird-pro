# Hard Rules

## Data

- Training rows come only from: Warbird Pro V9 Pine/TV exports, approved Databento ES market-data (5m/15m), or Nexus footprint evidence
- No FRED, macro, news, options, or unapproved cross-asset features. Active cross-asset: NQ + 6E only
- No daily-ingestion training dependency
- If a feature is not in Pine/TV output or approved Databento context, it is not in the modeling dataset

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
- DuckDB for local data/trade recording (replacing Supabase for training data)
- No Prisma, Drizzle, or ORM
- Local PG17 `warbird` warehouse is legacy/reference only
