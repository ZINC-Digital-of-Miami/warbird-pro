# V9 Core Smoke Verification Evidence — 2026-05-10

## Scope

This evidence closes the smoke-verification drift found after commit `7159633`.
It validates reproducible Core ETL smoke metrics only. It does not approve the
full 1y Core build, AG training, Core card body, hard-gate launch wiring, or
Optuna hub wiring.

## Commands

```bash
rm -rf artifacts/v9_core_smoke_may2025
python3 scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py \
  --symbol MES \
  --source data/mes_1m.parquet \
  --start 2025-05-01 \
  --end 2025-05-31 \
  --out-dir artifacts/v9_core_smoke_may2025 \
  --gate-mode smoke

python3 scripts/ag/report_v9_core_smoke.py \
  --csv artifacts/v9_core_smoke_may2025/mes_5m_core.csv \
  --manifest artifacts/v9_core_smoke_may2025/mes_5m_core.manifest.json \
  --out-json artifacts/v9_core_smoke_may2025/metrics.json

python3 scripts/ag/train_v9_locked.py \
  --csv artifacts/v9_core_smoke_may2025/mes_5m_core.csv \
  --validate-only \
  --smoke-ok
```

## Artifacts

- CSV: `artifacts/v9_core_smoke_may2025/mes_5m_core.csv`
- Manifest: `artifacts/v9_core_smoke_may2025/mes_5m_core.manifest.json`
- Metrics JSON: `artifacts/v9_core_smoke_may2025/metrics.json`

These are generated artifacts and remain under ignored `artifacts/`; this audit
records the reproducible command path and checksums.

## Metrics

```json
{
  "csv_sha256": "e867cf17e500eb653a2345ae1642266c34381245348a6817fae797aecf88bd4d",
  "manifest_sha256": "8a230d08f9abbb4bc90f62b481e88c44cb6db79d436c522a0c24908f7039bc29",
  "manifest_sha256_matches_csv": true,
  "row_count": 6000,
  "ts_first": "2025-05-01T00:00:00+00:00",
  "ts_last": "2025-05-30T20:55:00+00:00",
  "entry_long_count": 68,
  "entry_short_count": 0,
  "resolved_trade_count": 68,
  "winner_count": 62,
  "loss_count": 6,
  "winner_rate": 0.9117647058823529,
  "feature_count_locked": 52,
  "missing_features": [],
  "stale_columns": [],
  "manifest_warnings": [],
  "nonzero_counts": {
    "ml_xa_dxy_code": 5980,
    "ml_xa_dxy_diverge": 3111,
    "ml_xa_corr_nq": 2142,
    "ml_fp_delta_pct": 4603,
    "ml_delta_imbalance_pct": 4603,
    "ml_delta_acceleration": 4613,
    "ml_aggressor_pulse": 4603,
    "ml_cvd_div_bull": 486,
    "ml_cvd_div_bear": 714,
    "ml_absorption_candidate": 10,
    "ml_flush_candidate": 8,
    "ml_volume_spike_ratio": 4620,
    "ml_poc_shift": 4356
  }
}
```

## Order-Flow Threshold Evidence

`scripts/ag/report_v9_core_orderflow_distribution.py` now emits the
distribution proof for absorption/flush thresholds. May smoke showed absolute
delta max `51.86%`, so the old `55%` absorption and `65%` flush thresholds were
mathematically unable to fire in this month. The refactor uses `35%` delta with
the existing `1.5x` volume-spike and `0.75 ATR` range split:

```json
{
  "selected_recomputed_counts": {
    "absorption_count": 10,
    "flush_count": 8
  },
  "thresholds": {
    "absorption_delta_pct": 35.0,
    "flush_delta_pct": 35.0,
    "event_volume_spike": 1.5,
    "compressed_range_atr": 0.75
  }
}
```

## Gate Meaning

`--smoke-ok` is a small-window verification path. It confirms schema, stale
column bans, label construction, and at least one both-class smoke label set.
It does not replace the full `--validate-only` gate, which still enforces the
resolved-trade and chronological split floors.

## Deferred Work

| Item | Owner | Next Trigger |
|---|---|---|
| Full 1y Core ETL build | Codex, after Kirk approval to run full Core build | User asks to run the 1y Core build |
| Core card body + hard-gate launch wiring | Codex | Full 1y Core CSV passes full `--validate-only` gate |
| Optuna hub wiring | Codex | Core card body exists and hard-gate command is stable |
| Absorption/flush 1y confirmation | Codex | Full 1y Core build confirms or revises the 35%/1.5x/0.75 ATR smoke-tuned thresholds |
