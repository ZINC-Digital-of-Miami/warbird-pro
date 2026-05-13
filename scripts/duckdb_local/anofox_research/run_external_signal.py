#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from build_external_context import build_external_context
from common import (
    DEFAULT_EXTERNAL_CONTEXT_CSV,
    DEFAULT_EXTERNAL_CONTEXT_MANIFEST,
    DEFAULT_EXTERNAL_FRED_MACRO,
    DEFAULT_EXTERNAL_FUTURES_1H,
    DEFAULT_STUDY_DB,
    WORKSPACE,
    ensure_anofox,
    parse_model_list,
    read_json,
    write_json,
)


DEFAULT_SERIES_PREFIXES = ("sym_", "fred_")
DEFAULT_SERIES_SUFFIXES = ("ret_1h_bp", "_d1")


def _sign(value: float, neutral_band: float = 0.0) -> int:
    if not math.isfinite(value) or abs(value) <= neutral_band:
        return 0
    return 1 if value > 0 else -1


def _candidate_columns(df: pd.DataFrame, max_series: int) -> list[str]:
    columns = [
        column
        for column in df.columns
        if column.startswith(DEFAULT_SERIES_PREFIXES)
        and (column.endswith(DEFAULT_SERIES_SUFFIXES) or column in {"fred_vix", "fred_dxy"})
        and column != "sym_es_ret_1h_bp"
    ]

    es = pd.to_numeric(df["sym_es_ret_1h_bp"], errors="coerce")
    scored: list[tuple[float, str]] = []
    for column in columns:
        series = pd.to_numeric(df[column], errors="coerce")
        joined = pd.concat([es, series], axis=1).dropna()
        if len(joined) < 250:
            continue
        corr = _safe_corr(joined.iloc[:, 0], joined.iloc[:, 1])
        if math.isfinite(corr):
            scored.append((abs(float(corr)), column))
    scored.sort(reverse=True)
    selected = [column for _score, column in scored]
    if max_series > 0:
        selected = selected[:max_series]
    return selected


def _safe_corr(left: pd.Series, right: pd.Series) -> float:
    if left.nunique(dropna=True) < 2 or right.nunique(dropna=True) < 2:
        return float("nan")
    left_std = float(left.std())
    right_std = float(right.std())
    if not math.isfinite(left_std) or not math.isfinite(right_std) or left_std <= 0.0 or right_std <= 0.0:
        return float("nan")
    return float(left.corr(right))


def _select_cutoffs(df: pd.DataFrame, train_rows: int, horizon_hours: int, windows: int, step_hours: int) -> list[int]:
    min_cutoff = train_rows - 1
    max_cutoff = len(df) - horizon_hours - 1
    if max_cutoff < min_cutoff:
        raise ValueError(
            f"not enough rows for train_rows={train_rows}, horizon_hours={horizon_hours}, rows={len(df)}"
        )
    cutoffs: list[int] = []
    cursor = max_cutoff
    while cursor >= min_cutoff and len(cutoffs) < windows:
        if math.isfinite(float(df.iloc[cursor]["future_es_return_bp"])):
            cutoffs.append(cursor)
        cursor -= step_hours
    return sorted(cutoffs)


def _forecast_series(
    con: duckdb.DuckDBPyConnection,
    train: pd.DataFrame,
    series_id: str,
    model: str,
    horizon_hours: int,
    freq: str,
) -> pd.DataFrame:
    model_sql = model.replace("'", "''")
    forecast_input = train[["ts", series_id]].rename(columns={"ts": "ds", series_id: "y"}).copy()
    forecast_input["id"] = series_id
    forecast_input = forecast_input[np.isfinite(forecast_input["y"].to_numpy(dtype=float))]
    if len(forecast_input) < 100:
        raise ValueError(f"not enough finite training rows for {series_id}: {len(forecast_input)}")

    con.register("anofox_external_input_df", forecast_input)
    con.execute(
        """
        CREATE OR REPLACE TEMP TABLE anofox_external_input AS
        SELECT id, CAST(ds AS TIMESTAMP) AS ds, CAST(y AS DOUBLE) AS y
        FROM anofox_external_input_df
        ORDER BY ds
        """
    )
    forecast = con.execute(
        f"""
        SELECT forecast_step, ds, yhat, model_name
        FROM ts_forecast_by(
          'anofox_external_input',
          id,
          ds,
          y,
          '{model_sql}',
          {int(horizon_hours)},
          '{freq}',
          MAP{{}}
        )
        ORDER BY forecast_step
        """
    ).fetchdf()
    if len(forecast) < horizon_hours:
        raise ValueError(f"{model} returned {len(forecast)} rows for {series_id}; expected {horizon_hours}")
    return forecast


