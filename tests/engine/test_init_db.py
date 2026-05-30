"""Tests for engine/init_db.py — DuckDB schema initialization."""

from __future__ import annotations

import os
import tempfile

import duckdb
import pytest


@pytest.fixture()
def tmp_db(monkeypatch, tmp_path):
    """Provide a temporary DuckDB path and patch engine.config paths."""
    db_path = str(tmp_path / "test.duckdb")
    monkeypatch.setattr("engine.config.DATA_DIR", str(tmp_path))
    monkeypatch.setattr("engine.config.DUCKDB_PATH", db_path)
    return db_path


def test_init_creates_all_tables(tmp_db):
    from engine.init_db import init_all_tables

    init_all_tables(tmp_db)
    conn = duckdb.connect(tmp_db)
    tables = [r[0] for r in conn.execute("SHOW TABLES").fetchall()]
    conn.close()

    assert len(tables) >= 35
    assert "mes_1m" in tables
    assert "trades_raw" in tables
    assert "cross_asset_1h" in tables
    assert "series_catalog" in tables
    assert "trades" in tables
    assert "symbols" in tables
    assert "warbird_daily_bias" in tables
    assert "ai_analysis_log" in tables


def test_init_is_idempotent(tmp_db):
    from engine.init_db import init_all_tables

    init_all_tables(tmp_db)
    init_all_tables(tmp_db)
    conn = duckdb.connect(tmp_db)
    tables = [r[0] for r in conn.execute("SHOW TABLES").fetchall()]
    conn.close()
    assert len(tables) >= 35


def test_trades_table_has_sequence(tmp_db):
    from engine.init_db import init_all_tables

    init_all_tables(tmp_db)
    conn = duckdb.connect(tmp_db)
    conn.execute(
        "INSERT INTO trades (opened_at, timeframe, direction, entry_price) "
        "VALUES (current_timestamp, '5m', 'LONG', 5400.0)"
    )
    row = conn.execute("SELECT id FROM trades").fetchone()
    conn.close()
    assert row[0] == 1


def test_bar_tables_have_primary_key(tmp_db):
    from engine.init_db import init_all_tables

    init_all_tables(tmp_db)
    conn = duckdb.connect(tmp_db)
    conn.execute(
        "INSERT INTO mes_1m (ts, open, high, low, close, volume) "
        "VALUES ('2026-01-01 00:00:00+00', 5400, 5410, 5390, 5405, 1000)"
    )
    with pytest.raises(duckdb.ConstraintException):
        conn.execute(
            "INSERT INTO mes_1m (ts, open, high, low, close, volume) "
            "VALUES ('2026-01-01 00:00:00+00', 5400, 5410, 5390, 5405, 1000)"
        )
    conn.close()


def test_symbols_table_schema(tmp_db):
    from engine.init_db import init_all_tables

    init_all_tables(tmp_db)
    conn = duckdb.connect(tmp_db)
    conn.execute(
        "INSERT INTO symbols (code, display_name, short_name, description, "
        "tick_size, data_source, is_active) "
        "VALUES ('MES.v.0', 'Micro E-mini S&P', 'MES', 'Test', 0.25, 'DATABENTO', true)"
    )
    row = conn.execute("SELECT code, is_active FROM symbols WHERE code='MES.v.0'").fetchone()
    conn.close()
    assert row[0] == "MES.v.0"
    assert row[1] is True
