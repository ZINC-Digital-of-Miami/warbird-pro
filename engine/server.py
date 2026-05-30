"""Warbird Pro — WebSocket server with client-presence lifecycle.

Serves the dashboard UI, WebSocket streams for real-time bars,
and REST endpoints for historical data.  Engine lifecycle (COLD/WARMING/
WARM/COOLDOWN) is driven by WebSocket client-presence via LifecycleManager.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from engine.bar_store import Bar, BarStore
from engine.config import HOST, PORT
from engine.lifecycle import LifecycleManager

logger = logging.getLogger("warbird.server")

# ── Globals ───────────────────────────────────────────────────────────────────

store = BarStore()
lifecycle = LifecycleManager(store)
ws_clients: set[WebSocket] = set()
_loop: asyncio.AbstractEventLoop | None = None


# ── Bar callback — push to all connected WebSocket clients ────────────────────

def _on_bar(tf: str, bar: Bar) -> None:
    """Called from the Databento feed thread whenever a bar closes."""
    msg: dict[str, Any] = {
        "type": "bar",
        "tf": tf,
        "bar": bar.to_dict(),
    }
    payload = json.dumps(msg)
    _broadcast(payload)


def _broadcast(payload: str) -> None:
    """Send payload to all connected WebSocket clients (fire-and-forget)."""
    if not _loop or not ws_clients:
        return
    disconnected: list[WebSocket] = []
    for ws in ws_clients.copy():
        try:
            asyncio.run_coroutine_threadsafe(ws.send_text(payload), _loop)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        ws_clients.discard(ws)


# ── DuckDB persistence — write bars to DuckDB tables ─────────────────────────

def _persist_bar_to_duckdb(tf: str, bar: Bar) -> None:
    """Write a closed bar to the DuckDB bar table for the given timeframe."""
    try:
        import duckdb
        from engine.config import DUCKDB_PATH

        table_name = f"bars_{tf}"
        conn = duckdb.connect(DUCKDB_PATH)
        conn.execute(f"""
            INSERT OR IGNORE INTO {table_name} (ts, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [bar.ts, bar.open, bar.high, bar.low, bar.close, bar.volume])
        conn.close()
    except Exception:
        logger.debug("DuckDB persist skipped for %s (table may not exist)", tf)


def _on_bar_with_persist(tf: str, bar: Bar) -> None:
    """Combined callback: broadcast + DuckDB persist."""
    _on_bar(tf, bar)
    _persist_bar_to_duckdb(tf, bar)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _loop
    _loop = asyncio.get_running_loop()

    store.on_bar(_on_bar_with_persist)

    logger.info("Warbird server ready — listening on %s:%d (state: COLD)", HOST, PORT)
    yield

    lifecycle.force_cold()
    logger.info("Server shutdown complete")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="Warbird Pro", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REST Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/bars/{tf}")
async def get_bars(tf: str, limit: int = 500):
    """Return historical bars for a given timeframe."""
    bars = store.get_bars(tf)
    return [b.to_dict() for b in bars[-limit:]]


@app.get("/api/status")
async def get_status():
    """Health check with lifecycle status."""
    status = lifecycle.status()
    bars_1m = store.get_bars("1m")
    last = bars_1m[-1] if bars_1m else None
    return {
        **status,
        "bars_1m": len(bars_1m),
        "bars_5m": store.bar_count("5m"),
        "bars_15m": store.bar_count("15m"),
        "bars_1h": store.bar_count("1h"),
        "last_bar": last.to_dict() if last else None,
        "ws_clients": len(ws_clients),
    }


@app.get("/api/lifecycle")
async def get_lifecycle():
    """Return current lifecycle state machine status."""
    return lifecycle.status()


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket connection for real-time bar streaming.

    On connect: triggers lifecycle WARMING if COLD, sends snapshot.
    On disconnect: triggers lifecycle COOLDOWN if last client.
    """
    await ws.accept()
    ws_clients.add(ws)
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lifecycle.client_connected)

    try:
        snapshot: dict[str, Any] = {
            "type": "snapshot",
            "bars": {},
            "lifecycle": lifecycle.status(),
        }
        for tf in ["1m", "3m", "5m", "15m", "1h", "4h", "1d"]:
            bars = store.get_bars(tf)
            snapshot["bars"][tf] = [b.to_dict() for b in bars[-500:]]

        await ws.send_text(json.dumps(snapshot))

        while True:
            data = await ws.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await ws.send_text(json.dumps({"type": "pong"}))
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(ws)
        lifecycle.client_disconnected()


# ── Static Files (dashboard UI) ──────────────────────────────────────────────

DASHBOARD_DIR = Path(__file__).parent.parent / "dashboard"


@app.get("/")
async def serve_dashboard():
    index = DASHBOARD_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return HTMLResponse("<h1>Warbird Pro - Dashboard not built yet</h1>")


if DASHBOARD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR)), name="static")
