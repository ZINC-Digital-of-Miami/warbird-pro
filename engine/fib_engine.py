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
    1.618: "TP2",
    2.0: "TP3",
}

CONFLUENCE_LOOKBACKS = [8, 13, 21, 34, 55]
CONFLUENCE_RATIOS = [0.382, 0.5, 0.618]
CONFLUENCE_TOLERANCE = 0.001


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


def compute_fibs(bars: list[Bar]) -> FibState | None:
    """Compute fibonacci levels using multi-period confluence scoring.

    Examines multiple lookback windows, finds high/low anchors in each,
    then selects the anchor pair with the best confluence score (how many
    key fib ratios from different periods agree).
    """
    n = len(bars)
    min_lookback = CONFLUENCE_LOOKBACKS[0]  # 8
    if n < min_lookback:
        return None

    highs = [b.high for b in bars]
    lows = [b.low for b in bars]
    closes = [b.close for b in bars]

    # Check minimum fib range.
    atr_val = compute_atr(highs, lows, closes, 14)
    min_range = atr_val * MIN_FIB_RANGE_ATR

    @dataclass
    class PeriodAnchor:
        period: int
        high: float
        low: float
        fib_range: float
        mid_levels: list[float]

    anchors: list[PeriodAnchor] = []

    for period in CONFLUENCE_LOOKBACKS:
        start_idx = n - period
        if start_idx < 0:
            continue

        high = -math.inf
        low = math.inf
        for i in range(start_idx, n):
            if highs[i] > high:
                high = highs[i]
            if lows[i] < low:
                low = lows[i]

        fib_range = high - low
        if fib_range <= 0 or fib_range < min_range:
            continue

        mid_levels = [low + fib_range * r for r in CONFLUENCE_RATIOS]
        anchors.append(PeriodAnchor(
            period=period, high=high, low=low,
            fib_range=fib_range, mid_levels=mid_levels,
        ))

    if not anchors:
        return None

    # Score each anchor by confluence with other periods.
    best_anchor = anchors[-1]
    best_score = -1.0

    for i, anchor in enumerate(anchors):
        tolerance = anchor.fib_range * CONFLUENCE_TOLERANCE
        confluence_count = 0
        for j, other in enumerate(anchors):
            if i == j:
                continue
            for level_a in anchor.mid_levels:
                for level_b in other.mid_levels:
                    if abs(level_a - level_b) <= tolerance:
                        confluence_count += 1

        score = confluence_count * anchor.fib_range
        if score > best_score or (
            math.isclose(score, best_score, abs_tol=1e-9)
            and anchor.fib_range > best_anchor.fib_range
        ):
            best_score = score
            best_anchor = anchor

    # Direction via midpoint with hysteresis.
    last_close = closes[-1]
    midpoint = best_anchor.low + best_anchor.fib_range * 0.5
    hysteresis = best_anchor.fib_range * (MIDPOINT_HYSTERESIS_PCT / 100.0)
    is_bullish = last_close >= (midpoint - hysteresis)

    levels = _build_levels(best_anchor.high, best_anchor.low, is_bullish)

    return FibState(
        levels=levels,
        anchor_high=best_anchor.high,
        anchor_low=best_anchor.low,
        is_bullish=is_bullish,
        fib_range=best_anchor.fib_range,
    )
