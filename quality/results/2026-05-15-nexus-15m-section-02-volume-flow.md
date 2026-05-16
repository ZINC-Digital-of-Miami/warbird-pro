# Nexus 15m Section 02 — Volume Flow — 2026-05-15

## Scope
- Section: `volume_flow`
- Target: `label_volume_expansion_next_12b`
- Trigger family: `NEXUS_FOOTPRINT_DELTA`
- Source CSV: `/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_d464a.csv`
- Source SHA256: `560a0da03115be6c689a61c7bb5cdea861e16174a6a115efb65c25f745b351d7`
- Dataset SHA256: `004e4b7ed584d12de7a722e5a32ecd1752ac5374bedf924cc8bffd95f2d36d79`
- Model output: `/Volumes/Satechi Hub/warbird-pro/models/warbird_nexus_ml_rsi_15m/heavy_20260515_162301/volume_flow`
- Scope lock: Nexus-only; No V9 Pine/trainer/export/model/fib surface used.

## Full-Assault Settings
- AutoGluon preset: `best_quality`
- Time limit: `14400` seconds
- HPO trials per family: `80`
- Bagging: `5` folds × `2` sets
- Stack levels: `1`
- Dynamic stacking: `auto`
- Feature-importance shuffles: `10`
- AutoGluon reported total runtime: `9375.71` seconds

## Section Decision
- Decision: `save_and_proceed`
- Passed: `True`
- Reason: Chronological test beat baseline gates; save this section and proceed.
- Baseline log loss: `0.6825200759691016`
- Test log loss: `0.5127965361629997`
- Log-loss lift: `0.1697235398061019`
- Baseline AP/base rate: `0.4254658385093168`
- Test average precision: `0.8423268715847081`
- AP lift: `0.4168610330753913`
- Test ROC AUC: `0.8577058810635453`

## Top Model
- Top model: `NeuralNetFastAI_BAG_L1/d5f89_00070`
- Top score test: `-0.41832216930552046`
- Top score validation: `-0.4276119527158182`

## Top Feature Importance
- `nexus_fp_total_volume`: `0.37536340223781756`
- `nexus_visible_vf_bull`: `0.0030277581799166508`
- `price_tr`: `0.0016211323424230374`
- `nexus_gasout_bull`: `0.00024937969764944335`
- `open`: `0.0`
- `low`: `0.0`
- `close`: `0.0`
- `high`: `0.0`
- `nexus_visible_vf_bear`: `-0.00027361578446467584`
- `nexus_visible_delta_gasout`: `-0.0006889865354599234`

## Next Section
Proceed to `oscillator_regime` using the same section-chain contract because Section 02 cleared the chronological test gate.
