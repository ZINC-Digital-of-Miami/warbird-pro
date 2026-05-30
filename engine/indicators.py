"""Technical indicators for the engine pipeline.

Provides ATR and other indicators used by fib_engine and signal chain.
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
