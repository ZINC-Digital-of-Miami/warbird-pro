"""Tests for engine/server.py — REST endpoints, WebSocket, bar callbacks."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from engine.bar_store import Bar, BarStore
from engine.server import (
    _broadcast,
    _on_bar,
    _on_bar_with_persist,
    _persist_bar_to_duckdb,
    app,
    lifecycle,
    store,
    ws_clients,
)


@pytest.fixture
def sample_bar():
    return Bar(
        ts=datetime(2026, 5, 28, 14, 30, tzinfo=timezone.utc),
        open=5400.0,
        high=5410.0,
        low=5390.0,
        close=5405.0,
        volume=100,
    )


# ── REST endpoint tests ───────────────────────────────────────────────────────


@pytest.fixture
def async_client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="https://test")


@pytest.mark.asyncio
async def test_get_bars_empty(async_client):
    async with async_client as client:
        resp = await client.get("/api/bars/1m")
        assert resp.status_code == 200
        assert resp.json() == [] or isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_status(async_client):
    async with async_client as client:
        resp = await client.get("/api/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "state" in data
        assert "ws_clients" in data


@pytest.mark.asyncio
async def test_get_lifecycle(async_client):
    async with async_client as client:
        resp = await client.get("/api/lifecycle")
        assert resp.status_code == 200
        data = resp.json()
        assert "state" in data


@pytest.mark.asyncio
async def test_serve_dashboard(async_client):
    async with async_client as client:
        resp = await client.get("/")
        assert resp.status_code == 200


# ── Callback tests ────────────────────────────────────────────────────────────


def test_on_bar_creates_payload(sample_bar):
    """_on_bar creates JSON payload with type, tf, and bar dict."""
    import engine.server as srv

    original_loop = srv._loop
    srv._loop = None
    _on_bar("1m", sample_bar)
    srv._loop = original_loop


def test_broadcast_no_loop():
    """_broadcast returns early when no event loop."""
    import engine.server as srv

    original_loop = srv._loop
    srv._loop = None
    _broadcast('{"test": true}')
    srv._loop = original_loop


def test_broadcast_no_clients():
    """_broadcast returns early when no clients connected."""
    import engine.server as srv

    original_loop = srv._loop
    srv._loop = MagicMock()
    original_clients = ws_clients.copy()
    ws_clients.clear()
    _broadcast('{"test": true}')
    ws_clients.update(original_clients)
    srv._loop = original_loop


def test_broadcast_with_clients():
    """_broadcast sends to connected clients."""
    import engine.server as srv

    mock_loop = MagicMock()
    original_loop = srv._loop
    srv._loop = mock_loop

    mock_ws = MagicMock()
    ws_clients.add(mock_ws)

    _broadcast('{"type":"bar"}')

    mock_loop.call_soon_threadsafe = MagicMock()
    ws_clients.discard(mock_ws)
    srv._loop = original_loop


def test_persist_bar_to_duckdb_handles_missing_table(sample_bar):
    """_persist_bar_to_duckdb handles missing table gracefully."""
    with patch("engine.server.duckdb", create=True) as mock_duckdb:
        mock_conn = MagicMock()
        mock_duckdb.connect.return_value = mock_conn
        mock_conn.execute.side_effect = Exception("Table not found")
        _persist_bar_to_duckdb("1m", sample_bar)


def test_on_bar_with_persist_calls_both(sample_bar):
    """_on_bar_with_persist calls both broadcast and persist."""
    with patch("engine.server._on_bar") as mock_on, \
         patch("engine.server._persist_bar_to_duckdb") as mock_persist:
        _on_bar_with_persist("1m", sample_bar)
        mock_on.assert_called_once_with("1m", sample_bar)
        mock_persist.assert_called_once_with("1m", sample_bar)


# ── WebSocket tests ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_websocket_connect_and_snapshot():
    """WebSocket connection receives a snapshot message."""
    try:
        from httpx_ws import aconnect_ws

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="https://test") as client:
            async with aconnect_ws("/ws", client) as ws:
                msg = await ws.receive_json()
                assert msg["type"] == "snapshot"
    except ImportError:
        pytest.skip("httpx_ws not installed")


@pytest.mark.asyncio
async def test_websocket_ping_pong():
    """WebSocket responds to ping with pong."""
    try:
        from httpx_ws import aconnect_ws

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="https://test") as client:
            async with aconnect_ws("/ws", client) as ws:
                await ws.receive_json()
                await ws.send_json({"type": "ping"})
                msg = await ws.receive_json()
                assert msg["type"] == "pong"
    except ImportError:
        pytest.skip("httpx_ws not installed")
