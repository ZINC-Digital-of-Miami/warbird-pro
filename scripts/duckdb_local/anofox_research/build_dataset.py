#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from common import (
    DEFAULT_CORE_EXPORT,
    DEFAULT_CORE_MANIFEST,
    DEFAULT_DATASET_CSV,
    DEFAULT_DATASET_MANIFEST,
    DEFAULT_STUDY_DB,
    read_json,
    sha256_file,
    write_json,
)


REQUIRED_COLUMNS = {"ts", "open", "high", "low", "close"}


def _as_trigger(series: pd.Series | None, size: int) -> pd.Series:
    if series is None:
        return pd.Series(np.zeros(size, dtype=bool))
    return series.fillna(0).astype(float).ne(0)


def build_dataset(
    source_csv: Path,
    source_manifest: Path,
    output_csv: Path,
    output_manifest: Path,
    study_db: Path,
    horizon_bars: int,
) -> dict:
    if not source_csv.exists():
        raise FileNotFoundError(f"source export not found: {source_csv}")

    df = pd.read_csv(source_csv)
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"source export missing required columns: {missing}")

    df["ts"] = pd.to_datetime(df["ts"], utc=True, errors="coerce").dt.tz_convert(None)
    df = df.dropna(subset=["ts", "close"]).sort_values("ts").drop_duplicates("ts")
    df = df.reset_index(drop=True)

    prev_close = df["close"].shift(1)
    true_range = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    fallback_atr14 = true_range.rolling(14, min_periods=1).mean()
    atr14 = df["ml_atr14"] if "ml_atr14" in df.columns else fallback_atr14
    atr14 = atr14.astype(float).where(atr14.astype(float).gt(0), fallback_atr14)

    long_trigger = _as_trigger(df.get("ml_entry_long_trigger"), len(df))
    short_trigger = _as_trigger(df.get("ml_entry_short_trigger"), len(df))
    entry_dir = np.select(
        [long_trigger & ~short_trigger, short_trigger & ~long_trigger],
        [1, -1],
        default=0,
    )

    ma_fast_dist = df["ml_ma_fast_dist_atr"] if "ml_ma_fast_dist_atr" in df.columns else 0.0
    ma_slow_dist = df["ml_ma_slow_dist_atr"] if "ml_ma_slow_dist_atr" in df.columns else 0.0
    ma_spread_proxy = pd.Series(ma_fast_dist).astype(float) - pd.Series(ma_slow_dist).astype(float)

    out = pd.DataFrame(
        {
            "ts": df["ts"],
            "open": df["open"].astype(float),
            "high": df["high"].astype(float),
            "low": df["low"].astype(float),
            "close": df["close"].astype(float),
            "volume": df["volume"].astype(float) if "volume" in df.columns else np.nan,
            "bar_return_points": df["close"].astype(float).diff(),
            "bar_return_bp": np.log(df["close"].astype(float) / prev_close.astype(float)) * 10000.0,
            "atr14_points": atr14.astype(float),
            "atr_pct_bp": atr14.astype(float) / df["close"].astype(float) * 10000.0,
            "ma_spread_proxy_atr": ma_spread_proxy,
            "entry_dir": entry_dir.astype(int),
            "entry_long": long_trigger.astype(int),
            "entry_short": short_trigger.astype(int),
            "future_return_points": df["close"].shift(-horizon_bars).astype(float) - df["close"].astype(float),
            "future_return_bp": (
                (df["close"].shift(-horizon_bars).astype(float) / df["close"].astype(float)) - 1.0
            )
            * 10000.0,
            "future_return_sign": np.sign(df["close"].shift(-horizon_bars).astype(float) - df["close"].astype(float)),
            "future_atr_pct_bp_mean": (
                atr14.astype(float).shift(-1).rolling(horizon_bars, min_periods=horizon_bars).mean().shift(-(horizon_bars - 1))
                / df["close"].astype(float)
                * 10000.0
            ),
        }
    )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False)

    study_db.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(study_db))
    con.register("anofox_dataset_df", out)
    con.execute("CREATE OR REPLACE TABLE anofox_es_15m_context AS SELECT * FROM anofox_dataset_df")
    con.close()

    source_info = read_json(source_manifest)
    payload = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "lane": "anofox_research",
        "purpose": "forecasting sidecar for V9 regime/context signals; not the V9 trainer",
        "source_csv": str(source_csv),
        "source_manifest": str(source_manifest),
        "source_sha256": sha256_file(source_csv),
        "source_kind": source_info.get("source_kind"),
        "source_trigger_family": source_info.get("trigger_family"),
        "source_symbol": source_info.get("symbol"),
        "source_timeframe": source_info.get("timeframe"),
        "source_rows_declared": source_info.get("row_count"),
        "source_ts_first": source_info.get("ts_first"),
        "source_ts_last": source_info.get("ts_last"),
        "horizon_bars": horizon_bars,
        "row_count": int(len(out)),
        "ts_first": out["ts"].min().isoformat(),
        "ts_last": out["ts"].max().isoformat(),
        "entry_long_count": int(out["entry_long"].sum()),
        "entry_short_count": int(out["entry_short"].sum()),
        "output_csv": str(output_csv),
        "output_sha256": sha256_file(output_csv),
        "study_db": str(study_db),
        "duckdb_table": "anofox_es_15m_context",
        "target_series": ["bar_return_points", "atr_pct_bp"],
        "context_series": ["ma_spread_proxy_atr"],
    }
    write_json(output_manifest, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Build AnoFox 15m context-signal dataset from V9 core export.")
    parser.add_argument("--source-csv", default=DEFAULT_CORE_EXPORT, type=Path)
    parser.add_argument("--source-manifest", default=DEFAULT_CORE_MANIFEST, type=Path)
    parser.add_argument("--output-csv", default=DEFAULT_DATASET_CSV, type=Path)
    parser.add_argument("--output-manifest", default=DEFAULT_DATASET_MANIFEST, type=Path)
    parser.add_argument("--study-db", default=DEFAULT_STUDY_DB, type=Path)
    parser.add_argument("--horizon-bars", default=12, type=int)
    args = parser.parse_args()

    payload = build_dataset(
        source_csv=args.source_csv,
        source_manifest=args.source_manifest,
        output_csv=args.output_csv,
        output_manifest=args.output_manifest,
        study_db=args.study_db,
        horizon_bars=args.horizon_bars,
    )
    print(
        "PASS: built anofox dataset "
        f"rows={payload['row_count']} entries=L{payload['entry_long_count']}/S{payload['entry_short_count']}"
    )
    print(f"output_csv={payload['output_csv']}")
    print(f"output_manifest={args.output_manifest}")


if __name__ == "__main__":
    main()
