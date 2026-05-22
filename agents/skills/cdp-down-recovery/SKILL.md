---
name: cdp-down-recovery
description: Invoke when any TradingView MCP call fails because CDP is unresponsive. Enforces hard-stop protocol with no agent-side recovery actions.
disable-model-invocation: false
---

# CDP-down HARD STOP protocol

AGENTS locked rule, authorized 2026-05-05.

## What you must do

1. STOP IMMEDIATELY. Drop the current TV operation. Do not retry.
2. Report this exact phrase to the operator:
   > **CDP is not responding. I'm stopped. Waiting for instructions.**
3. Wait for explicit human direction. Do nothing else TV-related.

## What you must NOT do

Banned methods, no parameters that make them OK:

- `tv_launch` (any args, including `kill_existing: false`)
- `tv_health_check` as a recovery probe
- `launch_tv_debug_mac.sh`
- `pkill -f TradingView`
- `killall TradingView`
- `mcp__computer-use__request_access` against TradingView
- any retry loop disguised as symptom verification

## Why this rule is absolute

There is no judgment-call path here. If a TV MCP call errors on CDP, stop and
report. Recovery is operator-owned.

## Recovery path (operator-owned)

1. Operator runs `/Users/zincdigital/tradingview-mcp/scripts/launch_tv_debug_mac.sh`.
2. Operator confirms CDP health (`http://localhost:9222/json/version` or
   `python3 scripts/ag/tv_connection_doctor.py --json` with `ready: true`).
3. Operator explicitly authorizes resume.

## Doctor rule

`python3 scripts/ag/tv_connection_doctor.py --json` is allowed as preflight
only, not as a post-failure recovery probe.
