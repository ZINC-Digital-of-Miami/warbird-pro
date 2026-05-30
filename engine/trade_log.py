"""Trade log — DuckDB-backed trade recording for pattern learning.

Records every entry signal, trade outcome (W/L), and pattern tags.
The model can query this to improve entry quality over time.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

import duckdb

from engine.config import TRADE_LOG_DB

_SCHEMA_SQL = [
    "CREATE SEQUENCE IF NOT EXISTS trade_id_seq START 1;",
    """CREATE TABLE IF NOT EXISTS trades (
        id              INTEGER PRIMARY KEY DEFAULT (nextval('trade_id_seq')),
        opened_at       TIMESTAMP NOT NULL,
        closed_at       TIMESTAMP,
        symbol          VARCHAR DEFAULT 'MES',
        timeframe       VARCHAR NOT NULL,
        direction       VARCHAR NOT NULL,
        entry_price     DOUBLE NOT NULL,
        stop_price      DOUBLE,
        tp_price        DOUBLE,
        exit_price      DOUBLE,
        pnl_pts         DOUBLE,
        result          VARCHAR,
        score           DOUBLE,
        conviction      VARCHAR,
        fib_level       VARCHAR,
        ema21           DOUBLE,
        ema9            DOUBLE,
        rsi             DOUBLE,
        pressure_pct    DOUBLE,
        squeeze_on      BOOLEAN,
        pattern_tags    VARCHAR[],
        notes           VARCHAR,
        ai_commentary   VARCHAR
    );""",
]


def _get_conn() -> duckdb.DuckDBPyConnection:
    db_path = os.path.abspath(TRADE_LOG_DB)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    for stmt in _SCHEMA_SQL:
        conn.execute(stmt)
    return conn


def init_db() -> str:
    """Initialize the DuckDB trade log database. Returns the path."""
    conn = _get_conn()
    count = conn.execute("SELECT count(*) FROM trades").fetchone()[0]
    conn.close()
    db_path = os.path.abspath(TRADE_LOG_DB)
    return f"{db_path} ({count} trades)"


@dataclass
class TradeEntry:
    """All fields for opening a new trade."""

    direction: str
    entry_price: float
    timeframe: str = "5m"
    stop_price: float | None = None
    tp_price: float | None = None
    score: float | None = None
    conviction: str | None = None
    fib_level: str | None = None
    ema21: float | None = None
    ema9: float | None = None
    rsi: float | None = None
    pressure_pct: float | None = None
    squeeze_on: bool | None = None
    pattern_tags: list[str] = field(default_factory=list)
    ai_commentary: str | None = None


def record_trade(entry: TradeEntry) -> int:
    """Record a new trade entry. Returns the trade ID."""
    conn = _get_conn()
    now = datetime.now(timezone.utc)
    trade_id = conn.execute(
        """INSERT INTO trades (
            opened_at, symbol, timeframe, direction, entry_price,
            stop_price, tp_price, score, conviction, fib_level,
            ema21, ema9, rsi, pressure_pct, squeeze_on,
            pattern_tags, result, ai_commentary
        ) VALUES (?, 'MES', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?)
        RETURNING id""",
        [
            now, entry.timeframe, entry.direction, entry.entry_price,
            entry.stop_price, entry.tp_price, entry.score,
            entry.conviction, entry.fib_level,
            entry.ema21, entry.ema9, entry.rsi,
            entry.pressure_pct, entry.squeeze_on,
            entry.pattern_tags, entry.ai_commentary,
        ],
    ).fetchone()[0]
    conn.close()
    return trade_id


def close_trade(
    trade_id: int,
    exit_price: float,
    result: str = "WIN",
    notes: str | None = None,
) -> None:
    """Close an existing trade with outcome."""
    conn = _get_conn()
    now = datetime.now(timezone.utc)
    conn.execute(
        """UPDATE trades
           SET closed_at = ?, exit_price = ?, result = ?,
               pnl_pts = CASE WHEN direction = 'SHORT'
                               THEN entry_price - ?
                               ELSE ? - entry_price
                          END,
               notes = ?
           WHERE id = ?""",
        [now, exit_price, result, exit_price, exit_price, notes, trade_id],
    )
    conn.close()


def get_recent_trades(limit: int = 20) -> list[dict]:
    """Get recent trades for the trade log card."""
    conn = _get_conn()
    rows = conn.execute(
        """SELECT id, opened_at, direction, entry_price, exit_price,
                  pnl_pts, result, score, pattern_tags, timeframe
           FROM trades ORDER BY opened_at DESC LIMIT ?""",
        [limit],
    ).fetchall()
    conn.close()
    return [
        {
            "id": r[0], "opened_at": str(r[1]), "direction": r[2],
            "entry_price": r[3], "exit_price": r[4], "pnl_pts": r[5],
            "result": r[6], "score": r[7], "pattern_tags": r[8],
            "timeframe": r[9],
        }
        for r in rows
    ]


def get_win_rate() -> dict:
    """Get aggregate win/loss stats."""
    conn = _get_conn()
    total = conn.execute("SELECT count(*) FROM trades WHERE result != 'OPEN'").fetchone()[0]
    wins = conn.execute("SELECT count(*) FROM trades WHERE result = 'WIN'").fetchone()[0]
    conn.close()
    return {
        "total": total,
        "wins": wins,
        "losses": total - wins,
        "win_rate": round(wins / total * 100, 1) if total > 0 else 0.0,
    }
