"""Tests for engine/bar_store.py — Bar dataclass + multi-TF aggregation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from engine.bar_store import Bar, BarStore, validate_bar


# ── Bar dataclass tests ───────────────────────────────────────────────────────

def test_bar_creation():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0)
    assert bar.open == pytest.approx(5400.0)
    assert bar.high == pytest.approx(5410.0)
    assert bar.low == pytest.approx(5390.0)
    assert bar.close == pytest.approx(5405.0)
    assert bar.volume == 0


def test_bar_with_volume():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0, volume=1500)
    assert bar.volume == 1500


def test_bar_timestamp():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0)
    assert bar.ts.timestamp() > 0


def test_bar_to_dict():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0, volume=100)
    d = bar.to_dict()
    assert d["time"] == int(ts.timestamp())
    assert d["open"] == pytest.approx(5400.0)
    assert d["high"] == pytest.approx(5410.0)
    assert d["low"] == pytest.approx(5390.0)
    assert d["close"] == pytest.approx(5405.0)
    assert d["volume"] == 100


# ── Bar validation tests ──────────────────────────────────────────────────────

def test_validate_bar_valid():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)  # Wednesday
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0, volume=100)
    assert validate_bar(bar) is True


def test_validate_bar_negative_price():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bar = Bar(ts=ts, open=-1.0, high=5410.0, low=5390.0, close=5405.0)
    assert validate_bar(bar) is False


def test_validate_bar_zero_price():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bar = Bar(ts=ts, open=0.0, high=5410.0, low=5390.0, close=5405.0)
    assert validate_bar(bar) is False


def test_validate_bar_high_less_than_low():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bar = Bar(ts=ts, open=5400.0, high=5380.0, low=5390.0, close=5405.0)
    assert validate_bar(bar) is False


def test_validate_bar_saturday():
    ts = datetime(2026, 5, 30, 14, 30, tzinfo=timezone.utc)  # Saturday
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0)
    assert validate_bar(bar) is False


def test_validate_bar_sunday_before_open():
    ts = datetime(2026, 5, 31, 12, 0, tzinfo=timezone.utc)  # Sunday 12:00 UTC
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0)
    assert validate_bar(bar) is False


def test_validate_bar_sunday_after_open():
    ts = datetime(2026, 5, 31, 23, 0, tzinfo=timezone.utc)  # Sunday 23:00 UTC = 18:00 CT (after CME open)
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0)
    assert validate_bar(bar) is True


# ── BarStore multi-TF aggregation tests ───────────────────────────────────────

def _make_bar(minute_offset: int, base_ts: datetime | None = None) -> Bar:
    """Helper to create a bar at a given minute offset."""
    if base_ts is None:
        base_ts = datetime(2026, 5, 28, 14, 0, tzinfo=timezone.utc)
    ts = base_ts + timedelta(minutes=minute_offset)
    return Bar(
        ts=ts,
        open=5400.0 + minute_offset,
        high=5410.0 + minute_offset,
        low=5390.0 + minute_offset,
        close=5405.0 + minute_offset,
        volume=100 + minute_offset,
    )


def test_store_add_1m_bar():
    store = BarStore(max_bars=100)
    bar = _make_bar(0)
    result = store.add_1m_bar(bar)
    assert result is True
    assert store.bar_count("1m") == 1


def test_store_3m_aggregation():
    store = BarStore(max_bars=100)
    for i in range(3):
        store.add_1m_bar(_make_bar(i))
    assert store.bar_count("3m") == 1
    bar_3m = store.get_bars("3m")[0]
    assert bar_3m.open == pytest.approx(5400.0)
    assert bar_3m.close == pytest.approx(5407.0)
    assert bar_3m.high == pytest.approx(5412.0)
    assert bar_3m.low == pytest.approx(5390.0)
    assert bar_3m.volume == 303


def test_store_5m_aggregation():
    store = BarStore(max_bars=100)
    for i in range(5):
        store.add_1m_bar(_make_bar(i))
    assert store.bar_count("5m") == 1


def test_store_15m_aggregation():
    store = BarStore(max_bars=100)
    for i in range(15):
        store.add_1m_bar(_make_bar(i))
    assert store.bar_count("15m") == 1
    bar_15m = store.get_bars("15m")[0]
    assert bar_15m.open == pytest.approx(5400.0)
    assert bar_15m.close == pytest.approx(5419.0)
    assert bar_15m.volume == 1605


def test_store_1h_aggregation():
    store = BarStore(max_bars=5000)
    for i in range(60):
        store.add_1m_bar(_make_bar(i))
    assert store.bar_count("1h") == 1


def test_store_4h_aggregation():
    store = BarStore(max_bars=5000)
    for i in range(240):
        store.add_1m_bar(_make_bar(i))
    assert store.bar_count("4h") == 1


def test_store_1d_aggregation():
    store = BarStore(max_bars=5000)
    for i in range(1440):
        store.add_1m_bar(_make_bar(i))
    assert store.bar_count("1d") == 1


def test_store_callback_fires():
    store = BarStore(max_bars=100)
    received = []
    store.on_bar(lambda tf, bar: received.append((tf, bar)))
    store.add_1m_bar(_make_bar(0))
    assert len(received) == 1
    assert received[0][0] == "1m"


def test_store_callback_fires_on_aggregation():
    store = BarStore(max_bars=100)
    received = []
    store.on_bar(lambda tf, bar: received.append(tf))
    for i in range(3):
        store.add_1m_bar(_make_bar(i))
    assert "1m" in received
    assert "3m" in received


def test_store_backfill():
    store = BarStore(max_bars=5000)
    bars = [_make_bar(i) for i in range(60)]
    loaded = store.backfill("1m", bars)
    assert loaded == 60
    assert store.bar_count("1m") == 60
    assert store.bar_count("3m") == 20
    assert store.bar_count("5m") == 12
    assert store.bar_count("15m") == 4
    assert store.bar_count("1h") == 1


def test_store_invalid_bar_rejected():
    store = BarStore(max_bars=100)
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bad_bar = Bar(ts=ts, open=-1.0, high=5410.0, low=5390.0, close=5405.0)
    result = store.add_1m_bar(bad_bar)
    assert result is False
    assert store.bar_count("1m") == 0


def test_store_total_ingested():
    store = BarStore(max_bars=100)
    for i in range(5):
        store.add_1m_bar(_make_bar(i))
    assert store.total_bars_ingested == 5


def test_store_last_bar():
    store = BarStore(max_bars=100)
    bar = _make_bar(5)
    store.add_1m_bar(bar)
    last = store.last_bar("1m")
    assert last is not None
    assert last.close == bar.close


def test_store_last_bar_empty():
    store = BarStore(max_bars=100)
    assert store.last_bar("1m") is None
