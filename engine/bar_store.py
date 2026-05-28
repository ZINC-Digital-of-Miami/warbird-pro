"""In-memory bar store with multi-timeframe aggregation.

Stores 1m bars as they arrive from Databento and maintains aggregated views
for 3m, 5m, 15m, 1h, 4h timeframes.
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

from engine.config import AGGREGATION_PERIODS, MAX_BARS_IN_MEMORY


@dataclass
class Bar:
    ts: datetime  # bar close timestamp (UTC)
    open: float
    high: float
    low: float
    close: float
    volume: int

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


class BarStore:
    """Thread-safe multi-TF bar store.

    1m bars are pushed via ``add_1m_bar``.  Higher TF bars are aggregated
    automatically and kept in separate ring buffers.
    """

    def __init__(self, max_bars: int = MAX_BARS_IN_MEMORY) -> None:
        self._lock = threading.Lock()
        self._max = max_bars
        self._bars: dict[str, deque[Bar]] = {
            tf: deque(maxlen=max_bars) for tf in AGGREGATION_PERIODS
        }
        # Partial (in-progress) higher-TF bars being accumulated.
        self._partials: dict[str, Bar | None] = {tf: None for tf in AGGREGATION_PERIODS}
        self._1m_count_in_partial: dict[str, int] = {tf: 0 for tf in AGGREGATION_PERIODS}
        self._callbacks: list[BarCallback] = []

    # ── Public API ────────────────────────────────────────────────────────

    def on_bar(self, cb: BarCallback) -> None:
        """Register a callback ``(tf: str, bar: Bar) -> None``."""
        self._callbacks.append(cb)

    def add_1m_bar(self, bar: Bar) -> None:
        """Ingest a 1-minute bar and propagate aggregation."""
        with self._lock:
            self._bars["1m"].append(bar)

        self._fire("1m", bar)

        for tf, period in AGGREGATION_PERIODS.items():
            if period <= 1:
                continue
            closed_bar = self._accumulate(tf, period, bar)
            if closed_bar is not None:
                with self._lock:
                    self._bars[tf].append(closed_bar)
                self._fire(tf, closed_bar)

    def get_bars(self, tf: str) -> list[Bar]:
        """Return a snapshot of bars for a given timeframe."""
        with self._lock:
            return list(self._bars.get(tf, []))

    def last_bar(self, tf: str) -> Bar | None:
        with self._lock:
            buf = self._bars.get(tf)
            return buf[-1] if buf else None

    def backfill(self, tf: str, bars: list[Bar]) -> None:
        """Bulk-load historical bars (oldest first).

        When tf is '1m', also aggregates into all higher timeframes.
        """
        with self._lock:
            buf = self._bars[tf]
            for b in bars:
                buf.append(b)

        if tf == "1m":
            self._aggregate_backfill(bars)

    # ── Internal ──────────────────────────────────────────────────────────

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
        is reached, or ``None`` if still accumulating.
        """
        partial = self._partials[tf]
        if partial is None:
            # Start a new partial bar.
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

        # Update running OHLCV.
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
        for cb in self._callbacks:
            try:
                cb(tf, bar)
            except Exception:
                pass
