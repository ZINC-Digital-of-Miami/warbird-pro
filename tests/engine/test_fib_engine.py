"""Tests for engine/fib_engine.py — fibonacci confluence scoring."""

from __future__ import annotations

from datetime import datetime, timezone

from engine.bar_store import Bar
from engine.fib_engine import (
    CONFLUENCE_LOOKBACKS,
    CONFLUENCE_RATIOS,
    CONFLUENCE_TOLERANCE,
    FibState,
    _PeriodAnchor,
    _build_levels,
    _find_period_anchors,
    _score_anchor,
    _select_best_anchor,
    compute_fibs,
)


def _make_bars(prices: list[tuple[float, float, float, float]], start_ts: int = 1700000000) -> list[Bar]:
    """Create Bar objects from (open, high, low, close) tuples."""
    return [
        Bar(
            ts=datetime.fromtimestamp(start_ts + i * 300, tz=timezone.utc),
            open=p[0], high=p[1], low=p[2], close=p[3],
        )
        for i, p in enumerate(prices)
    ]


def _make_trending_bars(n: int, start: float = 5400.0, step: float = 2.0) -> list[Bar]:
    """Create n bars with a simple uptrend."""
    bars = []
    price = start
    for i in range(n):
        o = price
        h = price + 5.0
        l = price - 3.0
        c = price + step
        bars.append(Bar(
            ts=datetime.fromtimestamp(1700000000 + i * 300, tz=timezone.utc),
            open=o, high=h, low=l, close=c,
        ))
        price = c
    return bars


def test_compute_fibs_returns_none_for_short_bars():
    bars = _make_trending_bars(3)
    assert compute_fibs(bars) is None


def test_compute_fibs_returns_fib_state():
    bars = _make_trending_bars(60)
    result = compute_fibs(bars)
    assert result is not None
    assert isinstance(result, FibState)
    assert len(result.levels) > 0
    assert result.fib_range > 0
    assert result.anchor_high > result.anchor_low


def test_compute_fibs_has_correct_level_count():
    bars = _make_trending_bars(60)
    result = compute_fibs(bars)
    assert result is not None
    retracements = [lv for lv in result.levels if not lv.is_extension]
    extensions = [lv for lv in result.levels if lv.is_extension]
    assert len(retracements) == 7
    assert len(extensions) == 6


def test_build_levels_bullish():
    levels = _build_levels(5500.0, 5400.0, is_bullish=True)
    prices = [lv.price for lv in levels]
    assert 5400.0 in prices
    assert 5500.0 in prices
    pivot = next(lv for lv in levels if lv.label == "Pivot")
    assert pivot.price == 5450.0


def test_build_levels_bearish():
    levels = _build_levels(5500.0, 5400.0, is_bullish=False)
    pivot = next(lv for lv in levels if lv.label == "Pivot")
    assert pivot.price == 5450.0


def test_find_period_anchors_filters_small_ranges():
    highs = [100.0] * 20
    lows = [99.99] * 20
    anchors = _find_period_anchors(highs, lows, 20, min_range=1.0)
    assert len(anchors) == 0


def test_find_period_anchors_finds_valid_ranges():
    highs = [5500.0] * 60
    lows = [5400.0] * 60
    anchors = _find_period_anchors(highs, lows, 60, min_range=1.0)
    assert len(anchors) > 0
    for a in anchors:
        assert a.fib_range == 100.0
        assert a.period in CONFLUENCE_LOOKBACKS


def test_score_anchor_self_excluded():
    anchor = _PeriodAnchor(
        period=8, high=5500, low=5400, high_idx=0, low_idx=1,
        fib_range=100.0, mid_levels=[5438.2, 5450.0, 5461.8],
    )
    score = _score_anchor(anchor, [anchor])
    assert score == 0.0


def test_score_anchor_with_confluence():
    a1 = _PeriodAnchor(
        period=8, high=5500, low=5400, high_idx=0, low_idx=1,
        fib_range=100.0, mid_levels=[5438.2, 5450.0, 5461.8],
    )
    a2 = _PeriodAnchor(
        period=13, high=5500, low=5400, high_idx=0, low_idx=1,
        fib_range=100.0, mid_levels=[5438.2, 5450.0, 5461.8],
    )
    score = _score_anchor(a1, [a1, a2])
    assert score > 0


def test_select_best_anchor():
    a1 = _PeriodAnchor(
        period=8, high=5500, low=5400, high_idx=0, low_idx=1,
        fib_range=100.0, mid_levels=[5438.2, 5450.0, 5461.8],
    )
    a2 = _PeriodAnchor(
        period=13, high=5600, low=5400, high_idx=0, low_idx=1,
        fib_range=200.0, mid_levels=[5476.4, 5500.0, 5523.6],
    )
    best = _select_best_anchor([a1, a2])
    assert best is not None


def test_confluence_constants():
    assert CONFLUENCE_LOOKBACKS == [8, 13, 21, 34, 55]
    assert CONFLUENCE_RATIOS == [0.382, 0.5, 0.618]
    assert CONFLUENCE_TOLERANCE == 0.001


def test_fib_state_to_dict():
    bars = _make_trending_bars(60)
    result = compute_fibs(bars)
    assert result is not None
    d = result.to_dict()
    assert "levels" in d
    assert "anchorHigh" in d
    assert "anchorLow" in d
    assert "isBullish" in d
    assert "fibRange" in d
    assert isinstance(d["levels"], list)
    assert all("ratio" in lv for lv in d["levels"])


def test_compute_fibs_direction_bullish():
    bars = _make_trending_bars(60, start=5400.0, step=3.0)
    result = compute_fibs(bars)
    assert result is not None
    assert result.is_bullish is True


def test_compute_fibs_direction_bearish():
    bars = _make_trending_bars(60, start=5600.0, step=-3.0)
    result = compute_fibs(bars)
    assert result is not None
    assert result.is_bullish is False
