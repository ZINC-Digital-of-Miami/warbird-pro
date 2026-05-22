---
name: v9-postfit-shap-monte-carlo-gates
description: Use for V9 Core SHAP, Monte Carlo, calibration, and promotion-readiness review.
owner: warbird
last_reviewed: 2026-05-22
disable-model-invocation: true
---

# V9 Post-Fit SHAP / Monte Carlo Gates

Use this skill after a V9/Core model fit exists and the work is SHAP, Monte
Carlo, calibration, EV review, or promotion readiness.

## Active scripts

- SHAP: `scripts/ag/shap_v9.py`
- Monte Carlo: `scripts/ag/monte_carlo_v9.py`
- Trainer contract: `scripts/ag/train_v9_locked.py`
- Promotion checklist: `agents/skills/v9-promote-champion/SKILL.md`

Do not use legacy `scripts/ag/run_diagnostic_shap.py` or
`scripts/ag/monte_carlo_run.py` for V9/Core promotion claims.

## Required inputs

- exact run directory: `models/warbird_pro_v9/locked_<tag>/`
- run summary linked to that exact fit
- export CSV + manifest used by the fit
- repo commit and dirty-tree/provenance status
- threshold under review, normally `tau = 0.75`

If any input is missing or not tied to the same run, promotion is blocked.

## Gate order

1. Provenance gate
   - manifest, export hash, commit, feature list, and run summary align.
2. SHAP gate
   - run `shap_v9.py` for the exact run.
   - verify all expected `ML_FEATURES` are present in the inference frame.
3. Monte Carlo gate
   - run `monte_carlo_v9.py` for the exact run and threshold.
   - verify EV, drawdown, threshold, and calibration findings are tied to the
     same predictor/export.
4. Calibration gate
   - `calibrate=True` must be reflected in the fitted predictor artifacts.
5. Promotion gate
   - only after SHAP + MC pass, use `v9-promote-champion`.

## No-go findings

- SHAP or MC ran against a different export, predictor, or feature set.
- Any source data is not manifest-backed.
- `winner_tp_before_sl` label construction is inconsistent with the trainer.
- The worktree/provenance is dirty and the result claims promotion evidence.
- MC results are diagnostic-only but are described as promotion proof.
- 15m has not passed and the task attempts to move to 5m.

## Reporting standard

Report SHAP and MC separately. A completed model fit is not promotion proof.
Promotion requires fit + SHAP + Monte Carlo + provenance all tied to the exact
same run.
