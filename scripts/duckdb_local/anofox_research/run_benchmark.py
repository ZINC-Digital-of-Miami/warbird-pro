#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from build_dataset import build_dataset
from common import (
    DEFAULT_CORE_EXPORT,
    DEFAULT_CORE_MANIFEST,
    DEFAULT_DATASET_CSV,
    DEFAULT_DATASET_MANIFEST,
    DEFAULT_STUDY_DB,
    WORKSPACE,
    ensure_anofox,
    parse_model_list,
    read_json,
    write_json,
)


TARGETS = ("bar_return_points", "atr_pct_bp")


def _sign(value: float) -> int:
    if not math.isfinite(value) or value == 0.0:
        return 0
    return 1 if value > 0 else -1


def _finite_mean(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return float("nan")
    return float(values.mean())


def _rmse(errors: np.ndarray) -> float:
    errors = np.asarray(errors, dtype=float)
    errors = errors[np.isfinite(errors)]
    if len(errors) == 0:
        return float("nan")
    return float(np.sqrt(np.mean(np.square(errors))))


def _select_cutoffs(
    df: pd.DataFrame,
    train_rows: int,
    horizon_bars: int,
    windows: int,
    step_bars: int,
    cutoff_mode: str,
) -> tuple[list[int], list[str]]:
    notes: list[str] = []
    min_cutoff = train_rows - 1
    max_cutoff = len(df) - horizon_bars - 1
    if max_cutoff < min_cutoff:
        raise ValueError(
            f"not enough rows for train_rows={train_rows}, horizon_bars={horizon_bars}, rows={len(df)}"
        )

    eligible = np.arange(min_cutoff, max_cutoff + 1)
    if cutoff_mode == "entry":
        entry_mask = df["entry_dir"].to_numpy(dtype=int) != 0
        finite_future = np.isfinite(df["future_return_points"].to_numpy(dtype=float))
        entry_cutoffs = [int(i) for i in eligible if entry_mask[i] and finite_future[i]]
        if entry_cutoffs:
            take = min(windows, len(entry_cutoffs))
            selected_positions = np.linspace(0, len(entry_cutoffs) - 1, take, dtype=int)
            return [entry_cutoffs[int(pos)] for pos in selected_positions], notes
        notes.append("No eligible entry cutoffs found; fell back to latest rolling cutoffs.")

    cutoffs = []
    cursor = max_cutoff
    while cursor >= min_cutoff and len(cutoffs) < windows:
        cutoffs.append(cursor)
        cursor -= step_bars
    return sorted(cutoffs), notes


def _forecast(
    con: duckdb.DuckDBPyConnection,
    train: pd.DataFrame,
    target: str,
    model: str,
    horizon_bars: int,
    freq: str,
) -> pd.DataFrame:
    model_sql = model.replace("'", "''")
    forecast_input = train[["ts", target]].rename(columns={"ts": "ds", target: "y"}).copy()
    forecast_input["id"] = f"es_15m_{target}"
    forecast_input = forecast_input[np.isfinite(forecast_input["y"].to_numpy(dtype=float))]
    if len(forecast_input) < 25:
        raise ValueError(f"not enough finite training rows for {target}: {len(forecast_input)}")

    con.register("anofox_forecast_input_df", forecast_input)
    con.execute(
        """
        CREATE OR REPLACE TEMP TABLE anofox_forecast_input AS
        SELECT id, CAST(ds AS TIMESTAMP) AS ds, CAST(y AS DOUBLE) AS y
        FROM anofox_forecast_input_df
        ORDER BY ds
        """
    )
    forecast = con.execute(
        f"""
        SELECT forecast_step, ds, yhat, yhat_lower, yhat_upper, model_name
        FROM ts_forecast_by(
          'anofox_forecast_input',
          id,
          ds,
          y,
          '{model_sql}',
          {int(horizon_bars)},
          '{freq}',
          MAP{{}}
        )
        ORDER BY forecast_step
        """
    ).fetchdf()
    if len(forecast) < horizon_bars:
        raise ValueError(f"{model} returned {len(forecast)} rows for {target}; expected {horizon_bars}")
    return forecast


def _aggregate_metrics(forecast_rows: pd.DataFrame) -> list[dict]:
    metrics: list[dict] = []
    if forecast_rows.empty:
        return metrics

    for (model, target), group in forecast_rows.groupby(["model", "target"], sort=True):
        errors = group["yhat"].to_numpy(dtype=float) - group["actual"].to_numpy(dtype=float)
        mase_terms = np.abs(errors) / group["mase_scale"].to_numpy(dtype=float)
        metrics.append(
            {
                "model": model,
                "target": target,
                "forecast_rows": int(len(group)),
                "windows": int(group["window_id"].nunique()),
                "mae": _finite_mean(np.abs(errors)),
                "rmse": _rmse(errors),
                "bias": _finite_mean(errors),
                "mase": _finite_mean(mase_terms),
            }
        )
    return metrics


def _direction_metrics(direction_rows: pd.DataFrame) -> list[dict]:
    metrics: list[dict] = []
    if direction_rows.empty:
        return metrics

    for model, group in direction_rows.groupby("model", sort=True):
        valid = group[group["actual_sign"].ne(0)]
        entry = group[group["entry_dir"].ne(0)].copy()
        entry["baseline_points"] = entry["entry_dir"] * entry["actual_sum"]
        entry["passes_filter"] = entry["forecast_sign"].eq(entry["entry_dir"])
        filtered = entry[entry["passes_filter"]]
        metrics.append(
            {
                "model": model,
                "windows": int(len(group)),
                "direction_hit_rate": (
                    float(valid["forecast_sign"].eq(valid["actual_sign"]).mean()) if len(valid) else None
                ),
                "entry_windows": int(len(entry)),
                "entry_baseline_hit_rate": (
                    float(entry["baseline_points"].gt(0).mean()) if len(entry) else None
                ),
                "entry_baseline_expectancy_points": (
                    float(entry["baseline_points"].mean()) if len(entry) else None
                ),
                "entry_filtered_count": int(len(filtered)),
                "entry_filtered_hit_rate": (
                    float((filtered["entry_dir"] * filtered["actual_sum"]).gt(0).mean())
                    if len(filtered)
                    else None
                ),
                "entry_filtered_expectancy_points": (
                    float((filtered["entry_dir"] * filtered["actual_sum"]).mean()) if len(filtered) else None
                ),
                "entry_expectancy_delta_points": (
                    float((filtered["entry_dir"] * filtered["actual_sum"]).mean() - entry["baseline_points"].mean())
                    if len(filtered) and len(entry)
                    else None
                ),
                "entry_filtered_false_positive_rate": (
                    float((filtered["entry_dir"] * filtered["actual_sum"]).le(0).mean()) if len(filtered) else None
                ),
            }
        )
    return metrics


def _volatility_metrics(vol_rows: pd.DataFrame) -> list[dict]:
    metrics: list[dict] = []
    if vol_rows.empty:
        return metrics

    for model, group in vol_rows.groupby("model", sort=True):
        metrics.append(
            {
                "model": model,
                "windows": int(len(group)),
                "high_low_regime_hit_rate": float(group["forecast_high"].eq(group["actual_high"]).mean()),
                "forecast_high_rate": float(group["forecast_high"].mean()),
                "actual_high_rate": float(group["actual_high"].mean()),
            }
        )
    return metrics


def run_benchmark(
    dataset_csv: Path,
    dataset_manifest: Path,
    output_dir: Path,
    models: list[str],
    horizon_bars: int,
    train_rows: int,
    windows: int,
    step_bars: int,
    cutoff_mode: str,
    freq: str,
    build_if_missing: bool,
) -> dict:
    if not dataset_csv.exists():
        if not build_if_missing:
            raise FileNotFoundError(f"dataset not found: {dataset_csv}")
        build_dataset(
            source_csv=DEFAULT_CORE_EXPORT,
            source_manifest=DEFAULT_CORE_MANIFEST,
            output_csv=dataset_csv,
            output_manifest=dataset_manifest,
            study_db=DEFAULT_STUDY_DB,
            horizon_bars=horizon_bars,
        )

    df = pd.read_csv(dataset_csv, parse_dates=["ts"])
    for target in TARGETS:
        if target not in df.columns:
            raise ValueError(f"dataset missing target column: {target}")
    if "entry_dir" not in df.columns:
        raise ValueError("dataset missing entry_dir column")

    cutoffs, notes = _select_cutoffs(df, train_rows, horizon_bars, windows, step_bars, cutoff_mode)
    con = duckdb.connect(":memory:")
    extension_info = ensure_anofox(con, install=True)

    forecast_rows: list[dict] = []
    direction_rows: list[dict] = []
    volatility_rows: list[dict] = []
    failures: list[dict] = []

    for window_id, cutoff in enumerate(cutoffs, start=1):
        train = df.iloc[cutoff - train_rows + 1 : cutoff + 1].copy()
        future = df.iloc[cutoff + 1 : cutoff + horizon_bars + 1].copy()
        cutoff_ts = df.iloc[cutoff]["ts"]
        entry_dir = int(df.iloc[cutoff]["entry_dir"])

        for model in models:
            target_forecasts: dict[str, pd.DataFrame] = {}
            for target in TARGETS:
                train_y = train[target].dropna().to_numpy(dtype=float)
                scale = float(np.mean(np.abs(np.diff(train_y)))) if len(train_y) > 1 else float("nan")
                if not math.isfinite(scale) or scale <= 0:
                    scale = 1.0
                try:
                    forecast = _forecast(con, train, target, model, horizon_bars, freq)
                    target_forecasts[target] = forecast
                except Exception as error:
                    failures.append(
                        {
                            "window_id": window_id,
                            "cutoff_ts": pd.Timestamp(cutoff_ts).isoformat(),
                            "model": model,
                            "target": target,
                            "error": str(error),
                        }
                    )
                    continue

                actual = future[target].to_numpy(dtype=float)
                for row_idx, row in forecast.iterrows():
                    step_idx = int(row["forecast_step"]) - 1
                    if step_idx >= len(actual):
                        continue
                    forecast_rows.append(
                        {
                            "window_id": window_id,
                            "cutoff_ts": pd.Timestamp(cutoff_ts).isoformat(),
                            "model": model,
                            "target": target,
                            "forecast_step": int(row["forecast_step"]),
                            "forecast_ts": pd.Timestamp(row["ds"]).isoformat(),
                            "yhat": float(row["yhat"]),
                            "actual": float(actual[step_idx]),
                            "mase_scale": scale,
                            "model_name": str(row["model_name"]),
                        }
                    )

            if "bar_return_points" in target_forecasts:
                ret_forecast = target_forecasts["bar_return_points"]
                predicted_sum = float(ret_forecast["yhat"].head(horizon_bars).sum())
                actual_sum = float(future["bar_return_points"].sum())
                direction_rows.append(
                    {
                        "window_id": window_id,
                        "cutoff_ts": pd.Timestamp(cutoff_ts).isoformat(),
                        "model": model,
                        "forecast_sum": predicted_sum,
                        "actual_sum": actual_sum,
                        "forecast_sign": _sign(predicted_sum),
                        "actual_sign": _sign(actual_sum),
                        "entry_dir": entry_dir,
                    }
                )

            if "atr_pct_bp" in target_forecasts:
                vol_forecast = target_forecasts["atr_pct_bp"]
                threshold = float(train["atr_pct_bp"].dropna().median())
                forecast_mean = float(vol_forecast["yhat"].head(horizon_bars).mean())
                actual_mean = float(future["atr_pct_bp"].mean())
                volatility_rows.append(
                    {
                        "window_id": window_id,
                        "cutoff_ts": pd.Timestamp(cutoff_ts).isoformat(),
                        "model": model,
                        "threshold_atr_pct_bp": threshold,
                        "forecast_mean_atr_pct_bp": forecast_mean,
                        "actual_mean_atr_pct_bp": actual_mean,
                        "forecast_high": forecast_mean > threshold,
                        "actual_high": actual_mean > threshold,
                    }
                )

    forecast_df = pd.DataFrame(forecast_rows)
    direction_df = pd.DataFrame(direction_rows)
    volatility_df = pd.DataFrame(volatility_rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    forecast_csv = output_dir / "forecast_rows.csv"
    direction_csv = output_dir / "direction_rows.csv"
    volatility_csv = output_dir / "volatility_rows.csv"
    if not forecast_df.empty:
        forecast_df.to_csv(forecast_csv, index=False)
    if not direction_df.empty:
        direction_df.to_csv(direction_csv, index=False)
    if not volatility_df.empty:
        volatility_df.to_csv(volatility_csv, index=False)

    payload = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if not failures else "partial",
        "lane": "anofox_research",
        "purpose": "rolling OOS forecast benchmark for V9 regime/context sidecar",
        "dataset_csv": str(dataset_csv),
        "dataset_manifest": read_json(dataset_manifest),
        "output_dir": str(output_dir),
        "models": models,
        "targets": list(TARGETS),
        "horizon_bars": horizon_bars,
        "train_rows": train_rows,
        "windows_requested": windows,
        "windows_evaluated": len(cutoffs),
        "cutoff_mode": cutoff_mode,
        "cutoffs": [pd.Timestamp(df.iloc[idx]["ts"]).isoformat() for idx in cutoffs],
        "notes": notes,
        "extension": extension_info,
        "forecast_metrics": _aggregate_metrics(forecast_df),
        "direction_metrics": _direction_metrics(direction_df),
        "volatility_metrics": _volatility_metrics(volatility_df),
        "failures": failures,
        "outputs": {
            "forecast_rows_csv": str(forecast_csv) if not forecast_df.empty else None,
            "direction_rows_csv": str(direction_csv) if not direction_df.empty else None,
            "volatility_rows_csv": str(volatility_csv) if not volatility_df.empty else None,
            "metrics_json": str(output_dir / "metrics.json"),
        },
    }
    write_json(output_dir / "metrics.json", payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AnoFox rolling OOS benchmark on the 15m sidecar dataset.")
    parser.add_argument("--dataset-csv", default=DEFAULT_DATASET_CSV, type=Path)
    parser.add_argument("--dataset-manifest", default=DEFAULT_DATASET_MANIFEST, type=Path)
    parser.add_argument("--output-dir", default=None, type=Path)
    parser.add_argument("--models", default="AutoTheta,DynamicOptimizedTheta,AutoARIMA")
    parser.add_argument("--horizon-bars", default=12, type=int)
    parser.add_argument("--train-rows", default=750, type=int)
    parser.add_argument("--windows", default=6, type=int)
    parser.add_argument("--step-bars", default=96, type=int)
    parser.add_argument("--cutoff-mode", choices=("entry", "latest"), default="entry")
    parser.add_argument("--freq", default="15m")
    parser.add_argument("--build-if-missing", action="store_true")
    args = parser.parse_args()

    models = parse_model_list(args.models)
    output_dir = args.output_dir
    if output_dir is None:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_dir = WORKSPACE / "runs" / run_id

    payload = run_benchmark(
        dataset_csv=args.dataset_csv,
        dataset_manifest=args.dataset_manifest,
        output_dir=output_dir,
        models=models,
        horizon_bars=args.horizon_bars,
        train_rows=args.train_rows,
        windows=args.windows,
        step_bars=args.step_bars,
        cutoff_mode=args.cutoff_mode,
        freq=args.freq,
        build_if_missing=args.build_if_missing,
    )

    print(
        f"{payload['status'].upper()}: anofox benchmark "
        f"models={','.join(models)} windows={payload['windows_evaluated']} "
        f"failures={len(payload['failures'])}"
    )
    for item in payload["direction_metrics"]:
        print(
            "direction "
            f"model={item['model']} hit_rate={item['direction_hit_rate']} "
            f"entry_delta_pts={item['entry_expectancy_delta_points']} "
            f"filtered_count={item['entry_filtered_count']}"
        )
    for item in payload["volatility_metrics"]:
        print(
            "volatility "
            f"model={item['model']} high_low_hit_rate={item['high_low_regime_hit_rate']}"
        )
    print(f"metrics_json={payload['outputs']['metrics_json']}")


if __name__ == "__main__":
    main()
