---
name: cdp-down-recovery
description: Invoke when ANY TradingView MCP call fails because CDP is unresponsive, when the chart tab vanished, when Optuna runs report "Optuna conn blocked—CDP down", or any time you're about to rationalize calling tv_launch / tv_health_check as recovery / launch_tv_debug_mac.sh / pkill TradingView / killall TradingView / computer-use request_access on TradingView. This skill enforces the CLAUDE.md Locked Rule HARD STOP protocol — there is no agent-side recovery. The skill body is the literal protocol; reading it is the action.
disable-model-invocation: false
---

# CDP-down HARD STOP protocol

CLAUDE.md Locked Rule, authorized 2026-05-05 after the second `tv_launch` incident in two days.

## What you must do

1. STOP IMMEDIATELY. Drop the current TV operation. Do not retry.
2. Report this exact phrase to the operator:
   > **CDP is not responding. I'm stopped. Waiting for instructions.**
3. Wait for explicit human direction. Do nothing else TV-related.

## What you must NOT do

Banned methods, **no parameters that make them OK**:

- `tv_launch` (any args, including `kill_existing: false` — Electron's single-instance lock kills the running TV regardless)
- `tv_health_check` as a recovery probe (use only when explicitly authorized after operator says CDP is back up)
- `launch_tv_debug_mac.sh` (the helper script Kirk runs manually — agent does not invoke it)
- `pkill -f TradingView`
- `killall TradingView`
- `mcp__computer-use__request_access` against TradingView
- Any "retry loop" disguised as "verifying the symptom"

## Why this rule is absolute

Soft variants of this rule have been rationalized around twice. This version is intentionally written so there is no judgment call. If a TV MCP call errors, you stop. You do not diagnose. You do not "verify the connection just once more." The operator has the launcher script and decides when CDP is back.

## Recovery path (operator-owned, not agent-owned)

The operator's recovery workflow is:
1. They run `/Users/zincdigital/tradingview-mcp/scripts/launch_tv_debug_mac.sh` from their own terminal.
2. They confirm CDP is up by checking `http://localhost:9222/json/version` in a browser, OR by running `python3 scripts/ag/tv_connection_doctor.py --json` and reading `ready: true`.
3. They tell you "CDP is back, resume work." Only then do you resume.

## Doctor (read-only — agent CAN run this)

`python3 scripts/ag/tv_connection_doctor.py --json` is read-only and does not launch, kill, restart, or modify TV. You may run it BEFORE the first TV op in a session as a preflight. You may NOT run it as a recovery probe after a failure — that's the banned `tv_health_check`-style use.

## When to invoke this skill

- Any TV MCP tool returned an error mentioning CDP, Chrome DevTools Protocol, ECONNREFUSED on 9222, or a hung response
- The tradingview MCP server itself appears disconnected (`tv_discover` errors, etc.)
- An Optuna job log shows "Optuna conn blocked" or similar
- You are about to type `tv_launch` and your brain says "just this once"

If any of those apply, read the protocol above and execute step 1 — stop and report.
