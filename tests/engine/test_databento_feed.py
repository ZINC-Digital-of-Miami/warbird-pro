"""Tests for engine/databento_feed.py — gap-fill, contract roll, feed lifecycle."""

from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from engine.bar_store import Bar, BarStore
from engine.databento_feed import (
    _connect_and_subscribe,
    _consume_records,
    _record_to_bar,
    active_mes_contract,
    backfill,
    compute_gap_hours,
    detect_contract_roll,
    gap_fill_decision,
    start_feed,
    stop_feed,
    stream_live,
)


# ── Gap-fill cost cap tests ───────────────────────────────────────────────────


def test_gap_fill_auto():
    assert gap_fill_decision(1.0) == "auto"
    assert gap_fill_decision(5.9) == "auto"


def test_gap_fill_warn():
    assert gap_fill_decision(6.0) == "warn"
    assert gap_fill_decision(12.0) == "warn"
    assert gap_fill_decision(24.0) == "warn"


def test_gap_fill_refuse():
    assert gap_fill_decision(24.1) == "refuse"
    assert gap_fill_decision(48.0) == "refuse"
    assert gap_fill_decision(float("inf")) == "refuse"


def test_compute_gap_hours_none():
    assert compute_gap_hours(None) == float("inf")


def test_compute_gap_hours_recent():
    now = datetime.now(timezone.utc)
    result = compute_gap_hours(now)
    assert result < 0.01


# ── Contract roll detection ───────────────────────────────────────────────────


def test_active_mes_contract_format():
    contract = active_mes_contract()
    assert contract.startswith("MES")
    assert len(contract) == 6  # e.g. MESM26
    assert contract[3] in "HMUZ"


def test_detect_contract_roll_returns_bool():
    result = detect_contract_roll()
    assert isinstance(result, bool)


@pytest.mark.parametrize("fake_now,expected", [
    # Pre-roll: June 8 2026 (before customary roll week) → MESM26
    (datetime(2026, 6, 8, 12, 0, tzinfo=timezone.utc), "MESM26"),
    # Pre-roll: June 12 2026 (Friday before customary roll Monday) → MESM26
    (datetime(2026, 6, 12, 12, 0, tzinfo=timezone.utc), "MESM26"),
    # On customary roll date: June 15 2026 (Monday) → MESU26
    (datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc), "MESU26"),
    # Post-roll: June 16 2026 (Tuesday after roll date) → MESU26
    (datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc), "MESU26"),
    # Dec post-roll: Dec 14 2026 (Monday before 3rd Friday) → advances to MESH27
    (datetime(2026, 12, 14, 12, 0, tzinfo=timezone.utc), "MESH27"),
    # Non-roll month mid-quarter: Apr 15 2026 → MESM26
    (datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc), "MESM26"),
])
def test_active_mes_contract_date_parametrized(fake_now, expected):
    """active_mes_contract() follows customary roll week for calendar diagnostics."""
    with patch("engine.databento_feed.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = active_mes_contract()
    assert result == expected, f"For {fake_now.date()}: expected {expected}, got {result}"


def test_detect_contract_roll_non_calendar_rule_returns_false():
    fake_now = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
    with patch("engine.databento_feed.datetime") as mock_dt, \
         patch("engine.databento_feed.DATABENTO_CONTINUOUS_RULE", "n"):
        mock_dt.now.return_value = fake_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        assert detect_contract_roll() is False


def test_detect_contract_roll_calendar_rule_returns_true_in_roll_week():
    fake_now = datetime(2026, 6, 15, 12, 0, tzinfo=timezone.utc)
    with patch("engine.databento_feed.datetime") as mock_dt, \
         patch("engine.databento_feed.DATABENTO_CONTINUOUS_RULE", "c"):
        mock_dt.now.return_value = fake_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        assert detect_contract_roll() is True


# ── _record_to_bar conversion ─────────────────────────────────────────────────


def test_record_to_bar():
    """Convert a mock Databento OHLCVMsg record to a Bar."""
    ts_ns = int(datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc).timestamp() * 1e9)
    record = SimpleNamespace(
        ts_event=ts_ns,
        open=int(5400.0 * 1e9),
        high=int(5410.0 * 1e9),
        low=int(5390.0 * 1e9),
        close=int(5405.0 * 1e9),
        volume=150,
    )
    bar = _record_to_bar(record)
    assert bar.ts.year == 2026
    assert bar.open == pytest.approx(5400.0)
    assert bar.high == pytest.approx(5410.0)
    assert bar.low == pytest.approx(5390.0)
    assert bar.close == pytest.approx(5405.0)
    assert bar.volume == 150


