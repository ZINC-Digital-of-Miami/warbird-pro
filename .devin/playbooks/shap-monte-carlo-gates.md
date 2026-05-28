# SHAP & Monte Carlo Validation Gates

Both gates must pass before enabling any TradingView alert. A model that passes log_loss but fails either gate will push high-confidence entries that lose real money.

## Gate 1 — SHAP

```bash
python3 scripts/ag/shap_v9.py --predictor-dir <model-dir> --csv <15m-export>
```

Validates:
- **Top-feature audit** — model uses plausibly causal features, not leakage proxies
- **Per-class importance** — winners and losers driven by overlapping but distinct features
- **Temporal stability** — early-half vs late-half importances shouldn't shift dramatically
- **Calibration check** — `proba > 0.75` should deliver ~75% real-world WR
- **Redundancy** — identify DEAD / REDUNDANT / UNSTABLE feature candidates

## Gate 2 — Monte Carlo

```bash
python3 scripts/ag/monte_carlo_v9.py --predictor-path <model-dir> --csv <15m-export> --split oos
```

Validates:
- **P&L distribution + drawdown** under realistic resampling
- **Per-direction breakdown** — model works both long and short
- **Threshold sweep** — where is EV maximum relative to locked 0.75 threshold?
- **Regime stability** — early-half vs late-half performance
- **Win/loss streak profile** — serial correlation drives drawdown

## On Failure

Route back to settings/feature/Pine changes — NOT to "tune the threshold." The 0.75 threshold is locked per inference contract.
