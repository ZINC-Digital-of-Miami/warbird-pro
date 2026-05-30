"""Tests for engine/trade_log.py — trade recording and querying."""

from __future__ import annotations

import duckdb
import pytest


@pytest.fixture()
def tmp_trade_db(monkeypatch, tmp_path):
    """Patch TRADE_LOG_DB to a temp directory."""
    db_path = str(tmp_path / "trades_test.duckdb")
    monkeypatch.setattr("engine.config.TRADE_LOG_DB", db_path)
    monkeypatch.setattr("engine.trade_log.TRADE_LOG_DB", db_path)
    return db_path


def test_record_trade_returns_sequential_ids(tmp_trade_db):
    from engine.trade_log import TradeEntry, record_trade

    e1 = TradeEntry(direction="LONG", entry_price=5400.0)
    e2 = TradeEntry(direction="SHORT", entry_price=5410.0)
    tid1 = record_trade(e1)
    tid2 = record_trade(e2)
    assert tid1 == 1
    assert tid2 == 2


def test_record_trade_returning_is_atomic(tmp_trade_db):
    from engine.trade_log import TradeEntry, record_trade

    tid = record_trade(TradeEntry(direction="LONG", entry_price=5400.0))
    assert isinstance(tid, int)
    assert tid >= 1


def test_close_trade_long_positive_pnl(tmp_trade_db):
    from engine.trade_log import TradeEntry, close_trade, record_trade

    tid = record_trade(TradeEntry(direction="LONG", entry_price=5400.0))
    close_trade(tid, exit_price=5410.0, result="WIN")

    conn = duckdb.connect(tmp_trade_db)
    row = conn.execute("SELECT pnl_pts, result FROM trades WHERE id=?", [tid]).fetchone()
    conn.close()
    assert row[0] == 10.0
    assert row[1] == "WIN"


def test_close_trade_short_positive_pnl(tmp_trade_db):
    from engine.trade_log import TradeEntry, close_trade, record_trade

    tid = record_trade(TradeEntry(direction="SHORT", entry_price=5400.0))
    close_trade(tid, exit_price=5390.0, result="WIN")

    conn = duckdb.connect(tmp_trade_db)
    row = conn.execute("SELECT pnl_pts FROM trades WHERE id=?", [tid]).fetchone()
    conn.close()
    assert row[0] == 10.0


def test_close_trade_short_negative_pnl(tmp_trade_db):
    from engine.trade_log import TradeEntry, close_trade, record_trade

    tid = record_trade(TradeEntry(direction="SHORT", entry_price=5400.0))
    close_trade(tid, exit_price=5410.0, result="LOSS")

    conn = duckdb.connect(tmp_trade_db)
    row = conn.execute("SELECT pnl_pts FROM trades WHERE id=?", [tid]).fetchone()
    conn.close()
    assert row[0] == -10.0


def test_get_recent_trades(tmp_trade_db):
    from engine.trade_log import TradeEntry, get_recent_trades, record_trade

    for i in range(5):
        record_trade(TradeEntry(direction="LONG", entry_price=5400.0 + i))

    trades = get_recent_trades(limit=3)
    assert len(trades) == 3
    assert all("id" in t for t in trades)
    assert all("direction" in t for t in trades)


def test_get_win_rate_empty(tmp_trade_db):
    from engine.trade_log import get_win_rate

    stats = get_win_rate()
    assert stats["total"] == 0
    assert stats["win_rate"] == 0.0


def test_get_win_rate_with_trades(tmp_trade_db):
    from engine.trade_log import TradeEntry, close_trade, get_win_rate, record_trade

    t1 = record_trade(TradeEntry(direction="LONG", entry_price=5400.0))
    close_trade(t1, exit_price=5410.0, result="WIN")
    t2 = record_trade(TradeEntry(direction="LONG", entry_price=5400.0))
    close_trade(t2, exit_price=5390.0, result="LOSS")

    stats = get_win_rate()
    assert stats["total"] == 2
    assert stats["wins"] == 1
    assert stats["losses"] == 1
    assert stats["win_rate"] == 50.0


def test_trade_entry_defaults(tmp_trade_db):
    from engine.trade_log import TradeEntry, record_trade

    entry = TradeEntry(direction="LONG", entry_price=5400.0)
    assert entry.timeframe == "5m"
    assert entry.pattern_tags == []

    tid = record_trade(entry)
    conn = duckdb.connect(tmp_trade_db)
    row = conn.execute("SELECT timeframe, symbol FROM trades WHERE id=?", [tid]).fetchone()
    conn.close()
    assert row[0] == "5m"
    assert row[1] == "MES"
