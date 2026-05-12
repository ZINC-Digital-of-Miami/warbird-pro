#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone

import duckdb

from common import ensure_anofox, write_json, WORKSPACE


def run_preflight(output_json) -> dict:
    con = duckdb.connect(":memory:")
    extension_info = ensure_anofox(con, install=True)

    con.execute(
        """
        CREATE OR REPLACE TABLE anofox_smoke AS
        SELECT
          TIMESTAMP '2024-01-01 00:00:00' + (i * INTERVAL '15 minutes') AS ds,
          'smoke_15m' AS id,
          100.0 + sin(i / 10.0) AS y
        FROM generate_series(0, 199) AS t(i)
        """
    )
    rows = con.execute(
        """
        SELECT forecast_step, ds, yhat, model_name
        FROM ts_forecast_by('anofox_smoke', id, ds, y, 'AutoTheta', 3, '15m', MAP{})
        ORDER BY forecast_step
        """
    ).fetchall()

    payload = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "extension": extension_info,
        "smoke_rows": [
            {
                "forecast_step": int(step),
                "ds": ds.isoformat(),
                "yhat": float(yhat),
                "model_name": str(model_name),
            }
            for step, ds, yhat, model_name in rows
        ],
    }
    write_json(output_json, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Preflight DuckDB anofox_forecast extension.")
    parser.add_argument(
        "--output-json",
        default=WORKSPACE / "anofox_preflight.json",
        type=str,
        help="Path for preflight JSON output.",
    )
    args = parser.parse_args()

    payload = run_preflight(args.output_json)
    print(f"PASS: anofox_forecast loaded; smoke forecast rows={len(payload['smoke_rows'])}")
    print(f"output_json={args.output_json}")


if __name__ == "__main__":
    main()
