#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from common import (
    DEFAULT_EXTERNAL_CONTEXT_CSV,
    DEFAULT_EXTERNAL_CONTEXT_MANIFEST,
    DEFAULT_EXTERNAL_FRED_MACRO,
    DEFAULT_EXTERNAL_FUTURES_1H,
    DEFAULT_STUDY_DB,
    sha256_file,
    write_json,
)


DEFAULT_START = "2020-01-01"
DEFAULT_END = "2025-12-15"
DEFAULT_CORE_SYMBOLS = "ES,NQ,ZN,6E,HG,YM,RTY,CL,GC,ZB,ZF,ZT,6J,6B,6A,6C,SI,NG,HO,RB"
FRED_LEVEL_COLUMNS = [
    "fed_funds",
    "treasury_10y",
    "treasury_2y",
    "yield_curve_10y2y",
    "dxy",
    "vix",
    "stlfsi4",
    "nfci",
    "wti_crude",
]


def _safe_name(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z_]+", "_", value).strip("_")


def _symbol_column(symbol: str, suffix: str) -> str:
    return f"sym_{_safe_name(symbol).lower()}_{suffix}"


def _parse_symbols(raw: str, futures_path: Path, start: str, end: str, min_coverage: float) -> list[str]:
    if raw.strip().lower() != "all":
        return [item.strip().upper() for item in raw.split(",") if item.strip()]

    con = duckdb.connect(":memory:")
    total_hours = con.execute(
        """
        SELECT count(DISTINCT ts_event)
        FROM read_parquet(?)
        WHERE ts_event >= CAST(? AS TIMESTAMP)
          AND ts_event <= CAST(? AS TIMESTAMP)
        """,
        [str(futures_path), start, end],
    ).fetchone()[0]
    if not total_hours:
        raise ValueError(f"no futures rows found in requested window {start}..{end}")

    rows = con.execute(
        """
        SELECT symbol, count(*) AS rows
        FROM read_parquet(?)
        WHERE ts_event >= CAST(? AS TIMESTAMP)
          AND ts_event <= CAST(? AS TIMESTAMP)
        GROUP BY symbol
        HAVING count(*) >= ?
        ORDER BY symbol
        """,
        [str(futures_path), start, end, int(total_hours * min_coverage)],
    ).fetchall()
    symbols = [str(symbol).upper() for symbol, _rows in rows]
    if "ES" not in symbols:
        raise ValueError("symbol discovery did not find ES; cannot build ES-target context")
    return symbols


def _load_futures(futures_path: Path, symbols: list[str], start: str, end: str) -> pd.DataFrame:
    if not futures_path.exists():
        raise FileNotFoundError(f"external futures parquet not found: {futures_path}")

    con = duckdb.connect(":memory:")
    rows = con.execute(
        """
        SELECT
          CAST(ts_event AS TIMESTAMP) AS ts,
          upper(symbol) AS symbol,
          CAST(open AS DOUBLE) AS open,
          CAST(high AS DOUBLE) AS high,
          CAST(low AS DOUBLE) AS low,
          CAST(close AS DOUBLE) AS close,
          CAST(volume AS DOUBLE) AS volume,
          CAST(open_interest AS DOUBLE) AS open_interest
        FROM read_parquet(?)
        WHERE ts_event >= CAST(? AS TIMESTAMP)
          AND ts_event <= CAST(? AS TIMESTAMP)
          AND upper(symbol) IN (SELECT upper(unnest(?)))
        ORDER BY ts, symbol
        """,
        [str(futures_path), start, end, symbols],
    ).fetchdf()
    if rows.empty:
        raise ValueError(f"no futures rows loaded from {futures_path}")
    rows["ts"] = pd.to_datetime(rows["ts"], errors="coerce")
    rows = rows.dropna(subset=["ts", "symbol", "close"]).sort_values(["symbol", "ts"])
    return rows


def _build_futures_wide(rows: pd.DataFrame, symbols: list[str]) -> pd.DataFrame:
    base = rows.pivot(index="ts", columns="symbol", values="close").sort_index()
    volume = rows.pivot(index="ts", columns="symbol", values="volume").sort_index()
    high = rows.pivot(index="ts", columns="symbol", values="high").sort_index()
    low = rows.pivot(index="ts", columns="symbol", values="low").sort_index()

    columns: dict[str, pd.Series] = {}
    for symbol in symbols:
        if symbol not in base.columns:
            continue
        close = base[symbol].astype(float).where(base[symbol].astype(float).gt(0.0), np.nan)
        columns[_symbol_column(symbol, "close")] = close
        columns[_symbol_column(symbol, "ret_1h_bp")] = np.log(close / close.shift(1)) * 10000.0
        columns[_symbol_column(symbol, "ret_12h_bp")] = np.log(close / close.shift(12)) * 10000.0
        columns[_symbol_column(symbol, "range_bp")] = (high[symbol].astype(float) - low[symbol].astype(float)) / close * 10000.0
        if symbol in volume.columns:
            vol = volume[symbol].astype(float)
            vol_mean = vol.rolling(48, min_periods=12).mean()
            vol_std = vol.rolling(48, min_periods=12).std()
            columns[_symbol_column(symbol, "vol_z48")] = (vol - vol_mean) / vol_std.replace(0.0, np.nan)

    out = pd.DataFrame(columns, index=base.index).reset_index()
    out["ts"] = pd.to_datetime(out["ts"])
    return out


