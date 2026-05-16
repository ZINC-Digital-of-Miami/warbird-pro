# Nexus Live Meter Deferred Hold (2026-05-15)

## Operator Directive

Preserve the Nexus live pressure/gas/confidence meter plan in workbook docs now. Do not modify active training or active Nexus Pine during this hold window.

## Freeze Boundary (No-Edit While Run Is Active)

- indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine
- scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/build_nexus_15m_dataset.py
- scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/train_nexus_15m_heavy.py
- in-flight training manifests/artifacts/reports tied to the active run

## Deferred Backlog (Activate After Training Ends)

- Add live pressure meter from footprint bar-delta ratio on a 0-100 scale.
- Add buyer and seller gas-remaining intrabar telemetry.
- Add long/short confidence outputs and confidence state export.
- Extend export-only diagnostics with planned `nexus_*` hold columns.

## Tuning Path Decision Lock

1. Reconstructible knobs (bar-data + TA): Python Optuna path.
2. Pine-only/API-dependent knobs (`request.footprint`, exhaustion internals): CDP TV auto-tune path.
3. Final promotion with small candidate set: Manual Deep Backtest.

Do not route TV-only footprint/exhaustion knobs into reconstruction-only tuning.

## TC Skill Mapping (Required At Resume)

- tc-indicators-basics
- tc-math
- tc-operators
- tc-technical-analysis
- tc-advanced-pine
- tc-plots
- tc-visual-output
- tc-bar-coloring
- tc-alerts (only if alerts are explicitly reintroduced)

## Resume Gates (Post-Run)

1. Pine facade compile check
2. scripts/guards/pine-lint.sh on Nexus Pine file
3. scripts/guards/check-contamination.sh
4. scripts/guards/check-no-tv-force.sh
5. npm run build
6. pytest quality/test_functional.py -k nexus -q

## Scope Statement

This hold note captures planning/governance only. No active training or Pine behavior changes were performed as part of this preservation action.
