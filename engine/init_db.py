"""Initialize ALL DuckDB tables (Groups 1-10, ~35 tables).

Creates data/warbird_trades.duckdb on first run with the exact schema
from the Chart Parity plan Section 4 inventory. Tables are created
empty and populated by their respective phases.

Usage:
    python engine/init_db.py
"""

from __future__ import annotations

import os
import sys

import duckdb

from engine.config import DATA_DIR, DUCKDB_PATH

# Schema for mes_1m (shared by all Group 1 bar tables)
_BAR_SCHEMA = (
    "ts TIMESTAMPTZ PRIMARY KEY, "
    "open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume BIGINT"
)

# Schema for econ domain tables (shared by all Group 4 domain tables)
_ECON_DOMAIN_SCHEMA = (
    "ts TIMESTAMPTZ, series_id TEXT, value DOUBLE, "
    "PRIMARY KEY(ts, series_id)"
)

# ---------------------------------------------------------------------------
# Group 1 — MES OHLCV Bars (7 tables)
# ---------------------------------------------------------------------------
GROUP_1_TABLES: dict[str, str] = {
    "mes_1m": _BAR_SCHEMA,
    "mes_3m": _BAR_SCHEMA,
    "mes_5m": _BAR_SCHEMA,
    "mes_15m": _BAR_SCHEMA,
    "mes_1h": _BAR_SCHEMA,
    "mes_4h": _BAR_SCHEMA,
    "mes_1d": _BAR_SCHEMA,
}

# ---------------------------------------------------------------------------
# Group 2 — Trades-Side Volume (2 tables)
# ---------------------------------------------------------------------------
GROUP_2_TABLES: dict[str, str] = {
    "trades_raw": (
        "ts TIMESTAMPTZ, price DOUBLE, size INTEGER, "
        "side TEXT CHECK(side IN ('B','A','N'))"
    ),
    "trades_volume": (
        "ts TIMESTAMPTZ, "
        "timeframe TEXT CHECK(timeframe IN ('1m','3m','5m','15m')), "
        "buy_vol BIGINT, sell_vol BIGINT, unknown_vol BIGINT, "
        "delta BIGINT, total_vol BIGINT, "
        "confidence TEXT CHECK(confidence IN ('HIGH','LOW')), "
        "PRIMARY KEY(ts, timeframe)"
    ),
}

# ---------------------------------------------------------------------------
# Group 3 — Correlations (1 table)
# ---------------------------------------------------------------------------
GROUP_3_TABLES: dict[str, str] = {
    "cross_asset_1h": (
        "ts TIMESTAMPTZ, symbol_code TEXT, "
        "open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume BIGINT, "
        "PRIMARY KEY(ts, symbol_code)"
    ),
}

# ---------------------------------------------------------------------------
# Group 4 — FRED/Economic Data (11 tables)
# ---------------------------------------------------------------------------
GROUP_4_TABLES: dict[str, str] = {
    "series_catalog": (
        "series_id TEXT PRIMARY KEY, name TEXT, category TEXT, "
        "frequency TEXT, is_active BOOLEAN"
    ),
    "econ_rates_1d": _ECON_DOMAIN_SCHEMA,
    "econ_yields_1d": _ECON_DOMAIN_SCHEMA,
    "econ_fx_1d": _ECON_DOMAIN_SCHEMA,
    "econ_vol_1d": _ECON_DOMAIN_SCHEMA,
    "econ_inflation_1d": _ECON_DOMAIN_SCHEMA,
    "econ_labor_1d": _ECON_DOMAIN_SCHEMA,
    "econ_activity_1d": _ECON_DOMAIN_SCHEMA,
    "econ_money_1d": _ECON_DOMAIN_SCHEMA,
    "econ_commodities_1d": _ECON_DOMAIN_SCHEMA,
    "econ_indexes_1d": _ECON_DOMAIN_SCHEMA,
}

