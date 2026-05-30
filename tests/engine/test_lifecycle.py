"""Tests for engine/lifecycle.py — state machine + client presence."""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from engine.bar_store import BarStore
from engine.lifecycle import LifecycleManager


@pytest.fixture
def store():
    return BarStore(max_bars=100)


@pytest.fixture
def mgr(store):
    return LifecycleManager(store)


def test_initial_state_is_cold(mgr):
    assert mgr.state == "COLD"
    assert mgr.client_count == 0


@patch("engine.lifecycle.LifecycleManager._start_engine")
def test_first_client_transitions_to_warming(mock_start, mgr):
    mgr.client_connected()
    assert mgr.state == "WARM"  # transitions COLD -> WARMING -> WARM
    assert mgr.client_count == 1
    mock_start.assert_called_once()


@patch("engine.lifecycle.LifecycleManager._start_engine")
def test_multiple_clients_stay_warm(mock_start, mgr):
    mgr.client_connected()
    mgr.client_connected()
    mgr.client_connected()
    assert mgr.state == "WARM"
    assert mgr.client_count == 3


@patch("engine.lifecycle.LifecycleManager._start_engine")
def test_last_client_disconnect_starts_cooldown(mock_start, mgr):
    mgr.client_connected()
    mgr.client_disconnected()
    assert mgr.state == "COOLDOWN"
    assert mgr.client_count == 0


@patch("engine.lifecycle.LifecycleManager._start_engine")
def test_reconnect_during_cooldown_returns_to_warm(mock_start, mgr):
    mgr.client_connected()
    mgr.client_disconnected()
    assert mgr.state == "COOLDOWN"
    mgr.client_connected()
    assert mgr.state == "WARM"


@patch("engine.lifecycle.LifecycleManager._start_engine")
@patch("engine.lifecycle.LifecycleManager._stop_engine")
def test_force_cold(mock_stop, mock_start, mgr):
    mgr.client_connected()
    mgr.force_cold()
    assert mgr.state == "COLD"
    mock_stop.assert_called_once()


@patch("engine.lifecycle.LifecycleManager._start_engine")
def test_state_callback_fired(mock_start, mgr):
    transitions = []
    mgr.on_state_change(lambda old, new: transitions.append((old, new)))
    mgr.client_connected()
    assert ("COLD", "WARMING") in transitions
    assert ("WARMING", "WARM") in transitions


@patch("engine.lifecycle.LifecycleManager._start_engine")
def test_status_dict(mock_start, mgr):
    mgr.client_connected()
    status = mgr.status()
    assert status["state"] == "WARM"
    assert status["clients"] == 1
    assert "feed_alive" in status
    assert "bars_ingested" in status


@patch("engine.lifecycle.LifecycleManager._start_engine")
def test_client_count_never_negative(mock_start, mgr):
    mgr.client_disconnected()
    mgr.client_disconnected()
    assert mgr.client_count == 0


# ── Cooldown expiry tests ─────────────────────────────────────────────────────


@patch("engine.lifecycle.LifecycleManager._start_engine")
@patch("engine.lifecycle.LifecycleManager._stop_engine")
@patch("engine.lifecycle.COOLDOWN_PERIOD_S", 0.05)
def test_cooldown_expires_to_cold(mock_stop, mock_start, mgr):
    """Cooldown timer transitions to COLD when expired with no clients."""
    mgr.client_connected()
    mgr.client_disconnected()
    assert mgr.state == "COOLDOWN"
    time.sleep(0.15)
    assert mgr.state == "COLD"
    mock_stop.assert_called_once()


@patch("engine.lifecycle.LifecycleManager._start_engine")
@patch("engine.lifecycle.LifecycleManager._stop_engine")
@patch("engine.lifecycle.COOLDOWN_PERIOD_S", 0.05)
def test_cooldown_cancelled_on_reconnect(mock_stop, mock_start, mgr):
    """Cooldown timer is cancelled when client reconnects."""
    mgr.client_connected()
    mgr.client_disconnected()
    assert mgr.state == "COOLDOWN"
    mgr.client_connected()
    assert mgr.state == "WARM"
    time.sleep(0.15)
    assert mgr.state == "WARM"
    mock_stop.assert_not_called()


