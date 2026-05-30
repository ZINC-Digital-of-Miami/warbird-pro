"""Tests for engine/lifecycle.py — state machine + client presence."""

from __future__ import annotations

import time
import threading
from unittest.mock import patch, MagicMock

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