# ---------------------------------------------------------------------------
# Group 5 — News & Events (8 tables)
# ---------------------------------------------------------------------------
GROUP_5_TABLES: dict[str, str] = {
    "econ_news_topics": (
        "topic_code TEXT PRIMARY KEY, topic_label TEXT, topic_family TEXT, "
        "econ_category TEXT, topic_tags TEXT[], description TEXT, is_active BOOLEAN"
    ),
    "news_articles": (
        "id INTEGER PRIMARY KEY, provider TEXT, article_key TEXT UNIQUE, "
        "title TEXT, summary TEXT, url TEXT, publisher_domain TEXT, "
        "published_at TIMESTAMPTZ, published_minute TIMESTAMPTZ, "
        "normalized_title TEXT, dedupe_key TEXT UNIQUE, "
        "body_word_count INTEGER DEFAULT 0, related_symbols TEXT[], "
        "topic_codes TEXT[], benchmark_fit_score DOUBLE, "
        "fetched_at TIMESTAMPTZ DEFAULT now()"
    ),
    "news_article_segments": (
        "id INTEGER PRIMARY KEY, article_id INTEGER, "
        "segment TEXT, matched_keywords TEXT[], matched_symbols TEXT[]"
    ),
    "news_article_assessments": (
        "id INTEGER PRIMARY KEY, provider TEXT, dedupe_key TEXT, "
        "article_key TEXT, topic_code TEXT, source_quality_score DOUBLE, "
        "market_relevance_score DOUBLE, macro_specificity_score DOUBLE, "
        "technical_specificity_score DOUBLE, cross_asset_context_score DOUBLE, "
        "watchlist_relevance_score DOUBLE, reasoning_confidence DOUBLE, "
        "benchmark_fit_score DOUBLE, "
        "scoring_version TEXT DEFAULT 'reuters_benchmark_v1', "
        "scored_at TIMESTAMPTZ DEFAULT now()"
    ),
    "econ_calendar": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, event_name TEXT, "
        "actual DOUBLE, forecast DOUBLE, previous DOUBLE, "
        "impact TEXT, currency TEXT"
    ),
    "news_signals": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, signal_type TEXT, "
        "direction TEXT, confidence DOUBLE, source_headline TEXT"
    ),
    "geopolitical_risk_1d": (
        "ts TIMESTAMPTZ PRIMARY KEY, gpr_daily DOUBLE, gpr_threats DOUBLE, "
        "gpr_acts DOUBLE, country TEXT"
    ),
    "trump_effect_1d": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, event_type TEXT, "
        "title TEXT, summary TEXT, market_impact TEXT, "
        "sector TEXT, source TEXT, source_url TEXT"
    ),
}

# ---------------------------------------------------------------------------
# Group 6 — Trade Log (3 tables)
# ---------------------------------------------------------------------------
GROUP_6_TABLES: dict[str, str] = {
    "trades": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, symbol TEXT DEFAULT 'MES', "
        "direction TEXT, entry_price DOUBLE, stop_loss DOUBLE, "
        "tp1 DOUBLE, tp2 DOUBLE, exit_price DOUBLE, exit_reason TEXT, "
        "pnl DOUBLE, status TEXT"
    ),
    "trade_tags": (
        "id INTEGER PRIMARY KEY, trade_id INTEGER, tag TEXT"
    ),
    "indicator_state": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, timeframe TEXT, state_json TEXT"
    ),
}

# ---------------------------------------------------------------------------
# Group 7 — Symbols Registry (1 table)
# ---------------------------------------------------------------------------
GROUP_7_TABLES: dict[str, str] = {
    "symbols": (
        "code TEXT PRIMARY KEY, display_name TEXT, short_name TEXT, "
        "description TEXT, tick_size DOUBLE, data_source TEXT, "
        "dataset TEXT, databento_symbol TEXT, is_active BOOLEAN"
    ),
}

