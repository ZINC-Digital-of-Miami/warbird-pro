---
name: tv-preflight
description: Run before any TradingView CDP/MCP operation. Uses read-only doctor and gates whether TV ops may proceed.
---

# TradingView Preflight

Before any TV MCP call, verify CDP health using the read-only doctor.

## Run

```bash
python3 scripts/ag/tv_connection_doctor.py --json
```

The script does not launch, kill, restart, or modify TradingView.

## Decision tree

- `ready: true`: proceed with planned TV ops (one explicit command at a time).
- `ready: false`: stop, report failed field, invoke `cdp-down-recovery`, wait.
- doctor errors/hangs: treat as `ready: false`.

## Important

- Preflight is an entry gate, not a failure recovery probe.
- If any TV op fails with CDP-related error after preflight, do not re-run
  doctor. Invoke `cdp-down-recovery` immediately.

## Slot protection reminder

Before `pine_save`, `pine_set_source`, or `pine_new`, invoke the slot safety
skill/workflow to avoid editor-slot overwrites.