# ── _connect_and_subscribe ────────────────────────────────────────────────────


def test_connect_and_subscribe():
    """_connect_and_subscribe creates a client and subscribes."""
    mock_db = MagicMock()
    mock_client = MagicMock()
    mock_db.Live.return_value = mock_client

    with patch("engine.databento_feed.DATABENTO_API_KEY", "test-key"), \
         patch("engine.databento_feed.DATABENTO_SYMBOL", "MES.n.0"), \
         patch("engine.databento_feed.DATABENTO_STYPE", "continuous"):
        result = _connect_and_subscribe(mock_db)

    mock_db.Live.assert_called_once_with(key="test-key")
    mock_client.subscribe.assert_called_once_with(
        dataset="GLBX.MDP3",
        schema="ohlcv-1m",
        stype_in="continuous",
        symbols=["MES.n.0"],
    )
    assert result is mock_client


# ── _consume_records ──────────────────────────────────────────────────────────


def test_consume_records_processes_bars():
    """_consume_records iterates records and adds bars to store."""
    store = BarStore(max_bars=100)
    stop = threading.Event()
    ts_ns = int(datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc).timestamp() * 1e9)

    records = [
        SimpleNamespace(
            ts_event=ts_ns + i * 60_000_000_000,
            open=int(5400.0 * 1e9),
            high=int(5410.0 * 1e9),
            low=int(5390.0 * 1e9),
            close=int(5405.0 * 1e9),
            volume=100 + i,
        )
        for i in range(3)
    ]

    _consume_records(records, store, stop)
    assert store.bar_count("1m") == 3


def test_consume_records_stops_on_event():
    """_consume_records exits when stop event is set."""
    store = BarStore(max_bars=100)
    stop = threading.Event()
    stop.set()

    ts_ns = int(datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc).timestamp() * 1e9)
    records = [
        SimpleNamespace(
            ts_event=ts_ns,
            open=int(5400.0 * 1e9),
            high=int(5410.0 * 1e9),
            low=int(5390.0 * 1e9),
            close=int(5405.0 * 1e9),
            volume=100,
        )
    ]

    _consume_records(records, store, stop)
    assert store.bar_count("1m") == 0


def test_consume_records_skips_no_ts_event():
    """_consume_records skips records without ts_event."""
    store = BarStore(max_bars=100)
    stop = threading.Event()

    records = [SimpleNamespace(other_field=123)]
    _consume_records(records, store, stop)
    assert store.bar_count("1m") == 0


# ── stream_live ───────────────────────────────────────────────────────────────


def test_stream_live_no_api_key():
    """stream_live exits immediately with no API key."""
    store = BarStore(max_bars=100)
    stop = threading.Event()
    with patch("engine.databento_feed.DATABENTO_API_KEY", ""):
        stream_live(store, stop)
    assert store.bar_count("1m") == 0


def test_stream_live_no_databento_package():
    """stream_live exits if databento package not available."""
    store = BarStore(max_bars=100)
    stop = threading.Event()
    with patch("engine.databento_feed.DATABENTO_API_KEY", "test-key"), \
         patch("builtins.__import__", side_effect=ImportError("no module")):
        stream_live(store, stop)


def test_stream_live_exhausts_retries():
    """stream_live gives up after RECONNECT_ATTEMPTS failures."""
    store = BarStore(max_bars=100)
    stop = threading.Event()

    mock_db_module = MagicMock()
    mock_db_module.Live.side_effect = Exception("connection failed")

    with patch("engine.databento_feed.DATABENTO_API_KEY", "test-key"), \
         patch("engine.databento_feed.RECONNECT_ATTEMPTS", 2), \
         patch("engine.databento_feed.BACKOFF_BASE_S", 0.01):
        import sys
        sys.modules["databento"] = mock_db_module
        try:
            stream_live(store, stop)
        finally:
            del sys.modules["databento"]