# ---------------------------------------------------------------------------
# Group 8 — Volatility State (1 table)
# ---------------------------------------------------------------------------
GROUP_8_TABLES: dict[str, str] = {
    "vol_states": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, state_name TEXT, "
        "regime_label TEXT, days_into_regime INTEGER, "
        "vix_level DOUBLE, vix_percentile_20d DOUBLE"
    ),
}

# ---------------------------------------------------------------------------
# Group 9 — Warbird Signal Chain (8 tables)
# ---------------------------------------------------------------------------
GROUP_9_TABLES: dict[str, str] = {
    "warbird_daily_bias": (
        "ts TIMESTAMPTZ PRIMARY KEY, symbol_code TEXT DEFAULT 'MES', "
        "bias TEXT CHECK(bias IN ('BULL','BEAR','NEUTRAL')), "
        "close_price DOUBLE, ma_200 DOUBLE, price_vs_200d_ma DOUBLE, "
        "distance_pct DOUBLE, slope_200d_ma DOUBLE, sessions_on_side INTEGER, "
        "daily_return DOUBLE, daily_range_vs_avg DOUBLE"
    ),
    "warbird_structure_4h": (
        "ts TIMESTAMPTZ PRIMARY KEY, symbol_code TEXT DEFAULT 'MES', "
        "bias_4h TEXT CHECK(bias_4h IN ('BULL','BEAR','NEUTRAL')), "
        "agrees_with_daily BOOLEAN DEFAULT FALSE, trend_score DOUBLE, "
        "swing_high DOUBLE, swing_low DOUBLE, structural_note TEXT"
    ),
    "warbird_forecasts_1h": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, "
        "symbol_code TEXT DEFAULT 'MES', bias_1h TEXT, "
        "target_price_1h DOUBLE, target_price_4h DOUBLE, "
        "confidence DOUBLE, current_price DOUBLE, "
        "model_version TEXT, feature_snapshot TEXT"
    ),
    "warbird_triggers_15m": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, forecast_id INTEGER, "
        "symbol_code TEXT DEFAULT 'MES', direction TEXT, "
        "decision TEXT CHECK(decision IN ('GO','WAIT','NO_GO')), "
        "fib_level DOUBLE, entry_price DOUBLE, stop_loss DOUBLE, "
        "tp1 DOUBLE, tp2 DOUBLE, "
        "volume_confirmation BOOLEAN DEFAULT FALSE, volume_ratio DOUBLE, "
        "no_trade_reason TEXT"
    ),
    "warbird_conviction": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, "
        "forecast_id INTEGER, trigger_id INTEGER, "
        "symbol_code TEXT DEFAULT 'MES', "
        "level TEXT CHECK(level IN "
        "('MAXIMUM','HIGH','MODERATE','LOW','NO_TRADE')), "
        "counter_trend BOOLEAN DEFAULT FALSE, "
        "all_layers_agree BOOLEAN DEFAULT FALSE, "
        "runner_eligible BOOLEAN DEFAULT FALSE, "
        "daily_bias TEXT, bias_4h TEXT, bias_1h TEXT, trigger_decision TEXT"
    ),
    "warbird_setups": (
        "id INTEGER PRIMARY KEY, setup_key TEXT UNIQUE, ts TIMESTAMPTZ, "
        "symbol_code TEXT DEFAULT 'MES', "
        "forecast_id INTEGER, trigger_id INTEGER, conviction_id INTEGER, "
        "direction TEXT, "
        "status TEXT CHECK(status IN "
        "('ACTIVE','TP1_HIT','TP2_HIT','RUNNER_ACTIVE','RUNNER_EXITED','STOPPED','EXPIRED')), "
        "conviction_level TEXT, entry_price DOUBLE, stop_loss DOUBLE, "
        "tp1 DOUBLE, tp2 DOUBLE, "
        "volume_confirmation BOOLEAN DEFAULT FALSE, "
        "trigger_bar_ts TIMESTAMPTZ, tp1_hit_at TIMESTAMPTZ, "
        "tp2_hit_at TIMESTAMPTZ, stopped_at TIMESTAMPTZ, "
        "expires_at TIMESTAMPTZ, notes TEXT"
    ),
    "warbird_setup_events": (
        "id INTEGER PRIMARY KEY, setup_id INTEGER, ts TIMESTAMPTZ, "
        "event_type TEXT CHECK(event_type IN "
        "('TRIGGERED','TP1_HIT','TP2_HIT','RUNNER_STARTED','RUNNER_EXITED','STOPPED','EXPIRED')), "
        "price DOUBLE, note TEXT, metadata TEXT"
    ),
    "warbird_risk": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, "
        "forecast_id INTEGER, symbol_code TEXT DEFAULT 'MES', "
        "garch_sigma DOUBLE, garch_vol_ratio DOUBLE, "
        "zone_1_upper DOUBLE, zone_1_lower DOUBLE, "
        "zone_2_upper DOUBLE, zone_2_lower DOUBLE, "
        "gpr_level DOUBLE, trump_effect_active BOOLEAN, "
        "vix_level DOUBLE, vix_percentile_20d DOUBLE, "
        "vol_state_name TEXT, regime_label TEXT DEFAULT 'trump_2', "
        "days_into_regime INTEGER"
    ),
}

