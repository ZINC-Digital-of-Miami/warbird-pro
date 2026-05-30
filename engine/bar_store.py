"""Bar store — OHLCV bar data type for the engine pipeline.

Provides the canonical Bar dataclass used by fib_engine, indicators,
and the WebSocket feed (Phase 1.5).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Bar:
    """Single OHLCV bar."""

    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int = 0
