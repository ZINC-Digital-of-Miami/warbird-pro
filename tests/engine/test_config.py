"""Tests for engine/config.py — configuration constants and paths."""

from __future__ import annotations

import os


def test_data_dir_is_absolute():
    from engine.config import DATA_DIR
    assert os.path.isabs(DATA_DIR)


def test_duckdb_path_under_data_dir():
    from engine.config import DATA_DIR, DUCKDB_PATH
    assert DUCKDB_PATH.startswith(DATA_DIR)
    assert DUCKDB_PATH.endswith(".duckdb")


def test_trade_log_db_equals_duckdb_path():
    from engine.config import DUCKDB_PATH, TRADE_LOG_DB
    assert TRADE_LOG_DB == DUCKDB_PATH


def test_databento_approved_symbols():
    from engine.config import DATABENTO_APPROVED_SYMBOLS
    assert isinstance(DATABENTO_APPROVED_SYMBOLS, list)
    assert len(DATABENTO_APPROVED_SYMBOLS) == 17
    assert "MES.v.0" in DATABENTO_APPROVED_SYMBOLS


def test_databento_approved_schemas():
    from engine.config import DATABENTO_APPROVED_SCHEMAS
    assert "ohlcv-1m" in DATABENTO_APPROVED_SCHEMAS
    assert "ohlcv-1h" in DATABENTO_APPROVED_SCHEMAS
    assert "trades" in DATABENTO_APPROVED_SCHEMAS


def test_lifecycle_constants():
    from engine.config import BACKOFF_BASE_S, COOLDOWN_PERIOD_S, RECONNECT_ATTEMPTS
    assert COOLDOWN_PERIOD_S == 60
    assert RECONNECT_ATTEMPTS == 3
    assert BACKOFF_BASE_S == 2.0


def test_cost_cap_rules():
    from engine.config import GAP_FILL_AUTO_HOURS, GAP_FILL_WARN_HOURS
    assert GAP_FILL_AUTO_HOURS == 6
    assert GAP_FILL_WARN_HOURS == 24
    assert GAP_FILL_AUTO_HOURS < GAP_FILL_WARN_HOURS


def test_canonical_timeframes():
    from engine.config import CANONICAL_TIMEFRAMES, DEFAULT_TIMEFRAME
    assert "5m" in CANONICAL_TIMEFRAMES
    assert "1m" in CANONICAL_TIMEFRAMES
    assert "1d" in CANONICAL_TIMEFRAMES
    assert DEFAULT_TIMEFRAME == "5m"


def test_engine_states():
    from engine.config import ENGINE_STATES
    assert "COLD" in ENGINE_STATES
    assert "WARM" in ENGINE_STATES
    assert len(ENGINE_STATES) == 4


def test_correlation_symbols():
    from engine.config import CORRELATION_SYMBOLS
    assert "NQ" in CORRELATION_SYMBOLS
    assert "CL" in CORRELATION_SYMBOLS


def test_api_keys_default_empty():
    from engine.config import DATABENTO_API_KEY, FRED_API_KEY
    assert isinstance(DATABENTO_API_KEY, str)
    assert isinstance(FRED_API_KEY, str)


def test_fib_constants():
    from engine.config import (
        FIB_EXTENSIONS,
        FIB_RATIOS,
        MIDPOINT_HYSTERESIS_PCT,
        MIN_FIB_RANGE_ATR,
        ZIGZAG_DEPTH,
        ZIGZAG_DEVIATION,
        ZIGZAG_THRESHOLD_FLOOR_PCT,
    )
    assert ZIGZAG_DEVIATION == 3.0
    assert ZIGZAG_DEPTH == 10
    assert ZIGZAG_THRESHOLD_FLOOR_PCT == 0.25
    assert MIN_FIB_RANGE_ATR == 0.5
    assert MIDPOINT_HYSTERESIS_PCT == 2.0
    assert 0.618 in FIB_RATIOS
    assert 1.618 in FIB_EXTENSIONS