# ---------------------------------------------------------------------------
# Group 10 — AI Analysis Output (1 table)
# ---------------------------------------------------------------------------
GROUP_10_TABLES: dict[str, str] = {
    "ai_analysis_log": (
        "id INTEGER PRIMARY KEY, ts TIMESTAMPTZ, model TEXT, "
        "analysis_text TEXT, data_sources_used TEXT, "
        "screenshot_available BOOLEAN DEFAULT FALSE"
    ),
}

# ---------------------------------------------------------------------------
# All groups combined
# ---------------------------------------------------------------------------
ALL_GROUPS: list[tuple[str, dict[str, str]]] = [
    ("Group 1: MES OHLCV Bars", GROUP_1_TABLES),
    ("Group 2: Trades-Side Volume", GROUP_2_TABLES),
    ("Group 3: Correlations", GROUP_3_TABLES),
    ("Group 4: FRED/Economic Data", GROUP_4_TABLES),
    ("Group 5: News & Events", GROUP_5_TABLES),
    ("Group 6: Trade Log", GROUP_6_TABLES),
    ("Group 7: Symbols Registry", GROUP_7_TABLES),
    ("Group 8: Volatility State", GROUP_8_TABLES),
    ("Group 9: Warbird Signal Chain", GROUP_9_TABLES),
    ("Group 10: AI Analysis Output", GROUP_10_TABLES),
]


def init_all_tables(db_path: str | None = None) -> list[str]:
    """Create all DuckDB tables. Returns list of created table names."""
    if db_path is None:
        db_path = DUCKDB_PATH

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)

    created: list[str] = []
    for group_name, tables in ALL_GROUPS:
        for table_name, schema in tables.items():
            conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
            created.append(table_name)

    conn.close()
    return created


def main() -> None:
    """CLI entry point — initialize DuckDB and print summary."""
    init_all_tables()

    conn = duckdb.connect(DUCKDB_PATH)
    actual = conn.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main' ORDER BY table_name"
    ).fetchall()
    conn.close()

    print(f"DuckDB initialized at: {DUCKDB_PATH}")
    print(f"Tables created: {len(actual)}")
    print()
    for group_name, group_tables in ALL_GROUPS:
        print(f"  {group_name} ({len(group_tables)} tables):")
        for t in group_tables:
            marker = "  [ok]" if any(r[0] == t for r in actual) else "  [MISSING]"
            print(f"    {marker} {t}")
    print()
    print(f"Total: {len(actual)} tables across {len(ALL_GROUPS)} groups")


if __name__ == "__main__":
    main()