def _model_metrics(rows: pd.DataFrame) -> list[dict]:
    if rows.empty:
        return []
    output: list[dict] = []
    for model, group in rows.groupby("model", sort=True):
        valid = group[group["actual_sign"].ne(0)]
        active = group[group["pressure_sign"].ne(0)]
        output.append(
            {
                "model": model,
                "windows": int(len(group)),
                "direction_hit_rate": (
                    float(valid["pressure_sign"].eq(valid["actual_sign"]).mean()) if len(valid) else None
                ),
                "active_windows": int(len(active)),
                "active_direction_hit_rate": (
                    float(active["pressure_sign"].eq(active["actual_sign"]).mean()) if len(active) else None
                ),
                "mean_pressure_score": float(group["pressure_score"].mean()),
                "mean_abs_pressure_score": float(group["pressure_score"].abs().mean()),
            }
        )
    return output


def _series_metrics(rows: pd.DataFrame) -> list[dict]:
    if rows.empty:
        return []
    output: list[dict] = []
    for (model, series_id), group in rows.groupby(["model", "series_id"], sort=True):
        active = group[group["series_pressure_sign"].ne(0)]
        output.append(
            {
                "model": model,
                "series_id": series_id,
                "windows": int(len(group)),
                "active_windows": int(len(active)),
                "direction_hit_rate": (
                    float(active["series_pressure_sign"].eq(active["actual_sign"]).mean()) if len(active) else None
                ),
                "mean_abs_corr": float(group["abs_corr"].mean()),
            }
        )
    output.sort(key=lambda item: (-1 if item["direction_hit_rate"] is None else -item["direction_hit_rate"], item["series_id"]))
    return output


