"""Engine configuration — Databento allowlists, lifecycle, API key refs, cost caps.

All API keys read from environment variables (via .env). Never hardcode secrets.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Database paths
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DUCKDB_PATH = os.path.join(DATA_DIR, "warbird_trades.duckdb")
TRADE_LOG_DB = DUCKDB_PATH

# ---------------------------------------------------------------------------
# API key references — read from .env via os.environ, never hardcode
# ---------------------------------------------------------------------------
DATABENTO_API_KEY = os.environ.get("DATABENTO_API_KEY", "")
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
FINANCIALDATA_API_KEY = os.environ.get("FINANCIALDATA_API_KEY", "")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
NEWSFILTER_API_KEY = os.environ.get("NEWSFILTER_API_KEY", "")

# ---------------------------------------------------------------------------
# Databento allowlists — approved symbols and schemas
# ---------------------------------------------------------------------------
DATABENTO_DATASET = "GLBX.MDP3"

DATABENTO_APPROVED_SYMBOLS: list[str] = [
    "MES.v.0", "ES.c.0", "NQ.c.0", "YM.c.0", "RTY.c.0",
    "CL.c.0", "GC.c.0", "SI.c.0", "NG.c.0",
    "ZN.c.0", "ZB.c.0", "ZF.c.0",
    "SOX.c.0", "SR3.c.0",
    "6E.c.0", "6J.c.0", "HG.c.0",
]

DATABENTO_APPROVED_SCHEMAS: list[str] = [
    "ohlcv-1m",
    "ohlcv-1h",
    "trades",
]

# Correlation symbols (1h isolated update cycle)
CORRELATION_SYMBOLS: list[str] = ["NQ", "6E", "CL", "ZN"]

# ---------------------------------------------------------------------------
# Engine lifecycle configuration
# ---------------------------------------------------------------------------
COOLDOWN_PERIOD_S = 60
RECONNECT_ATTEMPTS = 3
BACKOFF_BASE_S = 2.0

# Engine states
ENGINE_STATES = ("COLD", "WARMING", "WARM", "COOLDOWN")

# ---------------------------------------------------------------------------
# Cost cap rules — Historical API gap-fill
# ---------------------------------------------------------------------------
GAP_FILL_AUTO_HOURS = 6       # < 6h: auto gap-fill
GAP_FILL_WARN_HOURS = 24      # > 6h and <= 24h: warn before filling
# > 24h: refuse and require manual approval

# ---------------------------------------------------------------------------
# Canonical timeframes
# ---------------------------------------------------------------------------
CANONICAL_TIMEFRAMES: list[str] = ["1m", "3m", "5m", "15m", "1h", "4h", "1d"]
DEFAULT_TIMEFRAME = "5m"

# ---------------------------------------------------------------------------
# Chart TF switching (cards update with TF, correlations always 1h)
# ---------------------------------------------------------------------------
CHART_TIMEFRAMES: list[str] = ["1m", "3m", "5m", "15m"]
CORRELATIONS_TF = "1h"
CORRELATIONS_UPDATE_INTERVAL_S = 3600

# ---------------------------------------------------------------------------
# Fib engine constants — match live TradingView indicator inputs exactly
# ---------------------------------------------------------------------------
ZIGZAG_DEVIATION = 3.0
ZIGZAG_DEPTH = 10
ZIGZAG_THRESHOLD_FLOOR_PCT = 0.25
MIN_FIB_RANGE_ATR = 0.5
MIDPOINT_HYSTERESIS_PCT = 2.0

FIB_RATIOS: list[float] = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
FIB_EXTENSIONS: list[float] = [1.236, 1.382, 1.5, 1.618, 2.0, 2.236]
