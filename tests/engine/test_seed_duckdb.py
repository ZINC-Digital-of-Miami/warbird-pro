"""Tests for engine/seed_duckdb.py — symbol seeding and file ingestion."""

from __future__ import annotations

import os

import duckdb
import pytest


@pytest.fixture()
def tmp_db_with_tables(monkeypatch, tmp_path):
    """Create a temp DuckDB with all tables initialized."""
    db_path = str(tmp_path / "test.duckdb")
    monkeypatch.setattr("engine.config.DATA_DIR", str(tmp_path))
    monkeypatch.setattr("engine.config.DUCKDB_PATH", db_path)

    from engine.init_db import init_all_tables
    init_all_tables(db_path)
    return db_path


def test_parse_active_symbols():
    from engine.seed_duckdb import _parse_active_symbols, SEED_SQL_PATH

    if not os.path.isfile(SEED_SQL_PATH):
        pytest.skip("seed.sql not found")

    symbols = _parse_active_symbols(SEED_SQL_PATH)
    assert len(symbols) == 20

    codes = [s["code"] for s in symbols]
    assert "MES" in codes

    databento = [s for s in symbols if s["data_source"] == "DATABENTO"]
    fred = [s for s in symbols if s["data_source"] == "FRED"]
    assert len(databento) == 17
    assert len(fred) == 3


def test_parse_active_symbols_missing_file():
    from engine.seed_duckdb import _parse_active_symbols

    result = _parse_active_symbols("/nonexistent/path/seed.sql")
    assert result == []


def test_seed_symbols(tmp_db_with_tables):
    from engine.seed_duckdb import SEED_SQL_PATH, seed_symbols

    if not os.path.isfile(SEED_SQL_PATH):
        pytest.skip("seed.sql not found")

    conn = duckdb.connect(tmp_db_with_tables)
    count = seed_symbols(conn)
    conn.close()
    assert count == 20


def test_seed_symbols_idempotent(tmp_db_with_tables):
    from engine.seed_duckdb import SEED_SQL_PATH, seed_symbols

    if not os.path.isfile(SEED_SQL_PATH):
        pytest.skip("seed.sql not found")

    conn = duckdb.connect(tmp_db_with_tables)
    seed_symbols(conn)
    seed_symbols(conn)
    total = conn.execute("SELECT count(*) FROM symbols").fetchone()[0]
    conn.close()
    assert total == 20


def test_resolve_target_table():
    from engine.seed_duckdb import _resolve_target_table

    assert _resolve_target_table("cross_asset_data.parquet") == "cross_asset_1h"
    assert _resolve_target_table("ohlcv_1h_data.parquet") == "cross_asset_1h"
    assert _resolve_target_table("trades_2026.parquet") == "trades_raw"
    assert _resolve_target_table("ohlcv_1m_mes.parquet") == "mes_1m"
    assert _resolve_target_table("random_file.parquet") is None


def test_tables_with_unique_set():
    from engine.seed_duckdb import _TABLES_WITH_UNIQUE

    assert "mes_1m" in _TABLES_WITH_UNIQUE
    assert "cross_asset_1h" in _TABLES_WITH_UNIQUE
    assert "trades_raw" not in _TABLES_WITH_UNIQUE


def test_seed_bars_no_data_dir(tmp_db_with_tables, monkeypatch, tmp_path):
    monkeypatch.setattr("engine.config.DATA_DIR", str(tmp_path / "nonexistent"))
    from engine.seed_duckdb import seed_bars_from_files

    conn = duckdb.connect(tmp_db_with_tables)
    results = seed_bars_from_files(conn)
    conn.close()
    assert results == {}
