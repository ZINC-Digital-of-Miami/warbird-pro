# Warbird V9 rebuild scope notes

Use these notes when resuming a half-finished Warbird Pro V9 cleanup/rebuild.

## No-edit scope pattern

- Start with `git status --short`.
- Use active Warbird docs as authority; avoid stale v7/MES/strategy-harness assumptions.
- Treat `indicators/warbird-pro-v9.pine` as protected until explicit current-session Pine-edit approval.
- Run V9 Python tests through the repo venv, not whichever `pytest` is first on PATH:
  - `.venv/bin/python -m pytest tests/ag/test_v9_core_indicator_input_contract.py -q`
  - `.venv/bin/python -m pytest tests/ag/test_v9_core_training_targets.py -q`

## Lean-cut probe

`tests/ag/test_v9_pine_lean_cut_contract.py` is intentionally skipped unless `WARBIRD_ENFORCE_PINE_LEAN_CUT=1` is set. Use the env var only as a scoping probe unless Pine edits have been approved:

```bash
WARBIRD_ENFORCE_PINE_LEAN_CUT=1 .venv/bin/python -m pytest tests/ag/test_v9_pine_lean_cut_contract.py -q
```

In the 2026-05-19 scope pass, enforcing this test showed the cleanup was partly complete:

- Passed: ZN/VIX requests/exports were already removed.
- Passed: redundant fib-touch binary emissions were absent.
- Failed: `request.footprint(` and footprint exports still existed.
- Failed: daily/weekly level export plots still existed (`ml_lvl_pdh_dist_atr`, `ml_lvl_pdl_dist_atr`, `ml_lvl_pwl_dist_atr`).

## Contract pitfall

The active V9 file may contain Pine v6-only syntax (`//@version=6`, `input.*(..., active=...)`, `request.footprint()`) while pasted validator text or stale policy notes say Pine edits must remain Pine Script v5. Do not silently choose a side. Surface the conflict and get the v5/v6 direction approved before editing. If the user explicitly confirms “We are Pine V6” in the current session, preserve V6 and do not downgrade.

## Daily open/close cleanup pattern

When replacing daily/weekly hidden exports with daily context exports:

- Keep the footprint request/exports if the user says to keep footprint.
- Remove `ml_lvl_pdh_dist_atr`, `ml_lvl_pdl_dist_atr`, `ml_lvl_pwh_dist_atr`, and `ml_lvl_pwl_dist_atr` from Pine export plots.
- Add hidden exports for current daily open and confirmed prior daily close, e.g. `ml_daily_open` and `ml_daily_close`.
- Do not stop at the Pine patch. Wire new trainable exports into `scripts/ag/train_v9_locked.py`, the Core builder/ETL (`scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py`), locked feature-count tests, and active docs (`CLAUDE.md`, `docs/MASTER_PLAN.md`) so AG actually trains on the new columns.
- Re-run enforced lean-cut, V9 Core contract tests through `.venv`, Pine compile/lint, guardrails, and `npm run build` before claiming the cleanup is complete.

## Training gate

Training is not part of indicator closeout. Only train after:

1. Pine/repo gates are clean,
2. the user explicitly asks to run training,
3. the lane/timeframe sequence is respected (ES 15m before ES 5m).
