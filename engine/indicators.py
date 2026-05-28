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


# ── Pressure computation ──────────────────────────────────────────────────────

@dataclass
class PressureResult:
    bull_pct: float
    bear_pct: float
    squeeze_on: bool
    squeeze_momentum: float
    momentum_direction: int
    rsi_value: float
    volume_ratio: float

    def to_dict(self) -> dict:
        return {
            "bullPct": round(self.bull_pct, 1),
            "bearPct": round(self.bear_pct, 1),
            "squeezeOn": self.squeeze_on,
            "squeezeMomentum": round(self.squeeze_momentum, 2),
            "momentumDirection": self.momentum_direction,
            "rsiValue": round(self.rsi_value, 1),
            "volumeRatio": round(self.volume_ratio, 2),
        }


def compute_pressure(
    closes: list[float],
    highs: list[float],
    lows: list[float],
    volumes: list[float],
    bar_directions: list[int],
) -> PressureResult:
    """Compute real-time pressure from volume, momentum, RSI, and squeeze.

    Returns bull_pct (0-100) that updates on every bar, independent of fib
    zone proximity.
    """
    n = len(closes)
    if n < 20:
        return PressureResult(
            bull_pct=50, bear_pct=50, squeeze_on=False,
            squeeze_momentum=0, momentum_direction=0,
            rsi_value=50, volume_ratio=0,
        )

    # 1. Volume pressure — buy vs sell volume over last 20 bars (30%)
    recent_dirs = bar_directions[-20:]
    recent_vols = volumes[-20:]
    buy_vol = sum(v for v, d in zip(recent_vols, recent_dirs) if d >= 0)
    sell_vol = sum(v for v, d in zip(recent_vols, recent_dirs) if d < 0)
    total_vol = buy_vol + sell_vol
    vol_pressure = (buy_vol / total_vol * 100) if total_vol > 0 else 50

    # 2. RSI position (25%)
    rsi_val = rsi(closes)
    rsi_pressure = rsi_val

    # 3. Price momentum — proportion of up closes in last 10 bars (20%)
    deltas = [closes[i] - closes[i - 1] for i in range(max(n - 10, 1), n)]
    up_count = sum(1 for d in deltas if d > 0)
    mom_pressure = (up_count / len(deltas) * 100) if deltas else 50

    # 4. TTM Squeeze momentum direction + magnitude (25%)
    sq = ttm_squeeze(closes, highs, lows)
    mom_clamped = max(-5, min(5, sq.momentum))
    squeeze_pressure = 50 + (mom_clamped / 5 * 50)

    # Weighted blend
    bull_pct = (
        vol_pressure * 0.30
        + rsi_pressure * 0.25
        + mom_pressure * 0.20
        + squeeze_pressure * 0.25
    )
    bull_pct = max(5, min(95, bull_pct))

    # Volume ratio for card
    avg_vol = sum(volumes[-20:]) / 20
    vol_ratio = volumes[-1] / avg_vol if avg_vol > 0 else 0

    return PressureResult(
        bull_pct=bull_pct,
        bear_pct=100 - bull_pct,
        squeeze_on=sq.squeeze_on,
        squeeze_momentum=sq.momentum,
        momentum_direction=sq.momentum_direction,
        rsi_value=rsi_val,
        volume_ratio=vol_ratio,
    )


# ── Nexus AMF oscillator ──────────────────────────────────────────────────────

def _rolling_highest(values: list[float], period: int) -> list[float]:
    out: list[float] = []
    for i in range(len(values)):
        start = max(0, i - period + 1)
        out.append(max(values[start : i + 1]))
    return out


def _rolling_lowest(values: list[float], period: int) -> list[float]:
    out: list[float] = []
    for i in range(len(values)):
        start = max(0, i - period + 1)
        out.append(min(values[start : i + 1]))
    return out


