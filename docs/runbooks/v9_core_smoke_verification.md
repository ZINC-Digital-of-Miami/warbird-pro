# V9 Core Smoke Verification

This runbook is the reproducible evidence path for small Core ETL smoke
windows. It is not a full 1y Core build, not AG training, and not a champion
gate.

> **2026-05-21 status:** This smoke packet is historical evidence only. It
> predates the active V9/Core parity surface (`ML_FEATURES=75`,
> `MODEL_FEATURES=81`), the NQ+6E-only Pine cross-asset contract, and the
> removal of candlestick/Risk Mode/DXY/ZN/VIX Pine feature surfaces. Do not use
> the May 2025 MES smoke counts below as current acceptance evidence; run a new
> ES 15m/5m Core smoke with the current manifest contract before citing metrics.

## Build Smoke CSV

```bash
rm -rf artifacts/v9_core_smoke_may2025
python3 scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py \
  --symbol MES \
  --source data/mes_1m.parquet \
  --start 2025-05-01 \
  --end 2025-05-31 \
  --out-dir artifacts/v9_core_smoke_may2025 \
  --gate-mode smoke
```

Expected artifact paths:

- `artifacts/v9_core_smoke_may2025/mes_5m_core.csv`
- `artifacts/v9_core_smoke_may2025/mes_5m_core.manifest.json`

## Report Exact Metrics

```bash
python3 scripts/ag/report_v9_core_smoke.py \
  --csv artifacts/v9_core_smoke_may2025/mes_5m_core.csv \
  --manifest artifacts/v9_core_smoke_may2025/mes_5m_core.manifest.json \
  --out-json artifacts/v9_core_smoke_may2025/metrics.json
```

Use the emitted JSON as the source of truth for row counts, entry counts,
feature nonzero counts, label counts, and CSV/manifest checksums. Do not cite
chat-transcribed smoke metrics without this JSON output.

Legacy reference run from 2026-05-10 after the order-flow threshold refactor
(superseded for active V9/Core parity):

- CSV SHA256: `e867cf17e500eb653a2345ae1642266c34381245348a6817fae797aecf88bd4d`
- Manifest SHA256: `8a230d08f9abbb4bc90f62b481e88c44cb6db79d436c522a0c24908f7039bc29`
- Rows: `6000`
- Entries: `68` long, `0` short
- Resolved labels: `68` total, `62` winners, `6` losses
- Locked features: `52`
- Nonzero counts: DXY code `5980`, DXY divergence `3111`, fp delta `4603`,
  delta acceleration `4613`, aggressor pulse `4603`, CVD bull `486`, CVD bear
  `714`, absorption `10`, flush `8`, volume spike `4620`, POC shift `4356`

## Order-Flow Threshold Distribution

```bash
python3 scripts/ag/report_v9_core_orderflow_distribution.py \
  --csv artifacts/v9_core_smoke_may2025/mes_5m_core.csv \
  --manifest artifacts/v9_core_smoke_may2025/mes_5m_core.manifest.json \
  --out-json artifacts/v9_core_smoke_may2025/orderflow_distribution.json
```

The current candidate thresholds are:

- Absorption delta: `35%`
- Flush delta: `35%`
- Event volume spike: `1.5x`
- Compressed range split: `0.75 ATR`

May smoke distribution evidence: absolute delta max was `51.86%`, so the old
`55%`/`65%` thresholds could not fire in this month. The `35%` + `1.5x` grid
point produces `10` absorption candidates and `8` flush candidates.

## Smoke Label Validation

```bash
python3 scripts/ag/train_v9_locked.py \
  --csv artifacts/v9_core_smoke_may2025/mes_5m_core.csv \
  --validate-only \
  --smoke-ok
```

`--smoke-ok` is only for small smoke windows. Full Core validation still uses
`--validate-only` without `--smoke-ok`, which preserves the >=200 resolved-trade
and chronological split gates.
