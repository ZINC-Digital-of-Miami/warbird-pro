"""Fibonacci engine — ZigZag-based anchor detection with multi-period confluence.

Combines the V9 Pine ZigZag logic (deviation/depth) with the TypeScript
multi-period confluence scoring (lookbacks 8/13/21/34/55).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from engine.bar_store import Bar
from engine.config import (
    FIB_EXTENSIONS,
    FIB_RATIOS,
    MIDPOINT_HYSTERESIS_PCT,
    MIN_FIB_RANGE_ATR,
    ZIGZAG_DEPTH,
    ZIGZAG_DEVIATION,
    ZIGZAG_THRESHOLD_FLOOR_PCT,
)
from engine.indicators import atr as compute_atr


@dataclass
class FibLevel:
    ratio: float
    price: float
    label: str
    is_extension: bool


@dataclass
class FibState:
    levels: list[FibLevel]
    anchor_high: float
    anchor_low: float
    anchor_high_time: int  # unix timestamp of the bar with the high
    anchor_low_time: int   # unix timestamp of the bar with the low
    is_bullish: bool
    fib_range: float

    def to_dict(self) -> dict:
        return {
            "levels": [
                {"ratio": lv.ratio, "price": lv.price, "label": lv.label, "isExtension": lv.is_extension}
                for lv in self.levels
            ],
            "anchorHigh": self.anchor_high,
            "anchorLow": self.anchor_low,
            "anchorHighTime": self.anchor_high_time,
            "anchorLowTime": self.anchor_low_time,
            "isBullish": self.is_bullish,
            "fibRange": self.fib_range,
        }


FIB_LABELS: dict[float, str] = {
    0: "0",
    0.236: ".236",
    0.382: ".382",
    0.5: "Pivot",
    0.618: ".618",
    0.786: ".786",
    1.0: "1",
    1.236: "TP1",
    1.382: "1.382",
    1.5: "1.5",
    1.618: "TP2",
    2.0: "TP3",
    2.236: "TP4",
}

CONFLUENCE_LOOKBACKS = [8, 13, 21, 34, 55]
CONFLUENCE_RATIOS = [0.382, 0.5, 0.618]
CONFLUENCE_TOLERANCE = 0.001


@dataclass
class _PeriodAnchor:
    period: int
    high: float
    low: float
    high_idx: int
    low_idx: int
    fib_range: float
    mid_levels: list[float]


def _build_levels(anchor_high: float, anchor_low: float, is_bullish: bool) -> list[FibLevel]:
    fib_range = anchor_high - anchor_low
    levels: list[FibLevel] = []
    for ratio in FIB_RATIOS:
        price = anchor_low + fib_range * ratio if is_bullish else anchor_high - fib_range * ratio
        levels.append(FibLevel(
            ratio=ratio,
            price=round(price, 2),
            label=FIB_LABELS.get(ratio, str(ratio)),
            is_extension=False,
        ))
    for ratio in FIB_EXTENSIONS:
        price = anchor_low + fib_range * ratio if is_bullish else anchor_high - fib_range * ratio
        levels.append(FibLevel(
            ratio=ratio,
            price=round(price, 2),
            label=FIB_LABELS.get(ratio, str(ratio)),
            is_extension=True,
        ))
    return levels


def _find_period_anchors(
    highs: list[float], lows: list[float], n: int, min_range: float,
) -> list[_PeriodAnchor]:
    """Scan each lookback window and return anchors that meet the min range."""
    anchors: list[_PeriodAnchor] = []
    for period in CONFLUENCE_LOOKBACKS:
        start_idx = n - period
        if start_idx < 0:
            continue

        high = -math.inf
        low = math.inf
        high_idx = start_idx
        low_idx = start_idx
        for i in range(start_idx, n):
            if highs[i] > high:
                high = highs[i]
                high_idx = i
            if lows[i] < low:
                low = lows[i]
                low_idx = i

        fib_range = high - low
        if fib_range <= 0 or fib_range < min_range:
            continue

        mid_levels = [low + fib_range * r for r in CONFLUENCE_RATIOS]
        anchors.append(_PeriodAnchor(
            period=period, high=high, low=low,
            high_idx=high_idx, low_idx=low_idx,
            fib_range=fib_range, mid_levels=mid_levels,
        ))
    return anchors


def _score_anchor(anchor: _PeriodAnchor, all_anchors: list[_PeriodAnchor]) -> float:
    """Score an anchor by how many fib levels agree with other periods."""
    tolerance = anchor.fib_range * CONFLUENCE_TOLERANCE
    confluence_count = 0
    for other in all_anchors:
        if other is anchor:
            continue
        for level_a in anchor.mid_levels:
            for level_b in other.mid_levels:
                if abs(level_a - level_b) <= tolerance:
                    confluence_count += 1
    return confluence_count * anchor.fib_range


def _select_best_anchor(anchors: list[_PeriodAnchor]) -> _PeriodAnchor:
    """Select the anchor with the highest confluence score, breaking ties by range."""
    best = anchors[-1]
    best_score = -1.0
    for anchor in anchors:
        score = _score_anchor(anchor, anchors)
        if score > best_score or (
            math.isclose(score, best_score, abs_tol=1e-9)
            and anchor.fib_range > best.fib_range
        ):
            best_score = score
            best = anchor
    return best


def compute_fibs(bars: list[Bar]) -> FibState | None:
    """Compute fibonacci levels using multi-period confluence scoring.

    Examines multiple lookback windows, finds high/low anchors in each,
    then selects the anchor pair with the best confluence score (how many
    key fib ratios from different periods agree).
    """
    n = len(bars)
    if n < CONFLUENCE_LOOKBACKS[0]:
        return None

    highs = [b.high for b in bars]
    lows = [b.low for b in bars]
    closes = [b.close for b in bars]

    atr_val = compute_atr(highs, lows, closes, 14)
    min_range = atr_val * MIN_FIB_RANGE_ATR

    anchors = _find_period_anchors(highs, lows, n, min_range)
    if not anchors:
        return None

    best_anchor = _select_best_anchor(anchors)

    midpoint = best_anchor.low + best_anchor.fib_range * 0.5
    hysteresis = best_anchor.fib_range * (MIDPOINT_HYSTERESIS_PCT / 100.0)
    is_bullish = closes[-1] >= (midpoint - hysteresis)

    levels = _build_levels(best_anchor.high, best_anchor.low, is_bullish)

    return FibState(
        levels=levels,
        anchor_high=best_anchor.high,
        anchor_low=best_anchor.low,
        anchor_high_time=int(bars[best_anchor.high_idx].ts.timestamp()),
        anchor_low_time=int(bars[best_anchor.low_idx].ts.timestamp()),
        is_bullish=is_bullish,
        fib_range=best_anchor.fib_range,
    )