def _full_ema(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    k = 2.0 / (period + 1)
    out = [values[0]]
    for v in values[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def _full_sma(values: list[float], period: int) -> list[float]:
    out: list[float] = []
    for i in range(len(values)):
        start = max(0, i - period + 1)
        window = values[start : i + 1]
        out.append(sum(window) / len(window))
    return out


def _smooth_series(values: list[float], period: int, method: str) -> list[float]:
    if method == "SMA":
        return _full_sma(values, period)
    if method == "EMA":
        return _full_ema(values, period)
    if method == "DEMA":
        e1 = _full_ema(values, period)
        e2 = _full_ema(e1, period)
        return [2 * a - b for a, b in zip(e1, e2)]
    if method == "TEMA":
        e1 = _full_ema(values, period)
        e2 = _full_ema(e1, period)
        e3 = _full_ema(e2, period)
        return [3 * a - 3 * b + c for a, b, c in zip(e1, e2, e3)]
    return _full_ema(values, period)


def nexus_series(
    times: list[int],
    opens: list[float],
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[float],
    period: int = 34,
    sig_period: int = 8,
    smooth_type: str = "SMA",
    sig_type: str = "EMA",
    ob: float = 71.84,
    os_level: float = 19.59,
) -> list[dict]:
    """Compute Nexus AMF oscillator time series.

    Returns a list of {time, osc, signal, vf} dicts, one per bar.
    """
    n = len(closes)
    if n < period + 1:
        return []

    source = opens  # Pine default: sourceInput = input.source(open)

    # 1. ROC → smooth → normalize
    roc_raw = [0.0] * n
    for i in range(period, n):
        if source[i - period] != 0:
            roc_raw[i] = (source[i] - source[i - period]) / source[i - period] * 100

    roc_smooth = _smooth_series(roc_raw, period, smooth_type)
    roc_high = _rolling_highest(roc_smooth, period * 3)
    roc_low = _rolling_lowest(roc_smooth, period * 3)
    nroc = []
    for i in range(n):
        rng = roc_high[i] - roc_low[i]
        if rng > 0:
            nroc.append((roc_smooth[i] - roc_low[i]) / rng * 100)
        else:
            nroc.append(50.0)

    # 2. Efficiency ratio
    er_vals = [0.0] * n
    for i in range(period, n):
        direction_val = abs(source[i] - source[i - period])
        volatility = sum(abs(source[j] - source[j - 1]) for j in range(i - period + 1, i + 1))
        er_vals[i] = direction_val / volatility if volatility > 0 else 0

    # 3. EWI — efficiency-weighted impulse
    atr_vals = [0.0] * n
    for i in range(1, n):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        if i < period:
            atr_vals[i] = tr
        else:
            atr_vals[i] = (atr_vals[i - 1] * (period - 1) + tr) / period

    impulse_raw = [0.0] * n
    for i in range(1, n):
        impulse_raw[i] = source[i] - source[i - 1]

    norm_impulse = [0.0] * n
    for i in range(n):
        imp_abs = max(atr_vals[i], abs(impulse_raw[i]) + 0.0001)
        norm_impulse[i] = (impulse_raw[i] / imp_abs) * er_vals[i]

    ewi_smooth = _smooth_series(norm_impulse, period, smooth_type)
    ewi_high = _rolling_highest(ewi_smooth, period * 4)
    ewi_low = _rolling_lowest(ewi_smooth, period * 4)
    ewi = []
    for i in range(n):
        rng = ewi_high[i] - ewi_low[i]
        if rng > 0:
            ewi.append((ewi_smooth[i] - ewi_low[i]) / rng * 100)
        else:
            ewi.append(50.0)

    # 4. Stochastic momentum
    stoch_high = _rolling_highest(source, period)
    stoch_low = _rolling_lowest(source, period)
    stoch_raw = []
    for i in range(n):
        rng = stoch_high[i] - stoch_low[i]
        if rng > 0:
            stoch_raw.append((source[i] - stoch_low[i]) / rng * 100)
        else:
            stoch_raw.append(50.0)
    smp_len = max(period // 2, 2)
    smp = _full_ema(stoch_raw, smp_len)

    # 5. Blend
    er_smooth = _full_ema(er_vals, period)
    osc_smooth_len = max(period // 3, 2)
    osc_raw = []
    for i in range(n):
        tw = min(er_smooth[i] * 1.5, 0.75)
        rw = 1.0 - tw
        val = tw * (nroc[i] * 0.55 + ewi[i] * 0.45) + rw * smp[i]
        osc_raw.append(val)

    osc_smooth = _smooth_series(osc_raw, osc_smooth_len, smooth_type)
    osc_vals = [max(0, min(100, v)) for v in osc_smooth]

    # 6. Signal line
    sig_vals = _smooth_series(osc_vals, sig_period, sig_type)

    # 7. Simplified volume flow (using bar delta since no footprint)
    vf_vals = [50.0] * n
    for i in range(1, n):
        bar_range = highs[i] - lows[i]
        if bar_range > 0:
            delta = (closes[i] - opens[i]) / bar_range
        else:
            delta = 0
        raw = delta * (volumes[i] if volumes[i] > 0 else 1)
        vf_vals[i] = raw

    vf_ema = _full_ema(vf_vals, max(int(period * 0.6), 2))
    vf_peak = _rolling_highest([abs(v) for v in vf_ema], period * 4)
    vf_norm = []
    for i in range(n):
        pk = max(vf_peak[i], 0.0001)
        vf_norm.append(max(0, min(100, vf_ema[i] / pk * 50 + 50)))

    # Build output (skip warmup period)
    warmup = max(period * 3, 60)
    result = []
    for i in range(warmup, n):
        result.append({
            "time": times[i],
            "osc": round(osc_vals[i], 2),
            "signal": round(sig_vals[i], 2),
            "vf": round(vf_norm[i], 2),
        })

    return result
