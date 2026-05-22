---
name: v9-promote-champion
description: Promotion checklist for V9 Core artifacts before any live TradingView champion move.
disable-model-invocation: true
---

# V9 Champion Promotion Checklist

Promotion is an operator decision. This skill standardizes gate order and audit
evidence.

## Required inputs

- run id (`models/warbird_pro_v9/locked_<timestamp>`)
- promotion threshold (default `tau = 0.75`)

## Gate order (no skipping)

1. Provenance gate
   - manifest fields complete and aligned to locked contract
2. SHAP gate
   - run `python3 scripts/ag/shap_v9.py --run-dir <run_dir>`
3. Monte Carlo EV gate
   - run `python3 scripts/ag/monte_carlo_v9.py --run-dir <run_dir> --threshold 0.75`
4. Calibration gate
   - confirm calibrator exists when `calibrate=True`
5. Pine alert readiness gate
   - alert plumbing present and lint clean
6. Audit log gate
   - append evidence to `docs/audits/<date>-v9-promotion-<run>.md`

Any gate failure is NO-GO.

## Post-promotion checklist

1. commit approved alert wiring changes to `main`
2. push `main` (only with explicit approval)
3. operator confirms live chart behavior
4. update memory index pointer
