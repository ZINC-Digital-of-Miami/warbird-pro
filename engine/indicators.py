"""Technical indicators — pure Python, no external TA library.

Ported from lib/ta/indicators.ts to keep the engine self-contained.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


def sma(values: list[float], period: int) -> float:
    if len(values) < period:
        return values[-1] if values else 0.0
    return sum(values[-period:]) / period


def ema(values: list[float], period: int) -> float:
    if not values:
        return 0.0
    k = 2.0 / (period + 1)
    result = values[0]
    for v in values[1:]:
        result = v * k + result * (1 - k)
    return result


def ema_series(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    k = 2.0 / (period + 1)
    out = [values[0]]
    for v in values[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def stdev(values: list[float], period: int) -> float:
    if len(values) < period:
        return 0.0
    window = values[-period:]
    mean = sum(window) / period
    variance = sum((x - mean) ** 2 for x in window) / period
    return math.sqrt(variance)


def rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    gains = []
    losses = []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    if len(gains) < period:
        return 50.0
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def atr(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float:
    if len(closes) < 2:
        return 0.0
    trs: list[float] = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)
    if not trs:
        return 0.0
    if len(trs) <= period:
        return sum(trs) / len(trs)
    atr_val = sum(trs[:period]) / period
    for i in range(period, len(trs)):
        atr_val = (atr_val * (period - 1) + trs[i]) / period
    return atr_val


def adx(highs: list[float], lows: list[float], closes: list[float], period: int = 14) -> float:
    """Average Directional Index."""
    n = len(closes)
    if n < period + 1:
        return 0.0

    plus_dm: list[float] = []
    minus_dm: list[float] = []
    tr_list: list[float] = []

    for i in range(1, n):
        up = highs[i] - highs[i - 1]
        down = lows[i - 1] - lows[i]
        plus_dm.append(up if up > down and up > 0 else 0)
        minus_dm.append(down if down > up and down > 0 else 0)
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        tr_list.append(tr)

    if len(tr_list) < period:
        return 0.0

    atr_val = sum(tr_list[:period]) / period
    plus_di = sum(plus_dm[:period]) / period
    minus_di = sum(minus_dm[:period]) / period

    for i in range(period, len(tr_list)):
        atr_val = (atr_val * (period - 1) + tr_list[i]) / period
        plus_di = (plus_di * (period - 1) + plus_dm[i]) / period
        minus_di = (minus_di * (period - 1) + minus_dm[i]) / period

    if atr_val == 0:
        return 0.0

    plus_di_pct = (plus_di / atr_val) * 100
    minus_di_pct = (minus_di / atr_val) * 100
    di_sum = plus_di_pct + minus_di_pct
    if di_sum == 0:
        return 0.0
    dx = abs(plus_di_pct - minus_di_pct) / di_sum * 100
    return dx


@dataclass
class SqueezeResult:
    squeeze_on: bool
    momentum: float
    momentum_direction: int  # 1 = increasing, -1 = decreasing


def ttm_squeeze(
    closes: list[float],
    highs: list[float],
    lows: list[float],
    bb_length: int = 20,
    bb_mult: float = 2.0,
    kc_length: int = 20,
    kc_mult: float = 1.5,
    momentum_length: int = 12,
) -> SqueezeResult:
    """TTM Squeeze — Bollinger Bands inside Keltner Channels."""
    n = len(closes)
    if n < max(bb_length, kc_length, momentum_length):
        return SqueezeResult(squeeze_on=False, momentum=0, momentum_direction=0)

    bb_basis = sma(closes, bb_length)
    bb_dev = stdev(closes, bb_length) * bb_mult
    bb_upper = bb_basis + bb_dev
    bb_lower = bb_basis - bb_dev

    kc_basis = sma(closes, kc_length)
    atr_val = atr(highs, lows, closes, kc_length)
    kc_upper = kc_basis + kc_mult * atr_val
    kc_lower = kc_basis - kc_mult * atr_val

    squeeze_on = bb_lower > kc_lower and bb_upper < kc_upper

    recent_highs = highs[-momentum_length:]
    recent_lows = lows[-momentum_length:]
    hh = max(recent_highs)
    ll = min(recent_lows)
    midline = (sma(closes, momentum_length) + (hh + ll) / 2) / 2
    momentum = closes[-1] - midline

    # Previous momentum for direction.
    direction = 0
    if n > momentum_length + 1:
        prev_closes = closes[:-1]
        prev_highs = highs[:-1]
        prev_lows = lows[:-1]
        ph = max(prev_highs[-momentum_length:])
        pl = min(prev_lows[-momentum_length:])
        prev_mid = (sma(prev_closes, momentum_length) + (ph + pl) / 2) / 2
        prev_momentum = prev_closes[-1] - prev_mid
        direction = 1 if momentum > prev_momentum else -1

    return SqueezeResult(squeeze_on=squeeze_on, momentum=momentum, momentum_direction=direction)
