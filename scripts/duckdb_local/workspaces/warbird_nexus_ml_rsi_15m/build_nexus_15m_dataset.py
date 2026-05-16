#!/usr/bin/env python3
"""Build and audit the isolated Nexus 15m training dataset.

This builder is Nexus-only. It ingests a TradingView chart export produced by
`indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine` and
containing OHLC plus the data-window/export-only `nexus_*` footprint evidence
columns. It does not import, modify, or write any Warbird V9 trainer/model
surface.

The output is a manifest-backed parquet dataset plus a pre-training label audit.
The audit is intentionally pre-training only: it reports label counts, split
boundaries, leakage exclusions, and feature availability so the heavy model can
be launched sequentially only after the labels are sane.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
WORKSPACE = REPO_ROOT / "scripts" / "duckdb_local" / "workspaces" / "warbird_nexus_ml_rsi_15m"
EXPORTS_DIR = WORKSPACE / "exports"
REPORTS_DIR = WORKSPACE / "reports"
DEFAULT_SOURCE_CSV = Path("/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_d464a.csv")
PINE_FILE = "indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine"
TRIGGER_FAMILY = "NEXUS_FOOTPRINT_DELTA"
CAPTURE_METHOD = "TV_NEXUS_15M_CHART_EXPORT"
DATASET_NAME = "nexus_15m_dataset"
LABEL_HORIZONS = (1, 3, 5, 10, 20)
VOLUME_EXPANSION_LOOKBACK = 96
VOLUME_EXPANSION_HORIZON = 12
PIVOT_SPAN = 3
PIVOT_LABEL_HORIZON = 12
EMBARGO_BARS = max(max(LABEL_HORIZONS), VOLUME_EXPANSION_HORIZON, PIVOT_LABEL_HORIZON) + 1

REQUIRED_COLUMNS: tuple[str, ...] = (
    "time", "open", "high", "low", "close",
    "VF Bull", "VF Bear", "VF Base", "NFE Oscillator", "Signal Line", "Cross Dot",
    "Tier 1 Exhaustion", "Delta Gas-Out", "Tier 2 Cross", "Momentum Fatigue",
    "OB Level", "Midline", "OS Level",
    "nexus_fp_available", "nexus_fp_quality_ok", "nexus_fp_bar_delta", "nexus_fp_total_volume",
    "nexus_norm_cum_delta", "nexus_delta_slope", "nexus_bar_delta_ratio", "nexus_delta_dir",
    "nexus_gasout_bull", "nexus_gasout_bear", "nexus_mode_minutes", "nexus_signal_tier",
    "nexus_pivot_span", "nexus_regime_score", "nexus_osc_momentum", "nexus_vf_calc",
    "nexus_div_reg_bull_raw", "nexus_div_reg_bear_raw", "nexus_div_hid_bull_raw", "nexus_div_hid_bear_raw",
    "nexus_div_reg_bull", "nexus_div_reg_bear", "nexus_div_hid_bull", "nexus_div_hid_bear",
)

VISIBLE_RENAME: dict[str, str] = {
    "VF Bull": "nexus_visible_vf_bull",
    "VF Bear": "nexus_visible_vf_bear",
    "VF Base": "nexus_visible_vf_base",
    "NFE Oscillator": "nexus_visible_nfe_oscillator",
    "Signal Line": "nexus_visible_signal_line",
    "Cross Dot": "nexus_visible_cross_dot",
    "Tier 1 Exhaustion": "nexus_visible_tier1_exhaustion",
    "Delta Gas-Out": "nexus_visible_delta_gasout",
    "Tier 2 Cross": "nexus_visible_tier2_cross",
    "Momentum Fatigue": "nexus_visible_momentum_fatigue",
    "OB Level": "nexus_visible_ob_level",
    "Midline": "nexus_visible_midline",
    "OS Level": "nexus_visible_os_level",
}

LEAKAGE_EXCLUSION_PATTERNS: tuple[str, ...] = (
    "label_",
    "future_",
    "fwd_",
    "split",
)

CORE_FEATURE_COLUMNS: tuple[str, ...] = (
    "open", "high", "low", "close",
    "nexus_visible_vf_bull", "nexus_visible_vf_bear", "nexus_visible_vf_base",
    "nexus_visible_nfe_oscillator", "nexus_visible_signal_line",
    "nexus_visible_tier1_exhaustion", "nexus_visible_delta_gasout",
    "nexus_visible_tier2_cross", "nexus_visible_momentum_fatigue",
    "nexus_visible_ob_level", "nexus_visible_midline", "nexus_visible_os_level",
    "nexus_fp_available", "nexus_fp_quality_ok", "nexus_fp_bar_delta", "nexus_fp_total_volume",
    "nexus_norm_cum_delta", "nexus_delta_slope", "nexus_bar_delta_ratio", "nexus_delta_dir",
    "nexus_gasout_bull", "nexus_gasout_bear", "nexus_mode_minutes", "nexus_signal_tier",
    "nexus_pivot_span", "nexus_regime_score", "nexus_osc_momentum", "nexus_vf_calc",
    "nexus_div_reg_bull_raw", "nexus_div_reg_bear_raw", "nexus_div_hid_bull_raw", "nexus_div_hid_bear_raw",
    "nexus_div_reg_bull", "nexus_div_reg_bear", "nexus_div_hid_bull", "nexus_div_hid_bear",
    "price_tr", "price_atr14", "price_er20", "price_range20_atr", "price_ret_1_atr",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_commit() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def clean_column_name(name: str) -> str:
    if name in VISIBLE_RENAME:
        return VISIBLE_RENAME[name]
    return name


def read_source_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    raw = pd.read_csv(path)
    missing = [col for col in REQUIRED_COLUMNS if col not in raw.columns]
    if missing:
        raise ValueError(f"Source CSV missing required Nexus 15m columns: {missing}")
    df = raw.loc[:, list(REQUIRED_COLUMNS)].rename(columns=clean_column_name).copy()
    df["ts"] = pd.to_datetime(df["time"], unit="s", utc=True)
    for col in df.columns:
        if col not in {"ts"}:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.sort_values("ts").reset_index(drop=True)
    return df


def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    prev_close = out["close"].shift(1)
    out["price_tr"] = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["price_atr14"] = out["price_tr"].rolling(14, min_periods=14).mean()
    out["price_ret_1"] = out["close"].diff()
    out["price_ret_1_atr"] = out["price_ret_1"] / out["price_atr14"]
    direction = (out["close"] - out["close"].shift(20)).abs()
    volatility = out["close"].diff().abs().rolling(20, min_periods=20).sum()
    out["price_er20"] = direction / volatility.replace(0, np.nan)
    range20 = out["high"].rolling(20, min_periods=20).max() - out["low"].rolling(20, min_periods=20).min()
    out["price_range20_atr"] = range20 / out["price_atr14"]
    return out


def add_labels(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    row_numbers = pd.Series(np.arange(len(out)), index=out.index)
    for horizon in LABEL_HORIZONS:
        complete_future = row_numbers <= (len(out) - horizon - 1)
        out[f"fwd_ret_{horizon}"] = out["close"].shift(-horizon) - out["close"]
        out[f"fwd_ret_atr_{horizon}"] = out[f"fwd_ret_{horizon}"] / out["price_atr14"]
        direction_label = pd.Series(pd.NA, index=out.index, dtype="object")
        valid = complete_future & out[f"fwd_ret_atr_{horizon}"].notna()
        direction_label.loc[valid] = "flat"
        direction_label.loc[valid & out[f"fwd_ret_atr_{horizon}"].ge(0.50)] = "up_0p5atr"
        direction_label.loc[valid & out[f"fwd_ret_atr_{horizon}"].le(-0.50)] = "down_0p5atr"
        out[f"label_dir_{horizon}b"] = direction_label
        move_0p5 = pd.Series(pd.NA, index=out.index, dtype="Int8")
        move_1p0 = pd.Series(pd.NA, index=out.index, dtype="Int8")
        move_0p5.loc[valid] = out.loc[valid, f"fwd_ret_atr_{horizon}"].abs().ge(0.50).astype("Int8")
        move_1p0.loc[valid] = out.loc[valid, f"fwd_ret_atr_{horizon}"].abs().ge(1.00).astype("Int8")
        out[f"label_abs_move_ge_0p5atr_{horizon}b"] = move_0p5
        out[f"label_abs_move_ge_1p0atr_{horizon}b"] = move_1p0

    vol_q = out["nexus_fp_total_volume"].rolling(VOLUME_EXPANSION_LOOKBACK, min_periods=30).quantile(0.75)
    tr_q = out["price_tr"].rolling(VOLUME_EXPANSION_LOOKBACK, min_periods=30).quantile(0.75)
    out["event_volume_expansion"] = (
        out["nexus_fp_quality_ok"].fillna(0).gt(0)
        & out["nexus_fp_total_volume"].gt(vol_q)
        & out["price_tr"].gt(tr_q)
    ).astype("Int8")
    future_expansion = pd.Series(False, index=out.index)
    for lead in range(1, VOLUME_EXPANSION_HORIZON + 1):
        future_expansion = future_expansion | out["event_volume_expansion"].shift(-lead).fillna(0).astype(bool)
    expansion_complete = row_numbers <= (len(out) - VOLUME_EXPANSION_HORIZON - 1)
    expansion_label = pd.Series(pd.NA, index=out.index, dtype="Int8")
    expansion_label.loc[expansion_complete] = future_expansion.loc[expansion_complete].astype("Int8")
    out[f"label_volume_expansion_next_{VOLUME_EXPANSION_HORIZON}b"] = expansion_label

    swing_low = pd.Series(False, index=out.index)
    swing_high = pd.Series(False, index=out.index)
    for idx in range(PIVOT_SPAN, len(out) - PIVOT_SPAN):
        lows = out["low"].iloc[idx - PIVOT_SPAN : idx + PIVOT_SPAN + 1]
        highs = out["high"].iloc[idx - PIVOT_SPAN : idx + PIVOT_SPAN + 1]
        if out["low"].iloc[idx] == lows.min() and int((lows == lows.min()).sum()) == 1:
            swing_low.iloc[idx] = True
        if out["high"].iloc[idx] == highs.max() and int((highs == highs.max()).sum()) == 1:
            swing_high.iloc[idx] = True
    out["event_swing_low"] = swing_low.astype("Int8")
    out["event_swing_high"] = swing_high.astype("Int8")
    future_low = pd.Series(False, index=out.index)
    future_high = pd.Series(False, index=out.index)
    for lead in range(1, PIVOT_LABEL_HORIZON + 1):
        future_low = future_low | out["event_swing_low"].shift(-lead).fillna(0).astype(bool)
        future_high = future_high | out["event_swing_high"].shift(-lead).fillna(0).astype(bool)
    pivot_complete = row_numbers <= (len(out) - PIVOT_LABEL_HORIZON - 1)
    low_label = pd.Series(pd.NA, index=out.index, dtype="Int8")
    high_label = pd.Series(pd.NA, index=out.index, dtype="Int8")
    low_label.loc[pivot_complete] = future_low.loc[pivot_complete].astype("Int8")
    high_label.loc[pivot_complete] = future_high.loc[pivot_complete].astype("Int8")
    out[f"label_swing_low_next_{PIVOT_LABEL_HORIZON}b"] = low_label
    out[f"label_swing_high_next_{PIVOT_LABEL_HORIZON}b"] = high_label
    return out


def assign_splits(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    split = np.full(len(out), "not_footprint_quality", dtype=object)
    eligible = np.flatnonzero(out["nexus_fp_quality_ok"].fillna(0).gt(0).to_numpy())
    n = len(eligible)
    train_end = int(n * 0.70)
    val_start = min(train_end + EMBARGO_BARS, n)
    val_end = int(n * 0.85)
    test_start = min(val_end + EMBARGO_BARS, n)
    split[eligible[:train_end]] = "train"
    split[eligible[train_end:val_start]] = "embargo_train_val"
    split[eligible[val_start:val_end]] = "validation"
    split[eligible[val_end:test_start]] = "embargo_val_test"
    split[eligible[test_start:]] = "test"
    out["split"] = split
    return out


def validate_dataset(df: pd.DataFrame) -> dict[str, Any]:
    intervals = df["ts"].diff().dt.total_seconds().dropna()
    if not df["ts"].is_monotonic_increasing:
        raise ValueError("timestamps are not monotonic increasing")
    if int(df["ts"].duplicated().sum()) != 0:
        raise ValueError("duplicate timestamps in source export")
    mode_values = sorted(float(v) for v in df["nexus_mode_minutes"].dropna().unique())
    if mode_values != [15.0]:
        raise ValueError(f"expected Nexus mode 15m export, got {mode_values}")
    missing_features = [col for col in CORE_FEATURE_COLUMNS if col not in df.columns]
    if missing_features:
        raise ValueError(f"missing feature columns after build: {missing_features}")
    return {
        "row_count": int(len(df)),
        "date_start": df["ts"].iloc[0].isoformat(),
        "date_end": df["ts"].iloc[-1].isoformat(),
        "duplicate_timestamps": int(df["ts"].duplicated().sum()),
        "interval_900s_count": int((intervals == 900).sum()),
        "non_900s_gap_count": int((intervals != 900).sum()),
        "largest_gap_minutes": float(intervals.max() / 60.0) if len(intervals) else math.nan,
        "nexus_mode_minutes": mode_values,
        "fp_available_rows": int(df["nexus_fp_available"].fillna(0).gt(0).sum()),
        "fp_quality_rows": int(df["nexus_fp_quality_ok"].fillna(0).gt(0).sum()),
        "fp_quality_ratio": float(df["nexus_fp_quality_ok"].fillna(0).gt(0).mean()),
        "pivot_span_values": sorted(float(v) for v in df["nexus_pivot_span"].dropna().unique()),
    }


def label_counts(df: pd.DataFrame) -> dict[str, Any]:
    labels = [col for col in df.columns if col.startswith("label_")]
    counts: dict[str, Any] = {}
    for label in labels:
        vc = df[label].value_counts(dropna=False).sort_index()
        counts[label] = {str(k): int(v) for k, v in vc.items()}
    return counts


def split_summary(df: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for split_name, group in df.groupby("split", sort=False):
        item: dict[str, Any] = {
            "rows": int(len(group)),
            "fp_quality_rows": int(group["nexus_fp_quality_ok"].fillna(0).gt(0).sum()),
        }
        if len(group):
            item["date_start"] = group["ts"].iloc[0].isoformat()
            item["date_end"] = group["ts"].iloc[-1].isoformat()
        summary[str(split_name)] = item
    return summary


def feature_availability(df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    fpq = df["nexus_fp_quality_ok"].fillna(0).gt(0)
    for col in CORE_FEATURE_COLUMNS:
        series = df[col]
        rows.append(
            {
                "feature": col,
                "non_null": int(series.notna().sum()),
                "non_null_ratio": float(series.notna().mean()),
                "non_null_on_fp_quality": int(series[fpq].notna().sum()),
                "non_null_ratio_on_fp_quality": float(series[fpq].notna().mean()) if int(fpq.sum()) else math.nan,
                "non_zero": int(series.fillna(0).astype(float).abs().gt(1e-12).sum()) if pd.api.types.is_numeric_dtype(series) else None,
            }
        )
    return rows


def leakage_exclusions(df: pd.DataFrame) -> list[str]:
    exclusions: list[str] = ["time", "ts"]
    for col in df.columns:
        if col in exclusions:
            continue
        if any(col.startswith(pattern) for pattern in LEAKAGE_EXCLUSION_PATTERNS):
            exclusions.append(col)
        elif col.startswith("event_"):
            exclusions.append(col)
    return sorted(exclusions)


def write_markdown_report(audit: dict[str, Any], path: Path) -> None:
    lines: list[str] = []
    lines.append("# Nexus 15m Pre-Training Label Audit — 2026-05-15\n")
    lines.append("## Source And Scope\n")
    lines.append(f"- Source CSV: `{audit['source_csv']}`\n")
    lines.append(f"- Source SHA256: `{audit['source_sha256']}`\n")
    lines.append(f"- Dataset parquet: `{audit['dataset_parquet']}`\n")
    lines.append(f"- Trigger family: `{TRIGGER_FAMILY}`\n")
    lines.append("- Scope: Nexus-only 15m dataset. No V9 Pine/trainer/export/model files are touched.\n")
    lines.append("\n## Dataset Validation\n")
    for key, value in audit["validation"].items():
        lines.append(f"- `{key}`: `{value}`\n")
    lines.append("\n## Chronological Split Plan\n")
    lines.append(f"- Embargo bars: `{EMBARGO_BARS}`\n")
    lines.append("| Split | Rows | FP quality rows | Date start | Date end |\n")
    lines.append("| --- | ---: | ---: | --- | --- |\n")
    for split_name, item in audit["splits"].items():
        lines.append(
            f"| {split_name} | {item['rows']} | {item['fp_quality_rows']} | {item.get('date_start', '')} | {item.get('date_end', '')} |\n"
        )
    lines.append("\n## Label Counts\n")
    for label, counts in audit["label_counts"].items():
        lines.append(f"### `{label}`\n")
        lines.append("| Class/value | Rows |\n| --- | ---: |\n")
        for value, count in counts.items():
            lines.append(f"| {value} | {count} |\n")
    lines.append("\n## Leakage Exclusions\n")
    lines.append("These columns are excluded from feature training inputs because they are timestamps, future-looking labels/returns, split metadata, or event labels.\n\n")
    for col in audit["leakage_exclusions"]:
        lines.append(f"- `{col}`\n")
    lines.append("\n## Feature Availability Summary\n")
    lines.append("| Feature | Non-null | Non-null % | Non-null on FP quality | FP quality non-null % | Non-zero |\n")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |\n")
    for row in audit["feature_availability"]:
        lines.append(
            f"| {row['feature']} | {row['non_null']} | {row['non_null_ratio']:.4f} | {row['non_null_on_fp_quality']} | {row['non_null_ratio_on_fp_quality']:.4f} | {row['non_zero']} |\n"
        )
    lines.append("\n## Training Readiness Gate\n")
    lines.append("- `label_volume_expansion_next_12b` is the preferred first heavy-model target because the diagnostics showed mild precursor value and enough positives for chronological splits.\n")
    lines.append("- Pivot-proximity labels are viable secondary targets, but divergence-specific labels are too sparse until confirmed-divergence examples are expanded or modeled as auxiliary features.\n")
    lines.append("- Directional-return labels are available for side models, but direct IC was weak; do not use immediate directional return as the first primary target.\n")
    lines.append("- Next step is a Nexus-only training config using this dataset and these split boundaries; no heavy training has been run by this audit.\n")
    path.write_text("".join(lines))


def build(source_csv: Path) -> dict[str, Any]:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df = read_source_csv(source_csv)
    df = add_price_features(df)
    df = add_labels(df)
    df = assign_splits(df)
    validation = validate_dataset(df)
    dataset_path = EXPORTS_DIR / f"{DATASET_NAME}.parquet"
    csv_path = EXPORTS_DIR / f"{DATASET_NAME}.csv"
    manifest_path = EXPORTS_DIR / f"{DATASET_NAME}.manifest.json"
    audit_json_path = REPORTS_DIR / "pretrain_label_audit.json"
    audit_md_path = REPORTS_DIR / "pretrain_label_audit.md"
    df.to_parquet(dataset_path, index=False)
    df.to_csv(csv_path, index=False)
    manifest = {
        "dataset_name": DATASET_NAME,
        "capture_method": CAPTURE_METHOD,
        "trigger_family": TRIGGER_FAMILY,
        "indicator_file": PINE_FILE,
        "symbol": "MES",
        "timeframe": "15m",
        "source_csv": str(source_csv),
        "source_sha256": sha256_file(source_csv),
        "dataset_parquet": str(dataset_path),
        "dataset_sha256": sha256_file(dataset_path),
        "dataset_csv": str(csv_path),
        "row_count": validation["row_count"],
        "date_start": validation["date_start"],
        "date_end": validation["date_end"],
        "fp_quality_rows": validation["fp_quality_rows"],
        "fp_quality_ratio": validation["fp_quality_ratio"],
        "feature_columns": list(CORE_FEATURE_COLUMNS),
        "label_columns": [col for col in df.columns if col.startswith("label_")],
        "event_columns": [col for col in df.columns if col.startswith("event_")],
        "embargo_bars": EMBARGO_BARS,
        "label_horizons": list(LABEL_HORIZONS),
        "build_utc": datetime.now(timezone.utc).isoformat(),
        "repo_commit": repo_commit(),
        "notes": "Isolated Nexus 15m dataset from TradingView/Pine footprint evidence export. No V9 artifacts used.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    audit = {
        "source_csv": str(source_csv),
        "source_sha256": manifest["source_sha256"],
        "dataset_parquet": str(dataset_path),
        "dataset_sha256": manifest["dataset_sha256"],
        "manifest": str(manifest_path),
        "validation": validation,
        "splits": split_summary(df),
        "label_counts": label_counts(df),
        "leakage_exclusions": leakage_exclusions(df),
        "feature_availability": feature_availability(df),
        "preferred_first_target": f"label_volume_expansion_next_{VOLUME_EXPANSION_HORIZON}b",
        "secondary_targets": [
            f"label_swing_low_next_{PIVOT_LABEL_HORIZON}b",
            f"label_swing_high_next_{PIVOT_LABEL_HORIZON}b",
            "label_dir_3b",
            "label_dir_5b",
            "label_dir_10b",
            "label_dir_20b",
        ],
        "training_started": False,
    }
    audit_json_path.write_text(json.dumps(audit, indent=2, default=str))
    write_markdown_report(audit, audit_md_path)
    return {"manifest": manifest, "audit": audit, "dataset_path": str(dataset_path), "audit_md": str(audit_md_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-csv", type=Path, default=DEFAULT_SOURCE_CSV)
    args = parser.parse_args()
    result = build(args.source_csv)
    print(json.dumps({
        "dataset_path": result["dataset_path"],
        "manifest": result["audit"]["manifest"],
        "audit_md": result["audit_md"],
        "row_count": result["manifest"]["row_count"],
        "fp_quality_rows": result["manifest"]["fp_quality_rows"],
        "preferred_first_target": result["audit"]["preferred_first_target"],
        "training_started": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