def run_external_signal(
    dataset_csv: Path,
    dataset_manifest: Path,
    output_dir: Path,
    models: list[str],
    horizon_hours: int,
    train_rows: int,
    windows: int,
    step_hours: int,
    freq: str,
    max_series: int,
    build_if_missing: bool,
) -> dict:
    if not dataset_csv.exists():
        if not build_if_missing:
            raise FileNotFoundError(f"external context dataset not found: {dataset_csv}")
        build_external_context(
            futures_path=DEFAULT_EXTERNAL_FUTURES_1H,
            fred_path=DEFAULT_EXTERNAL_FRED_MACRO,
            output_csv=dataset_csv,
            output_manifest=dataset_manifest,
            study_db=DEFAULT_STUDY_DB,
            symbols_raw="all",
            start="2020-01-01",
            end="2025-12-15",
            horizon_hours=horizon_hours,
            min_coverage=0.75,
        )

    df = pd.read_csv(dataset_csv, parse_dates=["ts"])
    required = {"ts", "sym_es_ret_1h_bp", "future_es_return_bp", "future_es_return_sign"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"external context dataset missing columns: {missing}")

    candidates = _candidate_columns(df, max_series=max_series)
    if not candidates:
        raise ValueError("no candidate external series found")
    cutoffs = _select_cutoffs(df, train_rows, horizon_hours, windows, step_hours)

    con = duckdb.connect(":memory:")
    extension_info = ensure_anofox(con, install=True)
    model_rows: list[dict] = []
    series_rows: list[dict] = []
    failures: list[dict] = []

    for window_id, cutoff in enumerate(cutoffs, start=1):
        train = df.iloc[cutoff - train_rows + 1 : cutoff + 1].copy()
        future = df.iloc[cutoff + 1 : cutoff + horizon_hours + 1].copy()
        actual_sum = float(future["sym_es_ret_1h_bp"].sum())
        actual_sign = _sign(actual_sum)
        cutoff_ts = pd.Timestamp(df.iloc[cutoff]["ts"]).isoformat()
        train_es = pd.to_numeric(train["sym_es_ret_1h_bp"], errors="coerce")

        for model in models:
            pressure_score = 0.0
            active_votes = 0
            for series_id in candidates:
                train_series = pd.to_numeric(train[series_id], errors="coerce")
                joined = pd.concat([train_es, train_series], axis=1).dropna()
                if len(joined) < 250:
                    continue
                corr = _safe_corr(joined.iloc[:, 0], joined.iloc[:, 1])
                if not math.isfinite(corr) or abs(corr) < 0.02:
                    continue
                try:
                    forecast = _forecast_series(con, train, series_id, model, horizon_hours, freq)
                except Exception as error:
                    failures.append(
                        {
                            "window_id": window_id,
                            "cutoff_ts": cutoff_ts,
                            "model": model,
                            "series_id": series_id,
                            "error": str(error),
                        }
                    )
                    continue

                forecast_sum = float(forecast["yhat"].head(horizon_hours).sum())
                series_signal = _sign(forecast_sum)
                series_pressure_sign = _sign(corr * series_signal)
                if series_pressure_sign:
                    pressure_score += abs(corr) * series_pressure_sign
                    active_votes += 1
                series_rows.append(
                    {
                        "window_id": window_id,
                        "cutoff_ts": cutoff_ts,
                        "model": model,
                        "series_id": series_id,
                        "corr_to_es": corr,
                        "abs_corr": abs(corr),
                        "forecast_sum": forecast_sum,
                        "series_signal": series_signal,
                        "series_pressure_sign": series_pressure_sign,
                        "actual_es_sum": actual_sum,
                        "actual_sign": actual_sign,
                    }
                )

            model_rows.append(
                {
                    "window_id": window_id,
                    "cutoff_ts": cutoff_ts,
                    "model": model,
                    "candidate_series": len(candidates),
                    "active_votes": active_votes,
                    "pressure_score": pressure_score,
                    "pressure_sign": _sign(pressure_score),
                    "actual_es_sum": actual_sum,
                    "actual_sign": actual_sign,
                }
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    model_df = pd.DataFrame(model_rows)
    series_df = pd.DataFrame(series_rows)
    model_csv = output_dir / "model_pressure_rows.csv"
    series_csv = output_dir / "series_pressure_rows.csv"
    if not model_df.empty:
        model_df.to_csv(model_csv, index=False)
    if not series_df.empty:
        series_df.to_csv(series_csv, index=False)

    payload = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if not failures else "partial",
        "lane": "anofox_research_external",
        "purpose": "cross-asset/FRED pressure benchmark for ES 1h context",
        "dataset_csv": str(dataset_csv),
        "dataset_manifest": read_json(dataset_manifest),
        "models": models,
        "horizon_hours": horizon_hours,
        "train_rows": train_rows,
        "windows_requested": windows,
        "windows_evaluated": len(cutoffs),
        "step_hours": step_hours,
        "candidate_series": candidates,
        "candidate_series_count": len(candidates),
        "cutoffs": [pd.Timestamp(df.iloc[idx]["ts"]).isoformat() for idx in cutoffs],
        "extension": extension_info,
        "model_metrics": _model_metrics(model_df),
        "series_metrics": _series_metrics(series_df),
        "failures": failures,
        "outputs": {
            "model_pressure_rows_csv": str(model_csv) if not model_df.empty else None,
            "series_pressure_rows_csv": str(series_csv) if not series_df.empty else None,
            "metrics_json": str(output_dir / "metrics.json"),
        },
    }
    write_json(output_dir / "metrics.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run external cross-asset/FRED AnoFox pressure benchmark.")
    parser.add_argument("--dataset-csv", default=DEFAULT_EXTERNAL_CONTEXT_CSV, type=Path)
    parser.add_argument("--dataset-manifest", default=DEFAULT_EXTERNAL_CONTEXT_MANIFEST, type=Path)
    parser.add_argument("--output-dir", default=None, type=Path)
    parser.add_argument("--models", default="AutoTheta,DynamicOptimizedTheta")
    parser.add_argument("--horizon-hours", default=12, type=int)
    parser.add_argument("--train-rows", default=4000, type=int)
    parser.add_argument("--windows", default=6, type=int)
    parser.add_argument("--step-hours", default=240, type=int)
    parser.add_argument("--freq", default="1h")
    parser.add_argument("--max-series", default=24, type=int, help="0 means use every eligible candidate series.")
    parser.add_argument("--build-if-missing", action="store_true")
    args = parser.parse_args()

    output_dir = args.output_dir
    if output_dir is None:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_dir = WORKSPACE / "runs_external" / run_id

    payload = run_external_signal(
        dataset_csv=args.dataset_csv,
        dataset_manifest=args.dataset_manifest,
        output_dir=output_dir,
        models=parse_model_list(args.models),
        horizon_hours=args.horizon_hours,
        train_rows=args.train_rows,
        windows=args.windows,
        step_hours=args.step_hours,
        freq=args.freq,
        max_series=args.max_series,
        build_if_missing=args.build_if_missing,
    )
    print(
        f"{payload['status'].upper()}: external signal benchmark "
        f"models={','.join(payload['models'])} windows={payload['windows_evaluated']} "
        f"series={payload['candidate_series_count']} failures={len(payload['failures'])}"
    )
    for item in payload["model_metrics"]:
        print(
            "pressure "
            f"model={item['model']} hit_rate={item['direction_hit_rate']} "
            f"active_hit_rate={item['active_direction_hit_rate']} active_windows={item['active_windows']}"
        )
    print(f"metrics_json={payload['outputs']['metrics_json']}")


if __name__ == "__main__":
    main()
