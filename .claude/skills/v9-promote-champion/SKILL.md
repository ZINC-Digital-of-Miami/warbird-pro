---
name: v9-promote-champion
description: Run BEFORE promoting any V9 Core training artifact to a live TradingView alert or champion. This is a user-invoked promotion checklist; the model cannot self-invoke it. Walks through SHAP gate, Monte Carlo EV gate at τ=0.75, provenance review, calibration verification, Pine alert wire-up readiness, and the post-promote main-branch push. Refuses to declare GO without evidence on every gate. Promotion artifacts get appended to docs/audits/<date>-v9-promotion-<run>.md.
disable-model-invocation: true
---

# V9 Champion Promotion Checklist (user-invoked only)

Promotion is an operator decision, not an agent decision. This skill exists so the checklist runs the same way every time and the evidence trail is auditable later.

## Inputs you must provide

- Run ID (the `locked_<timestamp>` directory under `models/warbird_pro_v9/`)
- Threshold to promote (default `τ = 0.75`; document any deviation)

If either is missing, the skill stops and asks for it.

## Gate sequence (run in order; do NOT skip)

### Gate 1 — Provenance
Invoke the `v9-promote-validator` subagent for the provenance check only. It reads `models/warbird_pro_v9/<run>/manifest.json` and confirms:

- CSV input path + SHA recorded
- Train/val/test ranges recorded and non-overlapping
- Embargo bars = 11
- `ML_FEATURES = 75`, `MODEL_FEATURES = 81`
- `calibrate = True`
- `eval_metric = log_loss`
- `preset = best_quality`
- `num_bag_folds = 0`, `num_stack_levels = 0`, `dynamic_stacking = False`

Any field missing or drifted → STOP. The operator must rerun the trainer with proper provenance, or run the existing `backfill_v9_run_provenance.py` if the artifact is otherwise good.

### Gate 2 — SHAP
Run `python3 scripts/ag/shap_v9.py --run-dir models/warbird_pro_v9/<run>`. Confirm:

- Top 10 features printed; no single feature carries > 80% importance
- No train→val SHAP drift > 30% on a top-10 feature
- Feature names match `ML_FEATURES` contract (no orphan columns, no DXY survivors)

Stop on any failure. Cite the SHAP output path.

### Gate 3 — Monte Carlo EV
Run `python3 scripts/ag/monte_carlo_v9.py --run-dir models/warbird_pro_v9/<run> --threshold 0.75`. Confirm:

- N trades at τ=0.75 is non-trivial (compare to today's reference: 296/4,836 from artifact `locked_20260512`)
- Win rate at τ=0.75 ≥ reference WR
- EV/trade ≥ $0 at MES $5/point flat 1-tick NinjaTrader Basic commission floor (reference: $198.85/trade)
- Max drawdown reported and acceptable to operator
- 38/38 MC integrity checks pass (or equivalent — read the MC output for the integrity tally)

Stop on any failure. Cite the MC output path.

### Gate 4 — Calibration
Confirm the predictor's `calibrate=True` actually produced an isotonic calibrator (uncalibrated probabilities mean τ=0.75 is not a 75% real-world WR — it's just a number).

```
python3 - <<'PY'
from autogluon.tabular import TabularPredictor
p = TabularPredictor.load("models/warbird_pro_v9/<run>/<predictor_dir>")
print("calibrator:", getattr(p._learner, "_calibrated_class", None))
PY
```

A `None` calibrator → STOP and rerun.

### Gate 5 — Pine alert readiness
Confirm the Pine file `indicators/warbird-pro-v9.pine` has the alert plumbing in place to fire on the chosen threshold:

- `alertcondition(` calls in the file (per CLAUDE.md V9 budget: 2 `alertcondition`)
- The condition variables map to entry / TP / SL outputs the AG predictor scored
- Threshold τ is configurable via input, or is hardcoded matching the promoted value

Run `./scripts/guards/pine-lint.sh indicators/warbird-pro-v9.pine` to confirm the file is currently clean.

### Gate 6 — Audit log
Append the decision to `docs/audits/<YYYY-MM-DD>-v9-promotion-<run>.md` with:

- Run ID + timestamp
- Threshold promoted (and source — Optuna champion / operator override / default)
- Gate 1–5 results with cited evidence paths
- Operator name + decision (GO / NO-GO)
- Pre-promotion vs. post-promotion `git rev-parse HEAD`

If GO, you are now authorized to wire the Pine alert and push to main. If NO-GO, the run is rejected and the audit log records that.

## Post-promotion

1. Commit the Pine alert wire-up (if any was changed) directly to `main` per CLAUDE.md Locked Rule.
2. Push `main`.
3. Confirm the live TV chart picks up the new alert (operator-checked, not agent-checked).
4. Update `MEMORY.md` index with a new project memory pointing at the promotion audit file.

## What you do NOT do in this skill

- Do NOT skip a gate because "it passed last time."
- Do NOT promote based on a partial validator output. All five gates pass or it's NO-GO.
- Do NOT call any banned TV op (`tv_launch`, etc.) even if the chart looks frozen.
- Do NOT edit the model artifact — promotions read, they don't mutate.
- Do NOT push to a feature branch — direct-to-`main` per Locked Rule.
