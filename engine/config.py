"""Engine configuration — Databento allowlists, lifecycle, API key refs, cost caps.

All API keys read from environment variables (via .env). Never hardcode secrets.
"""

from __future__ import annotations

import os


def normalize_databento_continuous_rule(rule: str) -> str:
    """Normalize Databento continuous rule aliases to canonical c/n/v tokens."""
    normalized = str(rule).strip().lower()
    aliases = {
        "calendar": "c",
        "c": "c",
        "open_interest": "n",
        "open-interest": "n",
        "openinterest": "n",
        "oi": "n",
        "o": "n",
        "n": "n",
        "volume": "v",
        "v": "v",
    }
    canonical = aliases.get(normalized, normalized)
    if canonical not in {"c", "n", "v"}:
        raise ValueError(
            "Invalid DATABENTO_CONTINUOUS_RULE. Use one of c/n/v (or aliases calendar/open_interest/volume)."
        )
    return canonical

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
DATABENTO_CONTINUOUS_ROOT: str = os.environ.get("DATABENTO_CONTINUOUS_ROOT", "MES").strip().upper()
DATABENTO_CONTINUOUS_RULE: str = normalize_databento_continuous_rule(
    os.environ.get("DATABENTO_CONTINUOUS_RULE", "n")
)
DATABENTO_CONTINUOUS_RANK: int = int(os.environ.get("DATABENTO_CONTINUOUS_RANK", "0"))
if DATABENTO_CONTINUOUS_RANK < 0:
    raise ValueError("DATABENTO_CONTINUOUS_RANK must be >= 0")

DATABENTO_SYMBOL: str = (
    f"{DATABENTO_CONTINUOUS_ROOT}.{DATABENTO_CONTINUOUS_RULE}.{DATABENTO_CONTINUOUS_RANK}"
)
DATABENTO_STYPE: str = "continuous"

DATABENTO_APPROVED_SYMBOLS: list[str] = [
    "MES.c.0", "MES.n.0", "MES.v.0",
    "ES.c.0", "NQ.c.0", "YM.c.0", "RTY.c.0",
    "CL.c.0", "GC.c.0", "SI.c.0", "NG.c.0",
    "ZN.c.0", "ZB.c.0", "ZF.c.0",
    "SOX.c.0", "SR3.c.0",
    "6E.c.0", "6J.c.0", "HG.c.0",
]
if DATABENTO_SYMBOL not in DATABENTO_APPROVED_SYMBOLS:
    raise ValueError(
        f"DATABENTO_SYMBOL {DATABENTO_SYMBOL!r} is not in DATABENTO_APPROVED_SYMBOLS"
    )

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
# Server
# ---------------------------------------------------------------------------
HOST: str = os.environ.get("WARBIRD_HOST", "127.0.0.1")
PORT: int = int(os.environ.get("WARBIRD_PORT", "3100"))

# ---------------------------------------------------------------------------
# Timeframe aggregation
# ---------------------------------------------------------------------------
AGGREGATION_PERIODS: dict[str, int] = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "4h": 240,
    "1d": 1440,
}
MAX_BARS_IN_MEMORY: int = 5000

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

# ---------------------------------------------------------------------------
# Bar validation
# ---------------------------------------------------------------------------
BAR_VALIDATION_ENABLED: bool = True
