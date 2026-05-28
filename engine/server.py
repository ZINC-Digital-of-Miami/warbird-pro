"""Warbird Pro Trading Command Center — FastAPI server.

Serves the dashboard UI, WebSocket streams for real-time bars + signals,
and REST endpoints for historical data.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from engine.bar_store import Bar, BarStore
from engine.config import HOST, PORT
from engine.databento_feed import start_feed
from engine.fib_engine import FibState, compute_fibs
from engine.trigger_engine import TriggerResult, evaluate_trigger

logger = logging.getLogger("warbird.server")

# ── Globals ───────────────────────────────────────────────────────────────────

store = BarStore()
ws_clients: set[WebSocket] = set()
_feed_thread: threading.Thread | None = None
_feed_stop: threading.Event | None = None
_latest_fibs: FibState | None = None
_latest_trigger: TriggerResult | None = None


# ── Bar callback — push to all connected WebSocket clients ────────────────────

def _on_bar(tf: str, bar: Bar) -> None:
    """Called from the Databento feed thread whenever a bar closes."""
    global _latest_fibs, _latest_trigger

    msg: dict[str, Any] = {
        "type": "bar",
        "tf": tf,
        "bar": bar.to_dict(),
    }

    # Recompute fibs on 1h bar close (for structure).
    if tf == "1h":
        bars_1h = store.get_bars("1h")
        if len(bars_1h) >= 8:
            _latest_fibs = compute_fibs(bars_1h)
            if _latest_fibs:
                msg["fibs"] = _latest_fibs.to_dict()

    # Evaluate trigger on 1m bar (for entry timing).
    if tf == "1m" and _latest_fibs:
        bars_1m = store.get_bars("1m")
        if len(bars_1m) >= 30:
            direction = "LONG" if _latest_fibs.is_bullish else "SHORT"
            _latest_trigger = evaluate_trigger(bars_1m, _latest_fibs, direction)
            msg["trigger"] = _latest_trigger.to_dict()

    # Broadcast to WebSocket clients.
    payload = json.dumps(msg)
    _broadcast(payload)


def _broadcast(payload: str) -> None:
    """Send payload to all connected WebSocket clients (fire-and-forget)."""
    disconnected: list[WebSocket] = []
    for ws in ws_clients.copy():
        try:
            asyncio.run_coroutine_threadsafe(ws.send_text(payload), _loop)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        ws_clients.discard(ws)


_loop: asyncio.AbstractEventLoop


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _feed_thread, _feed_stop, _loop

    _loop = asyncio.get_running_loop()

    # Register bar callback.
    store.on_bar(_on_bar)

    # Start Databento feed (backfill + live stream).
    logger.info("Starting Databento feed…")
    _feed_thread, _feed_stop = start_feed(store)

    # Compute initial fibs from backfilled data.
    global _latest_fibs
    bars_1h = store.get_bars("1h")
    if len(bars_1h) >= 8:
        _latest_fibs = compute_fibs(bars_1h)

    logger.info("Warbird engine ready — listening on %s:%d", HOST, PORT)
    yield

    # Shutdown.
    if _feed_stop:
        _feed_stop.set()
    if _feed_thread:
        _feed_thread.join(timeout=5)


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


@app.get("/api/fibs")
async def get_fibs():
    """Return current fibonacci state."""
    if _latest_fibs:
        return _latest_fibs.to_dict()
    return {"levels": [], "anchorHigh": 0, "anchorLow": 0, "isBullish": True, "fibRange": 0}


@app.get("/api/trigger")
async def get_trigger():
    """Return latest trigger evaluation."""
    if _latest_trigger:
        return _latest_trigger.to_dict()
    return {"decision": "NO_GO", "score": 0}


@app.get("/api/status")
async def get_status():
    """Health check with feed status."""
    bars_1m = store.get_bars("1m")
    last = bars_1m[-1] if bars_1m else None
    return {
        "status": "ok",
        "feed": "connected" if _feed_thread and _feed_thread.is_alive() else "disconnected",
        "bars_1m": len(bars_1m),
        "bars_5m": len(store.get_bars("5m")),
        "bars_15m": len(store.get_bars("15m")),
        "bars_1h": len(store.get_bars("1h")),
        "last_bar": last.to_dict() if last else None,
        "ws_clients": len(ws_clients),
        "fibs": _latest_fibs is not None,
        "trigger": _latest_trigger.decision if _latest_trigger else None,
    }


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket connection for real-time bar + signal streaming.

    On connect, sends a snapshot of current state (bars, fibs, trigger).
    Then pushes incremental updates as bars close.
    """
    await ws.accept()
    ws_clients.add(ws)
    logger.info("WebSocket client connected (%d total)", len(ws_clients))

    try:
        # Send initial snapshot.
        snapshot: dict[str, Any] = {
            "type": "snapshot",
            "bars": {},
        }
        for tf in ["1m", "5m", "15m", "1h", "4h"]:
            bars = store.get_bars(tf)
            snapshot["bars"][tf] = [b.to_dict() for b in bars[-500:]]

        if _latest_fibs:
            snapshot["fibs"] = _latest_fibs.to_dict()
        if _latest_trigger:
            snapshot["trigger"] = _latest_trigger.to_dict()

        await ws.send_text(json.dumps(snapshot))

        # Keep alive — wait for client messages or disconnect.
        while True:
            data = await ws.receive_text()
            # Client can send TF change requests, etc.
            try:
                msg = json.loads(data)
                if msg.get("type") == "subscribe":
                    # Future: per-client TF subscriptions.
                    pass
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(ws)
        logger.info("WebSocket client disconnected (%d remaining)", len(ws_clients))


# ── Static Files (dashboard UI) ──────────────────────────────────────────────

DASHBOARD_DIR = Path(__file__).parent.parent / "dashboard"


@app.get("/")
async def serve_dashboard():
    index = DASHBOARD_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return HTMLResponse("<h1>Warbird Pro — Dashboard not built yet</h1>")


if DASHBOARD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR)), name="static")
