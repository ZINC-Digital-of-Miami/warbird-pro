"""Trigger engine — determines WHETHER price is actually reversing at a fib zone.

Ported from scripts/warbird/trigger-15m.ts.  Uses 1m microstructure
(rejection wicks, volume spikes, engulfing, momentum shift) plus
TTM Squeeze to produce a scored GO / WAIT / NO_GO decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from engine.bar_store import Bar
from engine.config import (
    MES_TICK,
    REJECTION_WICK_RATIO,
    TRIGGER_GO_THRESHOLD,
    TRIGGER_LOOKBACK_1M,
    TRIGGER_WAIT_THRESHOLD,
    VOLUME_BASELINE_BARS,
    ZONE_PROXIMITY_PTS,
)
from engine.fib_engine import FibState
from engine.indicators import rsi, ttm_squeeze


@dataclass
class TriggerResult:
    decision: Literal["GO", "WAIT", "NO_GO"]
    score: float
    direction: Literal["LONG", "SHORT"]
    fib_ratio: float | None
    fib_level: float | None
    entry_price: float | None
    stop_loss: float | None
    tp1: float | None
    tp2: float | None
    rr: float | None
    # Feature breakdown.
    rejection_wick: bool
    volume_spike: bool
    volume_ratio: float
    engulfing: bool
    momentum_shift: bool
    squeeze_on: bool
    squeeze_momentum: float
    rsi_value: float

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "score": round(self.score, 3),
            "direction": self.direction,
            "fibRatio": self.fib_ratio,
            "fibLevel": self.fib_level,
            "entryPrice": self.entry_price,
            "stopLoss": self.stop_loss,
            "tp1": self.tp1,
            "tp2": self.tp2,
            "rr": self.rr,
            "rejectionWick": self.rejection_wick,
            "volumeSpike": self.volume_spike,
            "volumeRatio": self.volume_ratio,
            "engulfing": self.engulfing,
            "momentumShift": self.momentum_shift,
            "squeezeOn": self.squeeze_on,
            "squeezeMomentum": self.squeeze_momentum,
            "rsiValue": round(self.rsi_value, 1),
        }


def _round_tick(price: float) -> float:
    return round(round(price / MES_TICK) * MES_TICK, 2)


def evaluate_trigger(
    bars_1m: list[Bar],
    fibs: FibState,
    direction: Literal["LONG", "SHORT"],
) -> TriggerResult:
    """Score whether the most recent 1m bars show a real reversal at a fib zone."""

    closes = [b.close for b in bars_1m]
    highs = [b.high for b in bars_1m]
    lows = [b.low for b in bars_1m]
    volumes = [b.volume for b in bars_1m]

    # Find the closest fib level within the zone proximity.
    last_close = closes[-1] if closes else 0.0
    target_level: float | None = None
    target_ratio: float | None = None
    min_dist = ZONE_PROXIMITY_PTS + 1

    for lv in fibs.levels:
        if lv.is_extension:
            continue
        if lv.ratio in (0, 1.0):
            continue
        dist = abs(last_close - lv.price)
        if dist < min_dist:
            min_dist = dist
            target_level = lv.price
            target_ratio = lv.ratio

    if target_level is None or min_dist > ZONE_PROXIMITY_PTS:
        return TriggerResult(
            decision="NO_GO", score=0.0, direction=direction,
            fib_ratio=None, fib_level=None, entry_price=None,
            stop_loss=None, tp1=None, tp2=None, rr=None,
            rejection_wick=False, volume_spike=False, volume_ratio=0,
            engulfing=False, momentum_shift=False, squeeze_on=False,
            squeeze_momentum=0, rsi_value=50,
        )

    n = len(bars_1m)
    zone_bars = bars_1m[-min(TRIGGER_LOOKBACK_1M, n):]

    # ── Feature Detection ─────────────────────────────────────────────────

    # 1. Rejection wick.
    last_bar = zone_bars[-1]
    body = abs(last_bar.close - last_bar.open)
    if body < MES_TICK:
        body = MES_TICK
    if direction == "LONG":
        wick = last_bar.close - last_bar.low
    else:
        wick = last_bar.high - last_bar.close
    rejection_wick = (wick / body) >= REJECTION_WICK_RATIO

    # 2. Volume spike.
    baseline_vols = volumes[-VOLUME_BASELINE_BARS - 1:-1] if n > VOLUME_BASELINE_BARS else volumes[:-1]
    avg_vol = sum(baseline_vols) / len(baseline_vols) if baseline_vols else 1
    volume_ratio = volumes[-1] / avg_vol if avg_vol > 0 else 0
    volume_spike = volume_ratio >= 1.5

    # 3. Engulfing.
    engulfing = False
    if len(zone_bars) >= 2:
        prev = zone_bars[-2]
        curr = zone_bars[-1]
        if direction == "LONG":
            engulfing = curr.close > curr.open and curr.close > prev.open and curr.open < prev.close
        else:
            engulfing = curr.close < curr.open and curr.close < prev.open and curr.open > prev.close

    # 4. Momentum shift.
    momentum_shift = False
    if len(zone_bars) >= 3:
        prev_delta = zone_bars[-2].close - zone_bars[-3].close
        curr_delta = zone_bars[-1].close - zone_bars[-2].close
        if direction == "LONG":
            momentum_shift = prev_delta < 0 and curr_delta > 0
        else:
            momentum_shift = prev_delta > 0 and curr_delta < 0

    # 5. TTM Squeeze.
    sq = ttm_squeeze(closes, highs, lows)

    # 6. RSI.
    rsi_value = rsi(closes)

    # ── Scoring ───────────────────────────────────────────────────────────
    # Weighted scoring (matches the TS trigger engine structure).
    score = 0.0

    # Primary: rejection wick + volume (0-0.40)
    if rejection_wick:
        score += 0.20
    if volume_spike:
        score += 0.15
    elif volume_ratio >= 1.2:
        score += 0.08
    if engulfing:
        score += 0.05

    # Secondary: squeeze + momentum (0-0.25)
    if sq.squeeze_on:
        aligned = (direction == "LONG" and sq.momentum_direction > 0) or (
            direction == "SHORT" and sq.momentum_direction < 0
        )
        if aligned:
            score += 0.20
        else:
            score += 0.10
    else:
        if momentum_shift:
            score += 0.10

    # Tertiary: RSI at extreme (0-0.15)
    if direction == "LONG" and rsi_value < 35:
        score += 0.15
    elif direction == "SHORT" and rsi_value > 65:
        score += 0.15
    elif direction == "LONG" and rsi_value < 45:
        score += 0.08
    elif direction == "SHORT" and rsi_value > 55:
        score += 0.08

    # Zone proximity bonus (0-0.10)
    proximity_bonus = max(0, 1.0 - min_dist / ZONE_PROXIMITY_PTS) * 0.10
    score += proximity_bonus

    # Volume ratio continuous bonus (0-0.10)
    vol_bonus = min(volume_ratio / 3.0, 1.0) * 0.10
    score += vol_bonus

    # Clamp.
    score = min(score, 1.0)

    # ── Decision ──────────────────────────────────────────────────────────
    if score >= TRIGGER_GO_THRESHOLD:
        decision: Literal["GO", "WAIT", "NO_GO"] = "GO"
    elif score >= TRIGGER_WAIT_THRESHOLD:
        decision = "WAIT"
    else:
        decision = "NO_GO"

    # ── Entry / SL / TP ──────────────────────────────────────────────────
    entry_price = _round_tick(last_close)
    fib_range = fibs.fib_range
    if direction == "LONG":
        stop_loss = _round_tick(entry_price - fib_range * 0.236)
        tp1 = _round_tick(entry_price + fib_range * 0.618)
        tp2 = _round_tick(entry_price + fib_range * 1.0)
    else:
        stop_loss = _round_tick(entry_price + fib_range * 0.236)
        tp1 = _round_tick(entry_price - fib_range * 0.618)
        tp2 = _round_tick(entry_price - fib_range * 1.0)

    risk = abs(entry_price - stop_loss)
    reward = abs(tp1 - entry_price)
    rr = round(reward / risk, 2) if risk > 0 else 0

    return TriggerResult(
        decision=decision,
        score=score,
        direction=direction,
        fib_ratio=target_ratio,
        fib_level=target_level,
        entry_price=entry_price,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        rr=rr,
        rejection_wick=rejection_wick,
        volume_spike=volume_spike,
        volume_ratio=round(volume_ratio, 2),
        engulfing=engulfing,
        momentum_shift=momentum_shift,
        squeeze_on=sq.squeeze_on,
        squeeze_momentum=round(sq.momentum, 2),
        rsi_value=rsi_value,
    )
