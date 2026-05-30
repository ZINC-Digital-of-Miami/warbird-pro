"""Centralized engine lifecycle manager.

Manages the COLD/WARMING/WARM/COOLDOWN state machine based on WebSocket
client presence.  Starts/stops Databento feed, compute engines, and
timers based on client count.

State transitions:
    COLD -> WARMING: First client connects
    WARMING -> WARM: Databento feed established, data flowing
    WARM -> COOLDOWN: Last client disconnects, 60s grace period starts
    COOLDOWN -> COLD: Grace period expired, no reconnection
    COOLDOWN -> WARM: Client reconnects during grace period
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable

from engine.bar_store import BarStore
from engine.config import COOLDOWN_PERIOD_S, ENGINE_STATES

logger = logging.getLogger("warbird.lifecycle")

StateCallback = Callable[[str, str], None]  # (old_state, new_state)


class LifecycleManager:
    """Manages engine state based on client presence."""

    def __init__(self, store: BarStore) -> None:
        self._store = store
        self._state: str = "COLD"
        self._lock = threading.RLock()
        self._client_count: int = 0
        self._cooldown_timer: threading.Timer | None = None
        self._feed_thread: threading.Thread | None = None
        self._feed_stop: threading.Event | None = None
        self._state_callbacks: list[StateCallback] = []
        self._started = False

    @property
    def state(self) -> str:
        with self._lock:
            return self._state

    @property
    def client_count(self) -> int:
        with self._lock:
            return self._client_count

    def on_state_change(self, cb: StateCallback) -> None:
        """Register a callback for state transitions."""
        with self._lock:
            self._state_callbacks.append(cb)

    def client_connected(self) -> None:
        """Signal that a WebSocket client has connected."""
        with self._lock:
            self._client_count += 1
            count = self._client_count
            current = self._state

            logger.info("Client connected (total: %d, state: %s)", count, current)

            if current == "COLD":
                self._transition("WARMING")
                self._start_engine()
                self._transition("WARM")
            elif current == "COOLDOWN":
                self._cancel_cooldown()
                self._transition("WARM")

    def client_disconnected(self) -> None:
        """Signal that a WebSocket client has disconnected."""
        with self._lock:
            self._client_count = max(0, self._client_count - 1)
            count = self._client_count
            current = self._state

            logger.info("Client disconnected (total: %d, state: %s)", count, current)

            if count == 0 and current == "WARM":
                self._transition("COOLDOWN")
                self._start_cooldown()

    def force_cold(self) -> None:
        """Force the engine to COLD state (e.g., on server shutdown)."""
        self._cancel_cooldown()
        self._stop_engine()
        self._transition("COLD")

    def _transition(self, new_state: str) -> None:
        """Perform a state transition."""
        with self._lock:
            old = self._state
            if old == new_state:
                return
            if new_state not in ENGINE_STATES:
                logger.error("Invalid state transition: %s -> %s", old, new_state)
                return
            self._state = new_state
            callbacks = list(self._state_callbacks)

        logger.info("State transition: %s -> %s", old, new_state)
        for cb in callbacks:
            try:
                cb(old, new_state)
            except Exception:
                logger.exception("State callback error")

    def _start_engine(self) -> None:
        """Start the Databento feed."""
        from engine.databento_feed import start_feed

        if self._feed_thread and self._feed_thread.is_alive():
            return

        logger.info("Starting Databento feed...")
        self._feed_thread, self._feed_stop = start_feed(self._store)
        self._started = True

    def _stop_engine(self) -> None:
        """Stop the Databento feed."""
        from engine.databento_feed import stop_feed

        if self._feed_thread or self._feed_stop:
            logger.info("Stopping Databento feed...")
            stop_feed(self._feed_thread, self._feed_stop)
            self._feed_thread = None
            self._feed_stop = None
            self._started = False

    def _start_cooldown(self) -> None:
        """Start the cooldown timer."""
        self._cancel_cooldown()
        self._cooldown_timer = threading.Timer(
            COOLDOWN_PERIOD_S, self._cooldown_expired
        )
        self._cooldown_timer.daemon = True
        self._cooldown_timer.start()
        logger.info("Cooldown started (%ds grace period)", COOLDOWN_PERIOD_S)

    def _cancel_cooldown(self) -> None:
        """Cancel the cooldown timer if running."""
        if self._cooldown_timer:
            self._cooldown_timer.cancel()
            self._cooldown_timer = None

    def _cooldown_expired(self) -> None:
        """Called when cooldown period expires without reconnection."""
        with self._lock:
            count = self._client_count
            current = self._state

            if count == 0 and current == "COOLDOWN":
                logger.info("Cooldown expired - transitioning to COLD")
                self._stop_engine()
                self._transition("COLD")
            else:
                logger.info("Cooldown expired but clients present - staying WARM")
                self._transition("WARM")

    def status(self) -> dict:
        """Return current lifecycle status."""
        with self._lock:
            return {
                "state": self._state,
                "clients": self._client_count,
                "feed_alive": bool(
                    self._feed_thread and self._feed_thread.is_alive()
                ),
                "bars_ingested": self._store.total_bars_ingested,
            }
