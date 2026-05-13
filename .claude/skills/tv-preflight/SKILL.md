---
name: tv-preflight
description: Run BEFORE any TradingView CDP/MCP operation in this session. Wraps `python3 scripts/ag/tv_connection_doctor.py --json` and gates whether TV ops can proceed. If `ready: false`, this skill stops the workflow and points at cdp-down-recovery. Mandatory floor per CLAUDE.md Locked Rule. Invoke before pine_save, pine_set_source, pine_smart_compile, chart_set_symbol, data_get_*, or any other mcp__tradingview__* call.
---

# TradingView Preflight

Before any TV MCP call this session, verify CDP is up via the read-only doctor.

## Run

```bash
python3 scripts/ag/tv_connection_doctor.py --json
```

The script:
- Does NOT launch, kill, restart, or modify TradingView
- Reports `ready: true|false` plus per-check details (process, CDP HTTP, MCP server path, etc.)
- Is safe to run as preflight (NOT as recovery probe — that's the banned `tv_health_check` pattern)

## Decision tree

**`ready: true`** — proceed with the planned TV ops. Stick to one explicit command at a time. No retry loops.

**`ready: false`** — STOP. Read the doctor output for the specific failed check (TradingView process, CDP HTTP, MCP server path). Report the failure to the operator with the exact field that's false. Then invoke `cdp-down-recovery` skill and wait for human direction.

**Doctor itself errors or hangs** — treat as `ready: false`. Same stop-and-report path.

## What "proceed" means

After `ready: true` you are authorized for ONE planned batch of TV ops. If any TV op in the batch fails with a CDP-related error, you do NOT re-run the doctor — you go directly to `cdp-down-recovery`. Doctor on the way in only.

## Verify-tv-slot reminder

If your planned ops include `pine_save`, `pine_set_source`, or `pine_new`, also invoke the existing `verify-tv-slot` skill before issuing the write. That skill prevents silent overwrites of the currently-open Pine Editor slot — different concern from CDP readiness.

## Pine source size warning

`pine_get_source` can return 200KB+ for complex scripts and burn context budget. Do not call it just to "see what's there" — read the local file via `Read` instead. Use `pine_get_source` only when you specifically need to compare local vs. live and have already paged-down your other context.

## Banned operations even when CDP is up

CLAUDE.md Locked Rules still apply when CDP is healthy:
- No `tv_launch` (any args)
- No `pine_save` without operator approval — CLAUDE.md: "No TradingView Pine Editor push without explicit approval"
- No retry loops on any failed op
- No `mcp__computer-use__request_access` against TradingView apps

## When to invoke this skill

- First TV MCP call of the session
- After a long gap with no TV activity (process state changes)
- After the operator says "TV is back up" — preflight before resuming
- Before any `pine_save` / `pine_smart_compile` / `pine_set_source` even mid-session
