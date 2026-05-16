# Nexus 15m Section 03 — Oscillator Regime — 2026-05-15

## Scope
- Section: `oscillator_regime`
- Target: `label_abs_move_ge_0p5atr_5b`
- Trigger family: `NEXUS_FOOTPRINT_DELTA`
- Source CSV: `/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_d464a.csv`
- Source SHA256: `560a0da03115be6c689a61c7bb5cdea861e16174a6a115efb65c25f745b351d7`
- Dataset SHA256: `004e4b7ed584d12de7a722e5a32ecd1752ac5374bedf924cc8bffd95f2d36d79`
- Model output: `/Volumes/Satechi Hub/warbird-pro/models/warbird_nexus_ml_rsi_15m/heavy_20260515_195557/oscillator_regime`
- Scope lock: Nexus-only; No V9 Pine/trainer/export/model/fib surface used.

## Neural + Scout Settings
- Model profile: `neural_scout`
- Full HPO families: `['FASTAI', 'NN_TORCH']`
- Fixed scout families: `['GBM', 'CAT', 'XGB']`
- Dropped families: `['RF', 'XT']`
- HPO trials per neural family: `80`
- Bagging: `5` folds × `2` sets
- Stack levels: `1`
- AutoGluon reported total runtime: `5424.82` seconds

## Section Decision
- Decision: `save_and_proceed`
- Passed: `True`
- Reason: Chronological test beat baseline gates; save this section and proceed.
- Baseline log loss: `0.6685614502837951`
- Test log loss: `0.6615487565720294`
- Log-loss lift: `0.007012693711765716`
- Baseline AP/base rate: `0.6248715313463515`
- Test average precision: `0.6719593273141307`
- AP lift: `0.04708779596777912`
- Test ROC AUC: `0.5500090122566692`

## Caution
This section cleared the gate but only barely on ROC AUC. Treat it as weak-pass evidence, not a standalone Pine settings recommendation.

## Top Model
- Top model: `NeuralNetTorch_BAG_L1/fa360_00052`
- Top score test: `-0.6509051826681567`
- Top score validation: `-0.6081789442881096`

## Top Feature Importance
- `price_tr`: `0.010821323421849794`
- `nexus_regime_score`: `0.0029442990749883103`
- `price_range20_atr`: `0.0026751637246290373`
- `price_atr14`: `0.002074390382535085`
- `nexus_delta_slope`: `0.0014331599563319642`
- `nexus_visible_signal_line`: `0.0012006466052408627`
- `price_ret_1_atr`: `0.00112817809406347`
- `nexus_signal_tier`: `0.000477553781768425`
- `price_er20`: `0.0004372646398589586`
- `nexus_norm_cum_delta`: `0.00019998721347627146`

## Next Section
Proceed to `divergence_exhaustion`, but keep the weak oscillator readout separate from stronger footprint/volume evidence.
