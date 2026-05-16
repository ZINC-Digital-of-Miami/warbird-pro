# Nexus 15m Section 01 — Footprint Delta Flow — 2026-05-15

## Scope
- Section: `footprint_delta_flow`
- Target: `label_volume_expansion_next_12b`
- Trigger family: `NEXUS_FOOTPRINT_DELTA`
- Source CSV: `/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_d464a.csv`
- Source SHA256: `560a0da03115be6c689a61c7bb5cdea861e16174a6a115efb65c25f745b351d7`
- Dataset SHA256: `004e4b7ed584d12de7a722e5a32ecd1752ac5374bedf924cc8bffd95f2d36d79`
- Model output: `/Volumes/Satechi Hub/warbird-pro/models/warbird_nexus_ml_rsi_15m/heavy_20260515_132152/footprint_delta_flow`
- Scope lock: Nexus-only; No V9 Pine/trainer/export/model/fib surface used.

## Full-Assault Settings
- AutoGluon preset: `best_quality`
- Time limit: `14400` seconds
- HPO trials per family: `80`
- Bagging: `5` folds × `2` sets
- Stack levels: `1`
- Dynamic stacking: `auto`
- Feature-importance shuffles: `10`
- AutoGluon reported total runtime: `9397.72` seconds

## Leakage / Look-Forward Guard
- Label horizon: `12` bars
- Embargo: `21` bars
- Bagging policy: AutoGluon k-fold bagging is allowed only inside the historical train segment; chronological validation is passed as tuning_data with use_bag_holdout=True, and the future test split is never used for fitting or ensemble weighting.
- Proof policy: Use chronological validation/test metrics only; never treat internal k-fold scores as OOS proof.

## Split Counts
| Split | Rows | Positives | Positive rate | Start | End |
| --- | ---: | ---: | ---: | --- | --- |
| train | 4661 | 2058 | 0.4415 | 2026-02-03T16:00:00+00:00 | 2026-04-15T18:45:00+00:00 |
| validation | 978 | 430 | 0.4397 | 2026-04-16T01:15:00+00:00 | 2026-04-30T15:30:00+00:00 |
| test | 966 | 411 | 0.4255 | 2026-04-30T22:00:00+00:00 | 2026-05-15T09:15:00+00:00 |

## Section Decision
- Decision: `save_and_proceed`
- Passed: `True`
- Reason: Chronological test beat baseline gates; save this section and proceed.
- Baseline log loss: `0.6825200759691016`
- Test log loss: `0.5287160693936275`
- Log-loss lift: `0.1538040065754741`
- Baseline AP/base rate: `0.4254658385093168`
- Test average precision: `0.8418687068323737`
- AP lift: `0.4164028683230569`
- Test ROC AUC: `0.8532737116678722`

## Top Model
- Top model: `NeuralNetFastAI_BAG_L1/8510c_00042`
- Top score test: `-0.44143733860464207`
- Top score validation: `-0.44596073532537317`

## Top Feature Importance
- `nexus_fp_total_volume`: `0.36584885920509286`
- `nexus_fp_bar_delta`: `0.005845042455100369`
- `nexus_norm_cum_delta`: `0.00204587163832326`
- `price_tr`: `0.00025480504146264683`
- `nexus_delta_slope`: `0.0002262308499261123`
- `open`: `0.0`
- `high`: `0.0`
- `low`: `0.0`
- `close`: `0.0`
- `nexus_delta_dir`: `-0.0007492912999571555`

## Next Section
Proceed to `volume_flow` using the same section-chain contract because Section 01 cleared the chronological test gate.
