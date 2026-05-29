---
name: v9-core-training-governance
description: Use before changing, reviewing, or launching Warbird Pro V9 Core AutoGluon training.
owner: warbird
last_reviewed: 2026-05-22
disable-model-invocation: true
---

# V9 Core Training Governance

Use this skill for V9/Core trainer, ETL, manifest, feature, split, or training
launch work.

## Active path

- Trainer: `scripts/ag/train_v9_locked.py`
- Current 15m export:
  `scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.csv`
- Core builder:
  `scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py`
- Data layer: DuckDB + Pandera + `data_profiling`
- Model family: AutoGluon Tabular through the locked trainer

Do not route V9/Core work through `train_ag_baseline.py`, local Postgres
`ag_training`, cloud Supabase, or legacy warehouse preflight skills unless Kirk
explicitly reopens that architecture. FRED/macro data is approved under
local-first policy when manifest-backed.

## Stop conditions

- Do not start training/modeling unless the user explicitly asks.
- Do not build/train ES 5m until ES 15m fit + SHAP + Monte Carlo success is
  documented.
- Do not use `scripts/ag/train_hard_gate.py` for V9/Core production claims
  while it still routes to the legacy baseline trainer.
- Do not change Pine, fib anchors, label semantics, or export fields without
  explicit Pine approval and the Pine verification gate.

## AG contract (2026-05-28 — UNLOCKED, TBD)

Model selection (AutoGluon families, hyperparameters) is TBD pending deep
research. The prior full-zoo config below is reference only:

- `eval_metric="log_loss"`
- `calibrate=True`
- `num_bag_folds=0`
- `num_stack_levels=0`
- `dynamic_stacking=False`
- prior zoo: GBM, CAT, XGB, RF, XT, NN_TORCH, FASTAI
- OpenMP/BLAS thread guards before AutoGluon imports
- chronological split with embargo, not IID bagging

The target is `winner_tp_before_sl`. The trainer expands each admitted entry
across the discoverable TP/SL combo grid and scores combo-aware features.

## Preflight before edits

1. Run `git status --short`.
2. Read the active authority docs for the touched surface.
3. Inspect `train_v9_locked.py`, the Core builder, relevant manifest, and
   touched `tests/ag/**`.
4. Verify manifest feature and knob counts against current source constants,
   not memory.
5. Identify the exact verification gate before writing.

## Required verification when touched

For trainer, ETL, manifest, provenance, SHAP/MC integration, or Core feature
changes, run impacted `tests/ag/**` plus at minimum:

```bash
pytest tests/ag/test_v9_core_indicator_input_contract.py -q
pytest tests/ag/test_v9_core_training_targets.py -q
```

Run broader gates when the changed surface requires them. If a required gate is
not run, report the task as incomplete.

## Feature-change rules

- Every feature must be available at prediction time and tied to an approved
  manifest-backed source.
- FRED, macro, news, options, and cross-asset data are approved under
  local-first policy (2026-05-28) when manifest-backed. No cloud joins or
  non-manifest-backed features.
- Active Pine-native cross-asset context is NQ + 6E only.
- TP ladder prices are label-construction inputs, not model features.
- Update docs/contracts/tests in the same change when feature or label truth
  changes.

## Legacy source handling

The old training skill set (`training-full-zoo`, `training-gbm-only`,
`training-pre-audit`, `preflight-training`, `training-hard-gate`, and
warehouse-facing variants) contains useful failure history, but much of its
command text targets the retired Postgres/`train_ag_baseline.py` lane. Reuse
its lessons only after mapping them to the active V9/Core files above.
