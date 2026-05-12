# Warbird Local DuckDB Modeling Workspace

This README documents the current V9 Warbird DuckDB path. The Nexus indicator
and old Warbird tuning work remain separate Optuna-owned surfaces; do not route
current V9 Core work through them.

## Layout

- `runner.py`
  Legacy/Nexus profile runner; not the current V9 Core training path.
- `warbird_optuna_hub.py`
  Legacy/Nexus dashboard support; not the current V9 Core training path.
- `vscode_doctor.py`
  VS Code extension and sidecar diagnostics.
- `runtime_health.py`
  One-command runtime-only pass/fail probe for retained dashboard support.
- `prune_runtime_logs.py`
  Archives stale child logs without touching active lanes.
- `indicator_registry.json`
  Registry of supported profile-adapter lanes.
- `workspaces/<indicator_key>/`
  Per-indicator canonical workspace home (DuckDB exports + manifests; legacy
  retained lanes may also carry their own study artifacts).

## Per-Indicator Workspace Contract

Each indicator or strategy gets one canonical workspace:

```text
scripts/duckdb_local/workspaces/<indicator_key>/
  exports/
    *.csv
    *.manifest.json
    *.profile.html
  trial_models/            # optional local model scratch for direct trainers
  experiments/
    <symbol_timeframe>/
      trial_models/
```

Rules:

- `warbird_pro` is the only active main chart indicator key and maps to
  **Warbird Pro V9** at `indicators/warbird-pro-v9.pine`.
- `warbird_pro_v9` is a separate Warbird Pro V9 experiment lane for ES-only
  ATR/risk exit modeling. Prep supports both `5m` and `15m` datasets; keep the
  canonical workspace at `workspaces/warbird_pro_v9/`, store exports under
  `exports/`, and keep timeframe-specific artifacts under `experiments/es_5m/`
  and `experiments/es_15m/`.
- `warbird_pro_core` is the Core AutoGluon card workspace. Prep supports ES
  `5m` and `15m` datasets with the same separation rule: dataset exports at the
  workspace root `exports/`, contract-specific training artifacts under
  `experiments/es_5m/` and `experiments/es_15m/`. Full V9 training launches
  directly through `scripts/ag/train_v9_locked.py`.
- Databento is an approved ES 5m/15m market-data supplier for training rows when
  manifests declare a Databento capture/source kind such as
  `DATABENTO_OHLCV_CSV`. Databento is not the Pine indicator and must not be
  labeled `TRADINGVIEW_INDICATOR_CSV`.
- `warbird_nexus_ml_rsi` is footprint-only: use the TradingView/Pine
  `request.footprint()` parquet + manifest. Do not use CSV exports, plain OHLCV
  parquet, Databento bars, or synthetic body/wick delta for that lane.

## Current Runtime Ops

- Current-runtime-only health: `python scripts/duckdb_local/runtime_health.py`
- Stale child-log archive (dry run): `python scripts/duckdb_local/prune_runtime_logs.py`
- Stale child-log archive (apply): `python scripts/duckdb_local/prune_runtime_logs.py --apply`
