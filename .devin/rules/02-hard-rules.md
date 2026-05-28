# Hard Rules

## Data

- Never use mock, demo, placeholder, or fake data
- Training rows come only from: Warbird Pro V9 Pine/TV exports, approved Databento ES market-data (5m/15m), or Nexus footprint evidence
- No FRED, macro, news, options, or unapproved cross-asset features. Active cross-asset: NQ + 6E only
- No daily-ingestion training dependency
- If an indicator feature is not in Pine/TV output or approved V9/Core local Databento context, it is not in the active modeling dataset

## Pine

- NEVER edit `indicators/warbird-pro-v9.pine` without explicit approval in the current session
- NEVER edit Nexus Pine files without explicit approval
- NEVER push Pine changes to TradingView Pine Editor without explicit approval
- Fib anchor ownership, ladder math, and trade-state label semantics are protected scope — no changes without explicit approval and before/after evidence
- Never reintroduce the pivot-window `fibHtfSnapshot` variant (`ta.barssince(...)` with `pivotHighInWindow`/`pivotLowInWindow`) — banned due to wide-fib regressions
- Price every new output/request path before writing Pine code (only 10 output slots remain before 64-call hard cap)

## TradingView Safety (CDP-Down Protocol)

- If ANY TradingView MCP call fails because CDP is unresponsive: **STOP IMMEDIATELY**. Report "CDP is not responding. I'm stopped. Waiting for instructions." Wait for human direction.
- Do NOT call `tv_health_check` as recovery probe
- Do NOT call `tv_launch` with any args
- Do NOT use `mcp__computer-use__request_access` against TradingView
- Do NOT attempt any recovery automation
- Banned methods: `tv_launch`, `launch_tv_debug_mac.sh`, `pkill -f TradingView`, `killall TradingView`
- Live TV operations: one explicit command at a time, no retry loops

## Cloud / Database

- Cloud Supabase is runtime/support only — no raw trials, labels, or research datasets
- No Prisma, Drizzle, or ORM
- Local PG17 `warbird` warehouse is legacy/reference only

## Process

- One task at a time, complete fully
- Do not refactor unrelated code
- Do not revert user changes
- Do not start training/modeling unless explicitly asked
