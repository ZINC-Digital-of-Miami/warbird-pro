"""Technical indicators for the engine pipeline.

Provides ATR, EMA, and SMA used by fib_engine, signal chain, and MA overlays.
"""

from __future__ import annotations


def atr(highs: list[float], lows: list[float], closes: list[float], period: int) -> float:
    """Compute Average True Range over the last `period` bars.

    Uses Wilder's smoothing (exponential moving average of true range).
    """
    n = len(highs)
    if n < 2 or period < 1:
        return 0.0

    tr_values: list[float] = [highs[0] - lows[0]]
    for i in range(1, n):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        tr_values.append(tr)

    if len(tr_values) < period:
        return sum(tr_values) / len(tr_values)

    atr_val = sum(tr_values[:period]) / period
    for i in range(period, len(tr_values)):
        atr_val = (atr_val * (period - 1) + tr_values[i]) / period

    return atr_val


def ema_series(values: list[float], period: int) -> list[float | None]:
    """Compute EMA for a list of values.

    Returns a same-length list; entries before the first full window are None.
    Uses the standard EMA formula: multiplier = 2 / (period + 1).
    """
    n = len(values)
    if n == 0 or period < 1:
        return []

    result: list[float | None] = [None] * n
    if n < period:
        return result

    seed = sum(values[:period]) / period
    result[period - 1] = seed
    mult = 2.0 / (period + 1)
    prev = seed
    for i in range(period, n):
        val = values[i] * mult + prev * (1 - mult)
        result[i] = val
        prev = val
    return result


def sma_series(values: list[float], period: int) -> list[float | None]:
    """Compute SMA for a list of values.

    Returns a same-length list; entries before the first full window are None.
    """
    n = len(values)
    if n == 0 or period < 1:
        return []

    result: list[float | None] = [None] * n
    if n < period:
        return result

    rolling = sum(values[:period])
    result[period - 1] = rolling / period
    for i in range(period, n):
        rolling += values[i] - values[i - period]
        result[i] = rolling / period
    return result
