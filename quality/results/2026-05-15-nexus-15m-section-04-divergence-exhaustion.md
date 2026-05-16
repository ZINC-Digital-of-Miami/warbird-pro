# Nexus 15m Section 04 — Divergence Exhaustion — 2026-05-15

## Scope
- Section: `divergence_exhaustion`
- Target: `label_swing_low_next_12b`
- Trigger family: `NEXUS_FOOTPRINT_DELTA`
- Source CSV: `/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_d464a.csv`
- Source SHA256: `560a0da03115be6c689a61c7bb5cdea861e16174a6a115efb65c25f745b351d7`
- Dataset SHA256: `004e4b7ed584d12de7a722e5a32ecd1752ac5374bedf924cc8bffd95f2d36d79`
- Model output: `/Volumes/Satechi Hub/warbird-pro/models/warbird_nexus_ml_rsi_15m/heavy_20260515_213422/divergence_exhaustion`
- Scope lock: Nexus-only; No V9 Pine/trainer/export/model/fib surface used.

## Neural + Scout Settings
- Model profile: `neural_scout`
- Full HPO families: `['FASTAI', 'NN_TORCH']`
- Fixed scout families: `['GBM', 'CAT', 'XGB']`
- Dropped families: `['RF', 'XT']`
- HPO trials per neural family: `80`
- Bagging: `5` folds × `2` sets
- Stack levels: `1`
- AutoGluon reported total runtime: `6034.62` seconds

## Section Decision
- Decision: `save_and_proceed`
- Passed: `True`
- Reason: Chronological test beat baseline gates; save this section and proceed.
- Baseline log loss: `0.4625116554590619`
- Test log loss: `0.45925128646250585`
- Log-loss lift: `0.0032603689965560734`
- Baseline AP/base rate: `0.8260869565217391`
- Test average precision: `0.8563185408348117`
- AP lift: `0.0302315843130726`
- Test ROC AUC: `0.5716598042725862`
- Predicted-positive rate at 0.5: `1.0`

## Caution
This target is highly imbalanced and the default 0.5 threshold predicts all positives. Treat as weak-pass diagnostics rather than a settings-ready divergence model.

## Top Model
- Top model: `NeuralNetTorch_BAG_L1/f87e2_00023`
- Top score test: `-0.4562097709580979`
- Top score validation: `-0.46716498802068007`

## Top Feature Importance
- `price_ret_1_atr`: `0.0051047767762197275`
- `price_range20_atr`: `0.0046565708987141245`
- `price_er20`: `0.0017978726205090223`
- `price_atr14`: `0.00041728543359404455`
- `price_tr`: `0.0003026998367764322`
- `nexus_gasout_bull`: `8.49968097401621e-05`
- `nexus_div_reg_bear_raw`: `5.859160555804488e-05`
- `close`: `5.146653856645811e-05`
- `nexus_div_reg_bear`: `5.087885356417909e-05`
- `open`: `4.571991736955772e-05`

## Next Section
Proceed to `signal_tier_composite`; keep divergence/exhaustion evidence diagnostic until a better balanced target is approved.