def _add_fred_context(df: pd.DataFrame, fred_path: Path) -> tuple[pd.DataFrame, list[str]]:
    if not fred_path.exists():
        raise FileNotFoundError(f"FRED macro parquet not found: {fred_path}")
    fred = pd.read_parquet(fred_path)
    if "date" not in fred.columns:
        raise ValueError(f"FRED macro parquet missing date column: {fred_path}")

    present = [column for column in FRED_LEVEL_COLUMNS if column in fred.columns]
    fred = fred[["date", *present]].copy()
    fred["date"] = pd.to_datetime(fred["date"], errors="coerce")
    fred = fred.dropna(subset=["date"]).sort_values("date")
    for column in present:
        fred[f"fred_{column}"] = pd.to_numeric(fred[column], errors="coerce")
        fred[f"fred_{column}_d1"] = fred[f"fred_{column}"].diff()
    fred = fred.drop(columns=present)

    out = df.copy()
    out["date"] = pd.to_datetime(out["ts"]).dt.normalize()
    out = out.merge(fred, on="date", how="left")
    fred_columns = [column for column in out.columns if column.startswith("fred_")]
    out[fred_columns] = out[fred_columns].ffill()
    return out.drop(columns=["date"]), fred_columns


def build_external_context(
    futures_path: Path,
    fred_path: Path,
    output_csv: Path,
    output_manifest: Path,
    study_db: Path,
    symbols_raw: str,
    start: str,
    end: str,
    horizon_hours: int,
    min_coverage: float,
) -> dict:
    symbols = _parse_symbols(symbols_raw, futures_path, start, end, min_coverage)
    rows = _load_futures(futures_path, symbols, start, end)
    symbol_coverage = (
        rows.groupby("symbol")
        .agg(rows=("close", "size"), ts_first=("ts", "min"), ts_last=("ts", "max"))
        .reset_index()
    )

    out = _build_futures_wide(rows, symbols)
    out, fred_columns = _add_fred_context(out, fred_path)

    es_close = _symbol_column("ES", "close")
    es_ret = _symbol_column("ES", "ret_1h_bp")
    if es_close not in out.columns or es_ret not in out.columns:
        raise ValueError("external context requires ES close and ES return columns")

    out = out.dropna(subset=[es_close]).sort_values("ts").reset_index(drop=True)
    out["future_es_return_bp"] = out[es_ret].shift(-1).rolling(horizon_hours, min_periods=horizon_hours).sum().shift(
        -(horizon_hours - 1)
    )
    out["future_es_return_sign"] = np.sign(out["future_es_return_bp"])

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False)

    study_db.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(study_db))
    con.register("external_context_df", out)
    con.execute("CREATE OR REPLACE TABLE anofox_external_1h_context AS SELECT * FROM external_context_df")
    con.close()

    payload = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "lane": "anofox_research_external",
        "purpose": "external 1h forecasting sidecar; not active V9 trainer truth",
        "source_futures_1h": str(futures_path),
        "source_fred_macro": str(fred_path),
        "source_futures_sha256": sha256_file(futures_path),
        "source_fred_sha256": sha256_file(fred_path),
        "start": start,
        "end": end,
        "horizon_hours": horizon_hours,
        "symbols": symbols,
        "symbol_count": len(symbols),
        "fred_columns": fred_columns,
        "row_count": int(len(out)),
        "ts_first": out["ts"].min().isoformat(),
        "ts_last": out["ts"].max().isoformat(),
        "output_csv": str(output_csv),
        "output_sha256": sha256_file(output_csv),
        "study_db": str(study_db),
        "duckdb_table": "anofox_external_1h_context",
        "symbol_coverage": [
            {
                "symbol": str(row.symbol),
                "rows": int(row.rows),
                "ts_first": pd.Timestamp(row.ts_first).isoformat(),
                "ts_last": pd.Timestamp(row.ts_last).isoformat(),
            }
            for row in symbol_coverage.itertuples(index=False)
        ],
    }
    write_json(output_manifest, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build 5y external AnoFox context from local Historical Data futures + FRED rates."
    )
    parser.add_argument("--futures-1h", default=DEFAULT_EXTERNAL_FUTURES_1H, type=Path)
    parser.add_argument("--fred-macro", default=DEFAULT_EXTERNAL_FRED_MACRO, type=Path)
    parser.add_argument("--output-csv", default=DEFAULT_EXTERNAL_CONTEXT_CSV, type=Path)
    parser.add_argument("--output-manifest", default=DEFAULT_EXTERNAL_CONTEXT_MANIFEST, type=Path)
    parser.add_argument("--study-db", default=DEFAULT_STUDY_DB, type=Path)
    parser.add_argument("--symbols", default=DEFAULT_CORE_SYMBOLS)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument("--horizon-hours", default=12, type=int)
    parser.add_argument("--min-coverage", default=0.75, type=float)
    args = parser.parse_args()

    payload = build_external_context(
        futures_path=args.futures_1h,
        fred_path=args.fred_macro,
        output_csv=args.output_csv,
        output_manifest=args.output_manifest,
        study_db=args.study_db,
        symbols_raw=args.symbols,
        start=args.start,
        end=args.end,
        horizon_hours=args.horizon_hours,
        min_coverage=args.min_coverage,
    )
    print(
        "PASS: built external anofox context "
        f"rows={payload['row_count']} symbols={payload['symbol_count']} "
        f"fred_cols={len(payload['fred_columns'])}"
    )
    print(f"output_csv={payload['output_csv']}")
    print(f"output_manifest={args.output_manifest}")


if __name__ == "__main__":
    main()
