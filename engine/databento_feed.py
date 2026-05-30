"""Databento live feed with client-presence lifecycle.

Connects to Databento Live API on WARMING state (first client connects),
disconnects on COLD state (all clients gone + cooldown expired).
Falls back to Historical API backfill on startup.
Implements exponential backoff reconnect (3 attempts, 2s base).
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timedelta, timezone

from engine.bar_store import Bar, BarStore
from engine.config import (
    BACKOFF_BASE_S,
    DATABENTO_API_KEY,
    DATABENTO_DATASET,
    DATABENTO_SYMBOL,
    DATABENTO_STYPE,
    GAP_FILL_AUTO_HOURS,
    GAP_FILL_WARN_HOURS,
    MAX_BARS_IN_MEMORY,
    RECONNECT_ATTEMPTS,
)

logger = logging.getLogger("warbird.feed")

BACKFILL_BARS = 2000  # ~33 hours of 1m bars


def _record_to_bar(record) -> Bar:
    """Convert a Databento OHLCVMsg to our Bar dataclass."""
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


def active_mes_contract() -> str:
    """Determine the active front-month MES contract.

    CME E-mini/Micro ES rolls quarterly on the 2nd Friday of Mar/Jun/Sep/Dec.
    The continuous symbol MES.n.0 handles this automatically in Databento,
    but this function provides the explicit contract month for reference.
    """
    now = datetime.now(timezone.utc)
    month = now.month
    year = now.year

    quarterly_months = [3, 6, 9, 12]
    for qm in quarterly_months:
        if month <= qm:
            contract_month = qm
            contract_year = year
            break
    else:
        contract_month = 3
        contract_year = year + 1

    month_codes = {3: "H", 6: "M", 9: "U", 12: "Z"}
    code = month_codes[contract_month]
    return f"MES{code}{contract_year % 100:02d}"


def detect_contract_roll() -> bool:
    """Check if we are within the roll window (2nd Friday of roll month).

    Returns True if a roll is imminent (within 5 days of expiry).
    """
    now = datetime.now(timezone.utc)
    month = now.month
    year = now.year

    if month not in (3, 6, 9, 12):
        return False

    from calendar import monthcalendar
    cal = monthcalendar(year, month)
    fridays = [week[4] for week in cal if week[4] != 0]
    if len(fridays) < 2:
        return False
    second_friday = fridays[1]
    roll_date = datetime(year, month, second_friday, tzinfo=timezone.utc)
    days_to_roll = (roll_date - now).days
    return 0 <= days_to_roll <= 5


class GapFillResult:
    """Result of a gap-fill operation."""

    def __init__(self, bars_filled: int, gap_hours: float, action: str):
        self.bars_filled = bars_filled
        self.gap_hours = gap_hours
        self.action = action  # "auto", "warned", "refused"


def compute_gap_hours(last_bar_ts: datetime | None) -> float:
    """Compute hours since last bar."""
    if last_bar_ts is None:
        return float("inf")
    now = datetime.now(timezone.utc)
    delta = now - last_bar_ts
    return delta.total_seconds() / 3600


def gap_fill_decision(gap_hours: float) -> str:
    """Apply cost cap rules for gap-fill.

    < 6h: auto gap-fill
    > 6h and <= 24h: warn before filling
    > 24h: refuse and require manual approval
    """
    if gap_hours < GAP_FILL_AUTO_HOURS:
        return "auto"
    elif gap_hours <= GAP_FILL_WARN_HOURS:
        return "warn"
    else:
        return "refuse"


def backfill(store: BarStore, bars: int = BACKFILL_BARS) -> int:
    """Fetch recent 1m bars from Databento Historical API and seed the store.

    Applies gap-fill cost cap rules.
    """
    if not DATABENTO_API_KEY:
        logger.warning("No DATABENTO_API_KEY - skipping backfill")
        return 0

    last = store.last_bar("1m")
    gap_hours = compute_gap_hours(last.ts if last else None)
    decision = gap_fill_decision(gap_hours)

    if decision == "refuse":
        logger.error(
            "Gap-fill refused: %.1fh gap exceeds 24h limit. Manual approval required.",
            gap_hours,
        )
        return 0
    elif decision == "warn":
        logger.warning(
            "Gap-fill warning: %.1fh gap exceeds 6h. Proceeding with caution.",
            gap_hours,
        )

    try:
        import databento as db
    except ImportError:
        logger.error("databento package not installed - skipping backfill")
        return 0

    client = db.Historical(key=DATABENTO_API_KEY)
    end = datetime.now(timezone.utc) - timedelta(minutes=30)
    start = end - timedelta(minutes=bars)

    logger.info("Backfilling %d 1m bars from %s to %s", bars, start.isoformat(), end.isoformat())

    try:
        data = client.timeseries.get_range(
            dataset=DATABENTO_DATASET,
            symbols=[DATABENTO_SYMBOL],
            stype_in=DATABENTO_STYPE,
            schema="ohlcv-1m",
            start=start.isoformat(),
            end=end.isoformat(),
        )
    except Exception:
        logger.exception("Historical API backfill failed")
        return 0

    batch: list[Bar] = []
    for record in data:
        if hasattr(record, "ts_event"):
            batch.append(_record_to_bar(record))

    batch.sort(key=lambda b: b.ts)
    loaded = store.backfill("1m", batch)
    logger.info("Backfilled %d bars (of %d fetched)", loaded, len(batch))
    return loaded


def _connect_and_subscribe(db_module):
    """Create a Live client and subscribe to the MES 1m feed."""
    client = db_module.Live(key=DATABENTO_API_KEY)
    client.subscribe(
        dataset=DATABENTO_DATASET,
        schema="ohlcv-1m",
        stype_in=DATABENTO_STYPE,
        symbols=[DATABENTO_SYMBOL],
    )
    return client


def _consume_records(client, store: BarStore, stop_event: threading.Event) -> None:
    """Consume records from a live client until stop is signaled."""
    for record in client:
        if stop_event.is_set():
            break
        if hasattr(record, "ts_event"):
            bar = _record_to_bar(record)
            store.add_1m_bar(bar)


def stream_live(store: BarStore, stop_event: threading.Event) -> None:
    """Connect to Databento Live API and stream 1m bars into the store.

    Implements exponential backoff reconnect (3 attempts, 2s base).
    Runs in a dedicated thread.
    """
    if not DATABENTO_API_KEY:
        logger.error("No DATABENTO_API_KEY - live feed disabled")
        return

    try:
        import databento as db
    except ImportError:
        logger.error("databento package not installed - live feed disabled")
        return

    attempt = 0
    backoff = BACKOFF_BASE_S

    while not stop_event.is_set():
        try:
            if detect_contract_roll():
                logger.info("Contract roll window detected for %s", active_mes_contract())

            logger.info("Connecting to Databento Live (attempt %d)...", attempt + 1)
            client = _connect_and_subscribe(db)
            attempt = 0
            backoff = BACKOFF_BASE_S
            _consume_records(client, store, stop_event)

        except Exception:
            attempt += 1
            if attempt >= RECONNECT_ATTEMPTS:
                logger.error(
                    "Live feed failed after %d attempts - giving up", RECONNECT_ATTEMPTS
                )
                return
            logger.exception("Live feed error - reconnecting in %.0fs (attempt %d/%d)",
                            backoff, attempt, RECONNECT_ATTEMPTS)
            stop_event.wait(backoff)
            backoff = min(backoff * 2, 60.0)


def start_feed(store: BarStore) -> tuple[threading.Thread, threading.Event]:
    """Backfill and start the live feed thread. Returns (thread, stop_event)."""
    backfill(store)

    stop = threading.Event()
    t = threading.Thread(
        target=stream_live, args=(store, stop), daemon=True, name="databento-feed"
    )
    t.start()
    return t, stop


def stop_feed(thread: threading.Thread | None, stop_event: threading.Event | None) -> None:
    """Gracefully stop the feed thread."""
    if stop_event:
        stop_event.set()
    if thread and thread.is_alive():
        thread.join(timeout=5)
        if thread.is_alive():
            logger.warning("Feed thread did not stop within timeout")
