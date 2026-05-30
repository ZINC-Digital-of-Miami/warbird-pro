"""In-memory bar store with multi-timeframe aggregation.

Stores 1m bars as they arrive from Databento and maintains aggregated views
for 3m, 5m, 15m, 1h, 4h, 1d timeframes.  Thread-safe for concurrent
read/write from the feed thread + WebSocket handlers.
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from engine.config import AGGREGATION_PERIODS, BAR_VALIDATION_ENABLED, MAX_BARS_IN_MEMORY

logger = logging.getLogger("warbird.bar_store")


@dataclass
class Bar:
    """Single OHLCV bar."""

    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int = 0

    def to_dict(self) -> dict:
        return {
            "time": int(self.ts.timestamp()),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


BarCallback = Callable[[str, Bar], None]


def validate_bar(bar: Bar) -> bool:
    """Validate bar data: price > 0, high >= low, not weekend."""
    if not BAR_VALIDATION_ENABLED:
        return True
    if bar.open <= 0 or bar.high <= 0 or bar.low <= 0 or bar.close <= 0:
        logger.warning("Bar validation failed: price <= 0 at %s", bar.ts)
        return False
    if bar.high < bar.low:
        logger.warning("Bar validation failed: high < low at %s", bar.ts)
        return False
    if bar.ts.weekday() >= 5:
        day_name = bar.ts.strftime("%A")
        hour = bar.ts.hour
        if bar.ts.weekday() == 5 or (bar.ts.weekday() == 6 and hour < 17):
            logger.warning("Bar validation failed: weekend bar (%s) at %s", day_name, bar.ts)
            return False
    return True


class BarStore:
    """Thread-safe multi-TF bar store.

    1m bars are pushed via ``add_1m_bar``.  Higher TF bars are aggregated
    automatically and kept in separate ring buffers.
    """

    def __init__(self, max_bars: int = MAX_BARS_IN_MEMORY) -> None:
        self._lock = threading.RLock()
        self._max = max_bars
        self._bars: dict[str, deque[Bar]] = {
            tf: deque(maxlen=max_bars) for tf in AGGREGATION_PERIODS
        }
        self._partials: dict[str, Bar | None] = {tf: None for tf in AGGREGATION_PERIODS}
        self._1m_count_in_partial: dict[str, int] = {tf: 0 for tf in AGGREGATION_PERIODS}
        self._callbacks: list[BarCallback] = []
        self._total_bars_ingested: int = 0

    def on_bar(self, cb: BarCallback) -> None:
        """Register a callback ``(tf: str, bar: Bar) -> None``."""
        with self._lock:
            self._callbacks.append(cb)

    def add_1m_bar(self, bar: Bar) -> bool:
        """Ingest a 1-minute bar and propagate aggregation.

        Returns False if bar fails validation.
        """
        if not validate_bar(bar):
            return False

        with self._lock:
            self._bars["1m"].append(bar)
            self._total_bars_ingested += 1

        self._fire("1m", bar)

        for tf, period in AGGREGATION_PERIODS.items():
            if period <= 1:
                continue
            closed_bar = self._accumulate(tf, period, bar)
            if closed_bar is not None:
                with self._lock:
                    self._bars[tf].append(closed_bar)
                self._fire(tf, closed_bar)

        return True

    def get_bars(self, tf: str) -> list[Bar]:
        """Return a snapshot of bars for a given timeframe."""
        with self._lock:
            return list(self._bars.get(tf, []))

    def last_bar(self, tf: str) -> Bar | None:
        """Return the most recent bar for a timeframe."""
        with self._lock:
            buf = self._bars.get(tf)
            return buf[-1] if buf else None

    def bar_count(self, tf: str) -> int:
        """Return number of bars stored for a timeframe."""
        with self._lock:
            buf = self._bars.get(tf)
            return len(buf) if buf else 0

    @property
    def total_bars_ingested(self) -> int:
        return self._total_bars_ingested

    def backfill(self, tf: str, bars: list[Bar]) -> int:
        """Bulk-load historical bars (oldest first).

        When tf is '1m', also aggregates into all higher timeframes.
        Returns number of bars loaded (after validation).
        """
        valid_bars = [b for b in bars if validate_bar(b)]

        with self._lock:
            buf = self._bars[tf]
            for b in valid_bars:
                buf.append(b)

        if tf == "1m":
            self._aggregate_backfill(valid_bars)

        return len(valid_bars)

    def _aggregate_backfill(self, bars_1m: list[Bar]) -> None:
        """Build higher-TF bars from backfilled 1m bars."""
        for tf, period in AGGREGATION_PERIODS.items():
            if period <= 1:
                continue
            agg: list[Bar] = []
            partial: Bar | None = None
            count = 0
            for bar in bars_1m:
                if partial is None:
                    partial = Bar(
                        ts=bar.ts, open=bar.open, high=bar.high,
                        low=bar.low, close=bar.close, volume=bar.volume,
                    )
                    count = 1
                else:
                    partial.high = max(partial.high, bar.high)
                    partial.low = min(partial.low, bar.low)
                    partial.close = bar.close
                    partial.volume += bar.volume
                    partial.ts = bar.ts
                    count += 1

                if count >= period:
                    agg.append(partial)
                    partial = None
                    count = 0

            with self._lock:
                buf = self._bars[tf]
                for b in agg:
                    buf.append(b)

    def _accumulate(self, tf: str, period: int, bar_1m: Bar) -> Bar | None:
        """Accumulate a 1m bar into the partial for *tf*.

        Returns the completed higher-TF bar when the period boundary
        is reached, or None if still accumulating.
        """
        with self._lock:
            partial = self._partials[tf]
            if partial is None:
                self._partials[tf] = Bar(
                    ts=bar_1m.ts,
                    open=bar_1m.open,
                    high=bar_1m.high,
                    low=bar_1m.low,
                    close=bar_1m.close,
                    volume=bar_1m.volume,
                )
                self._1m_count_in_partial[tf] = 1
                if period == 1:
                    result = self._partials[tf]
                    self._partials[tf] = None
                    self._1m_count_in_partial[tf] = 0
                    return result
                return None

            partial.high = max(partial.high, bar_1m.high)
            partial.low = min(partial.low, bar_1m.low)
            partial.close = bar_1m.close
            partial.volume += bar_1m.volume
            partial.ts = bar_1m.ts
            self._1m_count_in_partial[tf] += 1

            if self._1m_count_in_partial[tf] >= period:
                result = partial
                self._partials[tf] = None
                self._1m_count_in_partial[tf] = 0
                return result
            return None

    def _fire(self, tf: str, bar: Bar) -> None:
        """Notify registered callbacks. Errors in callbacks are logged, not raised."""
        callbacks = list(self._callbacks)
        for cb in callbacks:
            try:
                cb(tf, bar)
            except Exception:
                logger.exception("Bar callback error for %s", tf)