# ── backfill ──────────────────────────────────────────────────────────────────


def test_backfill_no_api_key():
    """backfill returns 0 with no API key."""
    store = BarStore(max_bars=100)
    with patch("engine.databento_feed.DATABENTO_API_KEY", ""):
        result = backfill(store)
    assert result == 0


def test_backfill_refuses_large_gap():
    """backfill returns 0 when gap exceeds 24h."""
    store = BarStore(max_bars=100)
    with patch("engine.databento_feed.DATABENTO_API_KEY", "test-key"), \
         patch("engine.databento_feed.compute_gap_hours", return_value=48.0):
        result = backfill(store)
    assert result == 0


def test_backfill_no_databento_package():
    """backfill returns 0 if databento not installed."""
    store = BarStore(max_bars=100)
    with patch("engine.databento_feed.DATABENTO_API_KEY", "test-key"), \
         patch("engine.databento_feed.compute_gap_hours", return_value=1.0), \
         patch("builtins.__import__", side_effect=ImportError("no module")):
        result = backfill(store)
    assert result == 0


def test_backfill_warns_medium_gap():
    """backfill proceeds with warning for 6-24h gap."""
    store = BarStore(max_bars=100)
    mock_historical = MagicMock()

    ts_ns = int(datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc).timestamp() * 1e9)
    mock_records = [
        SimpleNamespace(
            ts_event=ts_ns + i * 60_000_000_000,
            open=int(5400.0 * 1e9),
            high=int(5410.0 * 1e9),
            low=int(5390.0 * 1e9),
            close=int(5405.0 * 1e9),
            volume=100,
        )
        for i in range(5)
    ]
    mock_historical.timeseries.get_range.return_value = mock_records

    mock_db_module = MagicMock()
    mock_db_module.Historical.return_value = mock_historical

    with patch("engine.databento_feed.DATABENTO_API_KEY", "test-key"), \
         patch("engine.databento_feed.compute_gap_hours", return_value=12.0):
        # Patch the import inside backfill
        import sys
        sys.modules["databento"] = mock_db_module
        try:
            result = backfill(store, bars=5)
        finally:
            del sys.modules["databento"]
    assert result == 5


def test_backfill_handles_api_error():
    """backfill returns 0 on Historical API error."""
    store = BarStore(max_bars=100)
    mock_historical = MagicMock()
    mock_historical.timeseries.get_range.side_effect = Exception("API error")

    mock_db_module = MagicMock()
    mock_db_module.Historical.return_value = mock_historical

    with patch("engine.databento_feed.DATABENTO_API_KEY", "test-key"), \
         patch("engine.databento_feed.compute_gap_hours", return_value=1.0):
        import sys
        sys.modules["databento"] = mock_db_module
        try:
            result = backfill(store, bars=5)
        finally:
            del sys.modules["databento"]
    assert result == 0


# ── start_feed / stop_feed ────────────────────────────────────────────────────


def test_start_feed_returns_thread_and_event():
    """start_feed returns a thread and stop event."""
    store = BarStore(max_bars=100)
    with patch("engine.databento_feed.backfill") as mock_bf, \
         patch("engine.databento_feed.DATABENTO_API_KEY", ""):
        thread, stop = start_feed(store)
    assert isinstance(thread, threading.Thread)
    assert isinstance(stop, threading.Event)
    stop.set()
    thread.join(timeout=2)
    mock_bf.assert_called_once()


def test_stop_feed_sets_event_and_joins():
    """stop_feed signals the thread to stop."""
    stop = threading.Event()
    thread = threading.Thread(target=lambda: stop.wait(5), daemon=True)
    thread.start()
    stop_feed(thread, stop)
    assert stop.is_set()
    assert not thread.is_alive()


def test_stop_feed_none_args():
    """stop_feed handles None thread/event gracefully."""
    stop_feed(None, None)
