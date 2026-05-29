---
name: warbird-tuning-router
description: Use when choosing between V9 Core AG training, retained Optuna research lanes, TradingView CDP tuning, and manual TV validation.
owner: warbird
last_reviewed: 2026-05-22
disable-model-invocation: true
---

# Warbird Tuning Router

Use this skill before selecting a tuning or optimization path. Pick the path
from the data source and contract, not from old file names.

## Decision table

| Work type | Route |
| --- | --- |
| V9 Core entry/TP-SL model training | `scripts/ag/train_v9_locked.py` |
| V9 Core ETL/export rebuild | `scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py` |
| V9 post-fit SHAP/MC | `scripts/ag/shap_v9.py` + `scripts/ag/monte_carlo_v9.py` |
| TV-only indicator behavior or live chart validation | `tv-preflight` then one explicit TV/CDP operation |
| Retained legacy/research profile optimization | `scripts/duckdb_local/runner.py` after explicit reopen |
| Retained dashboard/runtime health | `python scripts/duckdb_local/runtime_health.py` |
| Final visual/manual validation | TradingView evidence with manifest and settings recorded |

## Active boundaries

- V9 Core is not an Optuna lane.
- Nexus V3 HUD/refactor work is not an Optuna lane; any `optuna` token in a
  Nexus filename is legacy naming only.
- Retained legacy/research profile work may use the DuckDB-local runner only
  when explicitly reopened and manifest-backed.
- TradingView export evidence stays manual unless the user explicitly approves
  a live TV operation for the current session.

## Routing rules

1. If the knob changes Pine-only behavior, footprint values, chart state, or
   TradingView calculation, route to TradingView validation after CDP preflight.
2. If the knob is an AG model/trainer choice, route to V9 Core governance.
3. If the task is SHAP, Monte Carlo, EV, or calibration on a fitted V9 model,
   route to the post-fit gate skill.
4. If the task is a retained profile adapter or dashboard lane, verify
   `scripts/duckdb_local/indicator_registry.json`, the workspace, and runtime
   health before any launch.
5. If Pine is touched, run the full Pine verification matrix.

## Retained runner preflight

For explicitly reopened legacy/research profile work, inspect before running:

```bash
git status --short
rg -n "indicator_key|profile_module|study.db|default_study_name" scripts/duckdb_local docs AGENTS.md CLAUDE.md
python scripts/duckdb_local/runtime_health.py
```

Then answer:

- active indicator key, profile module, workspace, symbol, timeframe
- approved source data and manifest
- swept vs locked parameters
- IS/OOS/embargo split
- artifact that will prove the champion

## Hard stops

- Do not tune on OOS.
- Do not use mock, synthetic, or stale exports.
- Do not use local OHLCV/Databento bars for Nexus footprint claims.
- Do not reintroduce cloud or non-manifest-backed feature stacking into V9/Core.
  FRED/macro data is approved under local-first policy when manifest-backed.
- Do not restart, kill, or launch TradingView as recovery automation.
