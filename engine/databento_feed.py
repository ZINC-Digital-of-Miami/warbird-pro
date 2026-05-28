"""Databento live feed — streams MES 1m bars into the BarStore.

Uses the ``databento`` Python SDK to subscribe to the GLBX.MDP3 dataset
and receive OHLCV-1m bars in real-time.  Falls back to a historical
backfill on startup to seed the chart with recent data.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timedelta, timezone

import databento as db

from engine.bar_store import Bar, BarStore
from engine.config import (
    DATABENTO_API_KEY,
    DATABENTO_DATASET,
    DATABENTO_SYMBOL,
    DATABENTO_STYPE,
    MAX_BARS_IN_MEMORY,
)

logger = logging.getLogger("warbird.feed")

BACKFILL_BARS = 2000  # ~33 hours of 1m bars


def _record_to_bar(record: db.OHLCVMsg) -> Bar:
    ts_ns = record.ts_event
    ts = datetime.fromtimestamp(ts_ns / 1e9, tz=timezone.utc)
    return Bar(
        ts=ts,
        open=record.open / 1e9,
        high=record.high / 1e9,
        low=record.low / 1e9,
        close=record.close / 1e9,
        volume=record.volume,
    )


def backfill(store: BarStore, bars: int = BACKFILL_BARS) -> int:
    """Fetch recent 1m bars from Databento Historical API and seed the store."""
    if not DATABENTO_API_KEY:
        logger.warning("No DATABENTO_API_KEY — skipping backfill")
        return 0

    client = db.Historical(key=DATABENTO_API_KEY)
    # Databento historical data has a ~20-minute delay from real-time.
    end = datetime.now(timezone.utc) - timedelta(minutes=30)
    start = end - timedelta(minutes=bars)

    logger.info("Backfilling %d 1m bars from %s to %s", bars, start.isoformat(), end.isoformat())

    data = client.timeseries.get_range(
        dataset=DATABENTO_DATASET,
        symbols=[DATABENTO_SYMBOL],
        stype_in=DATABENTO_STYPE,
        schema="ohlcv-1m",
        start=start.isoformat(),
        end=end.isoformat(),
    )

    count = 0
    batch: list[Bar] = []
    for record in data:
        if isinstance(record, db.OHLCVMsg):
            batch.append(_record_to_bar(record))
            count += 1

    # Sort by timestamp and bulk-load.
    batch.sort(key=lambda b: b.ts)
    store.backfill("1m", batch)
    logger.info("Backfilled %d bars", count)
    return count


def stream_live(store: BarStore, stop_event: threading.Event) -> None:
    """Connect to Databento Live API and stream 1m bars into the store.

    Runs in a dedicated thread.  Reconnects on failure with exponential
    backoff.
    """
    if not DATABENTO_API_KEY:
        logger.error("No DATABENTO_API_KEY — live feed disabled")
        return

    backoff = 1.0
    max_backoff = 60.0

    while not stop_event.is_set():
        try:
            logger.info("Connecting to Databento Live…")
            client = db.Live(key=DATABENTO_API_KEY)
            client.subscribe(
                dataset=DATABENTO_DATASET,
                schema="ohlcv-1m",
                stype_in=DATABENTO_STYPE,
                symbols=[DATABENTO_SYMBOL],
            )

            backoff = 1.0  # Reset on successful connection.

            for record in client:
                if stop_event.is_set():
                    break
                if isinstance(record, db.OHLCVMsg):
                    bar = _record_to_bar(record)
                    store.add_1m_bar(bar)

        except Exception:
            logger.exception("Live feed error — reconnecting in %.0fs", backoff)
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)


def start_feed(store: BarStore) -> tuple[threading.Thread, threading.Event]:
    """Backfill and start the live feed thread.  Returns (thread, stop_event)."""
    backfill(store)

    stop = threading.Event()
    t = threading.Thread(target=stream_live, args=(store, stop), daemon=True, name="databento-feed")
    t.start()
    return t, stop
