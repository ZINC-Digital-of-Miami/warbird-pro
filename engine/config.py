"""Warbird engine configuration — all tunables in one place."""

from __future__ import annotations

import os

# ── Databento ─────────────────────────────────────────────────────────────────
DATABENTO_API_KEY: str = os.environ.get("DATABENTO_API_KEY", "")
DATABENTO_DATASET: str = "GLBX.MDP3"
DATABENTO_SYMBOL: str = "MES.n.0"
DATABENTO_STYPE: str = "continuous"

# ── Server ────────────────────────────────────────────────────────────────────
HOST: str = os.environ.get("WARBIRD_HOST", "127.0.0.1")
PORT: int = int(os.environ.get("WARBIRD_PORT", "3100"))

# ── Timeframes ────────────────────────────────────────────────────────────────
# Bars are streamed at 1m resolution and aggregated to higher TFs in-process.
AGGREGATION_PERIODS: dict[str, int] = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "4h": 240,
    "1d": 1440,
}

# How many bars of each TF to keep in memory for the chart backfill.
MAX_BARS_IN_MEMORY: int = 5000

# ── Fib Engine (V9 canonical settings — CLAUDE.md 2026-05-13) ────────────────
ZIGZAG_DEVIATION: float = 3.0
ZIGZAG_DEPTH: int = 10
ZIGZAG_THRESHOLD_FLOOR_PCT: float = 0.25
HTF_CONFLUENCE_TOLERANCE_PCT: float = 1.5
HTF_1H_LOOKBACK: int = 8
MIN_FIB_RANGE_ATR: float = 0.5
MIDPOINT_HYSTERESIS_PCT: float = 2.0

FIB_RATIOS: list[float] = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
FIB_EXTENSIONS: list[float] = [1.236, 1.618, 2.0]

# ── MA Gate (V9 canonical — 2026-05-13) ───────────────────────────────────────
PRIMARY_EMA_LENGTH: int = 21
SMOOTHING_TYPE: str = "EMA"
SMOOTHING_LENGTH: int = 9

# ── Trigger Engine ────────────────────────────────────────────────────────────
ZONE_PROXIMITY_PTS: float = 4.0
REJECTION_WICK_RATIO: float = 2.0
TRIGGER_GO_THRESHOLD: float = 0.55
TRIGGER_WAIT_THRESHOLD: float = 0.35
VOLUME_BASELINE_BARS: int = 20
TRIGGER_LOOKBACK_1M: int = 30

# ── Pressure Bar ──────────────────────────────────────────────────────────────
PRESSURE_NEUTRAL_THRESHOLD_BPS: float = 0.75
PRESSURE_DOMINANCE_PCT: float = 55.0

# ── News / Calendar ───────────────────────────────────────────────────────────
FINNHUB_API_KEY: str = os.environ.get("FINNHUB_API_KEY", "")
NEWS_POLL_INTERVAL_SEC: int = 30

# ── AI (OpenRouter preferred — cheaper, multi-model access) ───────────────────
OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
AI_MODEL: str = os.environ.get("WARBIRD_AI_MODEL", "mistralai/mistral-medium-3-5")
AI_BASE_URL: str = os.environ.get(
    "WARBIRD_AI_BASE_URL",
    "https://openrouter.ai/api/v1" if OPENROUTER_API_KEY else "https://api.openai.com/v1",
)

def get_ai_key() -> str:
    return OPENROUTER_API_KEY or OPENAI_API_KEY or ""

# ── Trade Log ─────────────────────────────────────────────────────────────────
TRADE_LOG_DB: str = os.environ.get(
    "WARBIRD_TRADE_DB",
    os.path.join(os.path.dirname(__file__), "..", "data", "warbird_trades.duckdb"),
)

# ── MES tick size ─────────────────────────────────────────────────────────────
MES_TICK: float = 0.25
