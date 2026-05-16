# Nexus 15m Research-Heavy Training Settings Update — 2026-05-15

## V9 Re-Review Findings
- V9 production uses `presets="best_quality"`, 7-family zoo, `calibrate=True`, `log_loss`, HPO, `persist()`, leaderboard, and feature importance.
- V9 also explicitly sets `num_bag_folds=0`, `num_stack_levels=0`, and `dynamic_stacking=False` for time-series safety; performance proof comes from chronological validation/test with embargo.
- The first Nexus run copied that no-bag/no-stack safety stance, so it was a smooth baseline/test train rather than the intended hour-plus research-heavy run.

## Updated Nexus Research-Heavy Defaults
- Time limit: `14400` seconds
- HPO trials per family: `80`
- Bag folds: `5`
- Bag sets: `2`
- Stack levels: `1`
- Dynamic stacking: `auto`
- Feature-importance shuffles: `10`
- `use_bag_holdout=True` whenever bagging is enabled

## Look-Forward / Overfit Guard
- Target horizon: `12` bars for `label_volume_expansion_next_12b`
- Dataset embargo: `21` bars
- Bagging/stacking is used only as variance reduction inside the historical training segment.
- Chronological validation remains `tuning_data`/bag-holdout for ensemble weighting/calibration.
- Future test remains untouched until final scoring.
- Internal AutoGluon k-fold scores are not accepted as OOS proof.

## Smoke Verification
A short bagged/stacked smoke train completed with:

```bash
--time-limit 3600 --hpo-trials 1 --num-bag-folds 2 --num-bag-sets 1 --num-stack-levels 1 --dynamic-stacking auto
```

AutoGluon accepted `use_bag_holdout=True`, bagged fold models, stacked L2 models, and chronological `tuning_data`.

## Full Research-Heavy Command

```bash
python scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/train_nexus_15m_heavy.py \
  --manifest scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/exports/nexus_15m_dataset.manifest.json \
  --target label_volume_expansion_next_12b \
  --time-limit 14400 \
  --hpo-trials 80 \
  --num-bag-folds 5 \
  --num-bag-sets 2 \
  --num-stack-levels 1 \
  --dynamic-stacking auto
```
