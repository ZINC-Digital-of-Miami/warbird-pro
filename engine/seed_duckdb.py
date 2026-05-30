"""Seed DuckDB from local batch files and the local repo SQL file at supabase/seed.sql.

Reads local .zip/.parquet files from data/ and populates:
- Bar tables (mes_1m, etc.)
- trades_raw
- cross_asset_1h
- symbols (from supabase/seed.sql active records — a local repo SQL file, not the Supabase cloud service)

This is for initial seeding from local Databento batch downloads — zero API cost.

Usage:
    python engine/seed_duckdb.py
"""

from __future__ import annotations

import os
import re
import sys

import duckdb

from engine.config import DATA_DIR, DUCKDB_PATH
from engine.init_db import init_all_tables

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_SEED_SQL_PATH = os.path.join(REPO_ROOT, "supabase", "seed.sql")


def _parse_active_symbols(seed_path: str) -> list[dict]:
    """Parse the local repo file supabase/seed.sql to extract active symbols (is_active = true).

    This reads a plain SQL file from the repo; it does not use the Supabase client or cloud API.
    Returns list of dicts with keys matching the symbols table schema.
    """
    if not os.path.isfile(seed_path):
        print(f"WARNING: seed.sql not found at {seed_path}")
        return []

    with open(seed_path, "r") as f:
        content = f.read()

    symbols: list[dict] = []

    pattern = re.compile(
        r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,"
        r"\s*([0-9.]+)\s*,\s*'([^']+)'\s*,\s*"
        r"(?:'([^']+)'|null)\s*,\s*"
        r"(?:'([^']+)'|null)\s*,\s*"
        r"(?:'([^']+)'|null)\s*,\s*"
        r"(true|false)\s*\)"
    )

    for m in pattern.finditer(content):
        is_active = m.group(10) == "true"
        data_source = m.group(6)

        if not is_active:
            continue

        # Only seed Databento futures (17) and FRED (3) — skip options
        if data_source == "DATABENTO" and ".OPT" in m.group(1):
            continue

        symbols.append({
            "code": m.group(1),
            "display_name": m.group(2),
            "short_name": m.group(3),
            "description": m.group(4),
            "tick_size": float(m.group(5)),
            "data_source": data_source,
            "dataset": m.group(7),
            "databento_symbol": m.group(8),
            "is_active": True,
        })

    return symbols


def seed_symbols(conn: duckdb.DuckDBPyConnection) -> int:
    """Seed the symbols table from the local repo file supabase/seed.sql."""
    symbols = _parse_active_symbols(LOCAL_SEED_SQL_PATH)
    if not symbols:
        print("WARNING: No active symbols parsed from seed.sql")
        return 0

    for s in symbols:
        conn.execute(
            "INSERT OR IGNORE INTO symbols "
            "(code, display_name, short_name, description, tick_size, "
            "data_source, dataset, databento_symbol, is_active) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                s["code"], s["display_name"], s["short_name"],
                s["description"], s["tick_size"], s["data_source"],
                s["dataset"], s["databento_symbol"], s["is_active"],
            ],
        )

    return len(symbols)


def _resolve_target_table(fname: str) -> str | None:
    """Map a data file name to its DuckDB target table."""
    name = fname.lower()
    if "cross_asset" in name or "ohlcv_1h" in name:
        return "cross_asset_1h"
    if "trades" in name:
        return "trades_raw"
    if "ohlcv" in name and "1m" in name:
        return "mes_1m"
    return None


def _read_source(fpath: str) -> str:
    """Return the DuckDB read expression for a file path."""
    safe = fpath.replace("'", "''")
    if fpath.endswith(".zip"):
        return f"read_parquet('{safe}/*.parquet')"
    return f"read_parquet('{safe}')"


_TABLES_WITH_UNIQUE = {"mes_1m", "cross_asset_1h"}


def _ingest_file(
    conn: duckdb.DuckDBPyConnection, fname: str, fpath: str,
) -> int | None:
    """Ingest a single data file into the matching DuckDB table. Returns row count or None."""
    table = _resolve_target_table(fname)
    if table is None:
        return None

    source = _read_source(fpath)
    try:
        count: int = conn.execute(f"SELECT count(*) FROM {source}").fetchone()[0]
        conflict = " ON CONFLICT DO NOTHING" if table in _TABLES_WITH_UNIQUE else ""
        conn.execute(f"INSERT INTO {table} SELECT * FROM {source}{conflict}")
        return count
    except Exception as e:
        print(f"WARNING: Could not read {fname}: {e}")
        return None


def seed_bars_from_files(conn: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Seed bar tables from local .zip and .parquet files in data/."""
    results: dict[str, int] = {}

    if not os.path.isdir(DATA_DIR):
        print(f"WARNING: data/ directory not found at {DATA_DIR}")
        return results

    for fname in os.listdir(DATA_DIR):
        if not fname.endswith((".parquet", ".zip")):
            continue
        fpath = os.path.join(DATA_DIR, fname)
        count = _ingest_file(conn, fname, fpath)
        if count is not None:
            results[fname] = count

    return results


def main() -> None:
    """CLI entry point — seed DuckDB from local files and seed.sql."""
    init_all_tables()

    conn = duckdb.connect(DUCKDB_PATH)

    print("Seeding symbols from supabase/seed.sql...")
    sym_count = seed_symbols(conn)
    print(f"  Seeded {sym_count} active symbols")

    # Verify breakdown
    db_count = conn.execute("SELECT count(*) FROM symbols WHERE data_source = 'DATABENTO'").fetchone()[0]
    fred_count = conn.execute("SELECT count(*) FROM symbols WHERE data_source = 'FRED'").fetchone()[0]
    print(f"  Databento: {db_count}, FRED: {fred_count}")

    print()
    print("Seeding bar data from local files...")
    file_results = seed_bars_from_files(conn)
    if file_results:
        for fname, count in file_results.items():
            print(f"  {fname}: {count} rows")
    else:
        print("  No data files found in data/ (this is OK for initial setup)")

    conn.close()
    print()
    print("Seed complete.")


if __name__ == "__main__":
    main()