@patch("engine.lifecycle.LifecycleManager._start_engine")
@patch("engine.lifecycle.COOLDOWN_PERIOD_S", 0.05)
def test_cooldown_expired_with_clients_stays_warm(mock_start, mgr):
    """If clients present when timer fires, stay WARM."""
    mgr.client_connected()
    mgr.client_connected()
    mgr.client_disconnected()
    assert mgr.state == "WARM"
    assert mgr.client_count == 1


# ── State transition edge cases ───────────────────────────────────────────────


@patch("engine.lifecycle.LifecycleManager._start_engine")
def test_invalid_state_transition_ignored(mock_start, mgr):
    """Invalid state transition does not crash."""
    mgr._transition("INVALID_STATE")
    assert mgr.state == "COLD"


@patch("engine.lifecycle.LifecycleManager._start_engine")
def test_same_state_transition_noop(mock_start, mgr):
    """Transition to same state is a no-op."""
    mgr._transition("COLD")
    assert mgr.state == "COLD"


@patch("engine.lifecycle.LifecycleManager._start_engine")
def test_state_callback_exception_handled(mock_start, mgr):
    """State callback exceptions don't crash the manager."""
    def bad_callback(old, new):
        raise RuntimeError("callback error")

    mgr.on_state_change(bad_callback)
    mgr.client_connected()
    assert mgr.state == "WARM"


# ── Engine start/stop integration ─────────────────────────────────────────────


def test_start_engine_with_mock_feed(store):
    """_start_engine calls start_feed."""
    mgr = LifecycleManager(store)
    mock_thread = MagicMock()
    mock_event = MagicMock()
    with patch("engine.databento_feed.start_feed", return_value=(mock_thread, mock_event)):
        mgr._start_engine()
    assert mgr._started is True
    assert mgr._feed_thread is mock_thread


def test_start_engine_idempotent(store):
    """_start_engine doesn't restart if already running."""
    mgr = LifecycleManager(store)
    mock_thread = MagicMock()
    mock_thread.is_alive.return_value = True
    mgr._feed_thread = mock_thread
    with patch("engine.databento_feed.start_feed") as mock_sf:
        mgr._start_engine()
    mock_sf.assert_not_called()


def test_stop_engine_calls_stop_feed(store):
    """_stop_engine calls stop_feed with thread and event."""
    mgr = LifecycleManager(store)
    mock_thread = MagicMock()
    mock_event = MagicMock()
    mgr._feed_thread = mock_thread
    mgr._feed_stop = mock_event
    mgr._started = True
    with patch("engine.databento_feed.stop_feed") as mock_sf:
        mgr._stop_engine()
    mock_sf.assert_called_once_with(mock_thread, mock_event)
    assert mgr._feed_thread is None
    assert mgr._feed_stop is None
    assert mgr._started is False


def test_stop_engine_noop_when_not_running(store):
    """_stop_engine is a no-op when nothing is running."""
    mgr = LifecycleManager(store)
    with patch("engine.databento_feed.stop_feed") as mock_sf:
        mgr._stop_engine()
    mock_sf.assert_not_called()


# ── Race condition prevention ─────────────────────────────────────────────────


@patch("engine.lifecycle.LifecycleManager._start_engine")
@patch("engine.lifecycle.LifecycleManager._stop_engine")
@patch("engine.lifecycle.COOLDOWN_PERIOD_S", 0.05)
def test_race_cooldown_vs_connect(mock_stop, mock_start, mgr):
    """Race between cooldown expiry and client reconnect is handled atomically."""
    mgr.client_connected()
    mgr.client_disconnected()
    assert mgr.state == "COOLDOWN"
    mgr.client_connected()
    assert mgr.state == "WARM"
    time.sleep(0.15)
    assert mgr.state == "WARM"
