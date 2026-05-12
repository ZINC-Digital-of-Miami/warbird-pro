#!/usr/bin/env python3
"""Report V9 Core order-flow distributions and absorption/flush threshold counts.

This is a read-only diagnostic. It does not rebuild the CSV or train a model.
Use it after `build_core_dataset.py` to prove whether the current
absorption/flush thresholds actually fire on the selected window.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.duckdb_local.workspaces.warbird_pro_core.build_core_dataset import (
    ORDERFLOW_ABSORPTION_DELTA_PCT,
    ORDERFLOW_COMPRESSED_RANGE_ATR,
    ORDERFLOW_EVENT_VOLUME_SPIKE,
    ORDERFLOW_FLUSH_DELTA_PCT,
)

REQUIRED_COLUMNS = [
    "high",
    "low",
    "ml_atr14",
    "ml_fp_delta_pct",
    "ml_volume_spike_ratio",
    "ml_poc_shift",
    "ml_absorption_candidate",
    "ml_flush_candidate",
]

DELTA_GRID = [25.0, 35.0, 45.0, 55.0, 65.0]
VOLUME_GRID = [1.0, 1.25, 1.5, 2.0]
PERCENTILES = [0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0]


def quantiles(values: pd.Series) -> dict[str, float]:
    numeric = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if numeric.empty:
        return {}
    qs = numeric.quantile(PERCENTILES)
    return {f"p{int(p * 100):02d}": float(qs.loc[p]) for p in PERCENTILES}


def nonzero_count(values: pd.Series) -> int:
    return int((pd.to_numeric(values, errors="coerce").fillna(0.0).abs() > 0).sum())


def candidate_counts(abs_delta: pd.Series, volume_spike: pd.Series, range_atr: pd.Series, delta_threshold: float, volume_threshold: float) -> dict[str, int]:
    absorption = (abs_delta >= delta_threshold) & (volume_spike >= volume_threshold) & (range_atr <= ORDERFLOW_COMPRESSED_RANGE_ATR)
    flush = (abs_delta >= delta_threshold) & (volume_spike >= volume_threshold) & (range_atr > ORDERFLOW_COMPRESSED_RANGE_ATR)
    return {
        "delta_threshold": int(delta_threshold) if float(delta_threshold).is_integer() else float(delta_threshold),
        "volume_spike_threshold": float(volume_threshold),
        "absorption_count": int(absorption.sum()),
        "flush_count": int(flush.sum()),
    }


def build_report(csv_path: Path, manifest_path: Path | None) -> dict[str, Any]:
    df = pd.read_csv(csv_path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise RuntimeError(f"Order-flow distribution CSV missing columns: {missing}")

    delta = pd.to_numeric(df["ml_fp_delta_pct"], errors="coerce").fillna(0.0)
    abs_delta = delta.abs()
    volume_spike = pd.to_numeric(df["ml_volume_spike_ratio"], errors="coerce").fillna(0.0)
    atr = pd.to_numeric(df["ml_atr14"], errors="coerce").replace(0, np.nan)
    range_atr = ((pd.to_numeric(df["high"], errors="coerce") - pd.to_numeric(df["low"], errors="coerce")) / atr)
    range_atr = range_atr.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    grid = [
        candidate_counts(abs_delta, volume_spike, range_atr, delta_threshold, volume_threshold)
        for delta_threshold in DELTA_GRID
        for volume_threshold in VOLUME_GRID
    ]
    selected_abs = (abs_delta >= ORDERFLOW_ABSORPTION_DELTA_PCT) & (volume_spike >= ORDERFLOW_EVENT_VOLUME_SPIKE) & (range_atr <= ORDERFLOW_COMPRESSED_RANGE_ATR)
    selected_flush = (abs_delta >= ORDERFLOW_FLUSH_DELTA_PCT) & (volume_spike >= ORDERFLOW_EVENT_VOLUME_SPIKE) & (range_atr > ORDERFLOW_COMPRESSED_RANGE_ATR)

    manifest = {}
    if manifest_path is not None:
        if not manifest_path.exists():
            raise RuntimeError(f"Manifest not found: {manifest_path}")
        manifest = json.loads(manifest_path.read_text())

    return {
        "csv_path": str(csv_path),
        "manifest_path": str(manifest_path) if manifest_path else None,
        "row_count": int(len(df)),
        "thresholds": {
            "absorption_delta_pct": ORDERFLOW_ABSORPTION_DELTA_PCT,
            "flush_delta_pct": ORDERFLOW_FLUSH_DELTA_PCT,
            "event_volume_spike": ORDERFLOW_EVENT_VOLUME_SPIKE,
            "compressed_range_atr": ORDERFLOW_COMPRESSED_RANGE_ATR,
        },
        "manifest_thresholds": manifest.get("orderflow_candidate_thresholds"),
        "nonzero_counts": {
            "ml_fp_delta_pct": nonzero_count(df["ml_fp_delta_pct"]),
            "ml_volume_spike_ratio": nonzero_count(df["ml_volume_spike_ratio"]),
            "ml_poc_shift": nonzero_count(df["ml_poc_shift"]),
            "ml_absorption_candidate": nonzero_count(df["ml_absorption_candidate"]),
            "ml_flush_candidate": nonzero_count(df["ml_flush_candidate"]),
        },
        "distributions": {
            "abs_delta_pct": quantiles(abs_delta),
            "volume_spike_ratio": quantiles(volume_spike),
            "range_atr": quantiles(range_atr),
            "poc_shift_abs": quantiles(pd.to_numeric(df["ml_poc_shift"], errors="coerce").fillna(0.0).abs()),
        },
        "selected_recomputed_counts": {
            "absorption_count": int(selected_abs.sum()),
            "flush_count": int(selected_flush.sum()),
        },
        "threshold_grid_counts": grid,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Report V9 Core order-flow threshold distributions")
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
    args = parser.parse_args()

    if not args.csv.exists():
        raise SystemExit(f"CSV not found: {args.csv}")

    report = build_report(args.csv, args.manifest)
    payload = json.dumps(report, indent=2, sort_keys=True)
    print(payload)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(payload + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
