"""Tests for engine/indicators.py — ATR computation."""

from __future__ import annotations

import pytest

from engine.indicators import atr


def test_atr_basic():
    highs = [10.0, 11.0, 12.0, 11.5, 12.5]
    lows = [9.0, 9.5, 10.0, 10.0, 11.0]
    closes = [9.5, 10.5, 11.0, 10.5, 12.0]
    result = atr(highs, lows, closes, 3)
    assert result > 0


def test_atr_single_bar():
    result = atr([10.0], [9.0], [9.5], 1)
    assert result == pytest.approx(0.0)  # needs at least 2 bars for true range with gaps


def test_atr_empty():
    result = atr([], [], [], 14)
    assert result == pytest.approx(0.0)


def test_atr_fewer_bars_than_period():
    highs = [10.0, 11.0]
    lows = [9.0, 10.0]
    closes = [9.5, 10.5]
    result = atr(highs, lows, closes, 14)
    assert result > 0


def test_atr_true_range_includes_gaps():
    highs = [10.0, 15.0]
    lows = [9.0, 14.0]
    closes = [9.5, 14.5]
    result = atr(highs, lows, closes, 2)
    assert result > 1.0
