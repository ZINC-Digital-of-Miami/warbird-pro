"""Databento live feed with client-presence lifecycle.

Connects to Databento Live API on WARMING state (first client connects),
disconnects on COLD state (all clients gone + cooldown expired).
Falls back to Historical API backfill on startup.
Implements exponential backoff reconnect: 3 total attempts with 2 waits
(2 s before attempt 2, 4 s before attempt 3). No third wait — failure on
attempt 3 exits immediately.
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
    DATABENTO_CONTINUOUS_RULE,
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
QUARTERLY_MONTHS = (3, 6, 9, 12)
MONTH_CODES = {3: "H", 6: "M", 9: "U", 12: "Z"}


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


def _third_friday_day(year: int, month: int) -> int:
    from calendar import monthcalendar

    fridays = [week[4] for week in monthcalendar(year, month) if week[4] != 0]
    if len(fridays) < 3:
        raise RuntimeError("Could not determine third Friday for quarter month")
    return fridays[2]


def _calendar_roll_date(year: int, quarter_month: int) -> datetime:
    third_friday = _third_friday_day(year, quarter_month)
    return datetime(year, quarter_month, third_friday, tzinfo=timezone.utc) - timedelta(days=4)


def _next_quarter_contract(quarter_month: int, year: int) -> tuple[int, int]:
    idx = QUARTERLY_MONTHS.index(quarter_month)
    if idx + 1 < len(QUARTERLY_MONTHS):
        return QUARTERLY_MONTHS[idx + 1], year
    return 3, year + 1


def _calendar_front_month(now: datetime) -> tuple[int, int]:
    for quarter_month in QUARTERLY_MONTHS:
        if now.month < quarter_month:
            return quarter_month, now.year
        if now.month == quarter_month:
            if now >= _calendar_roll_date(now.year, quarter_month):
                return _next_quarter_contract(quarter_month, now.year)
            return quarter_month, now.year
    return 3, now.year + 1


def active_mes_contract() -> str:
    """Estimate the active front-month MES contract for calendar diagnostics.

    Databento continuous symbols handle actual contract switching according to the
    configured rule (c/n/v). This helper is calendar-only and used for log context.
    It follows the CME equity-index customary roll date: Monday prior to the
    third Friday in Mar/Jun/Sep/Dec.
    """
    now = datetime.now(timezone.utc)
    contract_month, contract_year = _calendar_front_month(now)
    code = MONTH_CODES[contract_month]
    return f"MES{code}{contract_year % 100:02d}"


def detect_contract_roll() -> bool:
    """Check whether we are in a calendar roll window.

    For Databento n/v continuous rules, roll timing is market-data-driven and this
    helper intentionally returns False to avoid pretending calendar certainty.
    For c (calendar) rule, returns True when the customary roll week is active.
    """
    if DATABENTO_STYPE != "continuous":
        return False
    if DATABENTO_CONTINUOUS_RULE != "c":
        return False

    now = datetime.now(timezone.utc)
    if now.month not in QUARTERLY_MONTHS:
        return False

    roll_date = _calendar_roll_date(now.year, now.month)
    days_to_roll = (roll_date.date() - now.date()).days
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

    logger.info(
        "Databento live feed configured: symbol=%s stype=%s continuous_rule=%s",
        DATABENTO_SYMBOL,
        DATABENTO_STYPE,
        DATABENTO_CONTINUOUS_RULE,
    )

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
