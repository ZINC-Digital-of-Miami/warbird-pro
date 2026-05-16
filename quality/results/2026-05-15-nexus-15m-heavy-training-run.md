# Nexus 15m Baseline Heavy Training Test Run — 2026-05-15

## Scope
- Trigger family: `NEXUS_FOOTPRINT_DELTA`
- Target: `label_volume_expansion_next_12b`
- Source CSV: `/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_d464a.csv`
- Source SHA256: `560a0da03115be6c689a61c7bb5cdea861e16174a6a115efb65c25f745b351d7`
- Dataset SHA256: `004e4b7ed584d12de7a722e5a32ecd1752ac5374bedf924cc8bffd95f2d36d79`
- Model output: `/Volumes/Satechi Hub/warbird-pro/models/warbird_nexus_ml_rsi_15m/heavy_20260515_125550`
- Scope lock: Nexus-only; No V9 Pine/trainer/export/model/fib surface used.

## Split Counts
| Split | Rows | Positives | Positive rate | Start | End |
| --- | ---: | ---: | ---: | --- | --- |
| train | 4661 | 2058 | 0.4415 | 2026-02-03T16:00:00+00:00 | 2026-04-15T18:45:00+00:00 |
| validation | 978 | 430 | 0.4397 | 2026-04-16T01:15:00+00:00 | 2026-04-30T15:30:00+00:00 |
| test | 966 | 411 | 0.4255 | 2026-04-30T22:00:00+00:00 | 2026-05-15T09:15:00+00:00 |

## Fit Settings
- Presets: `best_quality`
- Eval metric: `log_loss`
- Time limit: `7200` seconds
- HPO trials per family: `20`
- Bag folds / stack levels: `0` / `0`
- Dynamic stacking: `False`

## Result
- Top model: `WeightedEnsemble_L2`
- Test log loss: `0.42941420333658104`
- Validation score: `-0.4344130108073418`
- Test ROC AUC: `0.8812125994607747`
- Test average precision: `0.8496896703304528`
- Accuracy at 0.5: `0.8178053830227743`

## Top Feature Importance
- `nexus_fp_total_volume`: `0.5490826460097068`
- `price_range20_atr`: `0.01576499955020465`
- `nexus_visible_vf_bear`: `0.014382676587710752`
- `nexus_norm_cum_delta`: `0.013296214635968006`
- `nexus_vf_calc`: `0.011751577117688395`
- `nexus_visible_vf_bull`: `0.010757356328148527`
- `price_tr`: `0.00682481065162831`
- `nexus_regime_score`: `0.004309622905893551`
- `nexus_osc_momentum`: `0.0013129416293918505`
- `nexus_visible_signal_line`: `0.0012263114466108504`

## Notes
- This run completed the first sequential heavy target only.
- AutoGluon dropped constant train-split features internally (`nexus_fp_quality_ok`, `nexus_fp_available`, `nexus_mode_minutes`, `nexus_pivot_span`, and visible static level/base columns), which is expected because the training subset is footprint-quality only.
- The result is evidence for volume-expansion precursor modeling, not a Pine setting change by itself.


## Baseline/no-bag test train note
- This completed smoothly and proved the pipeline, but it used the initial no-bag/no-stack profile.
- It is now treated as a baseline test train, not the final research-heavy run.
- Research-heavy settings were added afterward with bagging, bag sets, stacking, and stricter look-forward guardrails.
