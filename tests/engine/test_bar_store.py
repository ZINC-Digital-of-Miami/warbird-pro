"""Tests for engine/bar_store.py — Bar dataclass."""

from __future__ import annotations

from datetime import datetime, timezone

from engine.bar_store import Bar


def test_bar_creation():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0)
    assert bar.open == 5400.0
    assert bar.high == 5410.0
    assert bar.low == 5390.0
    assert bar.close == 5405.0
    assert bar.volume == 0


def test_bar_with_volume():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0, volume=1500)
    assert bar.volume == 1500


def test_bar_timestamp():
    ts = datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc)
    bar = Bar(ts=ts, open=5400.0, high=5410.0, low=5390.0, close=5405.0)
    assert bar.ts.timestamp() > 0
