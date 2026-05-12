import numpy as np

from scripts.duckdb_local.workspaces.warbird_pro_core import build_core_dataset as core


def test_liquidity_state_matches_pine_sweep_and_reclaim_semantics():
    high = np.array([10.0, 11.0, 12.0, 10.5, 13.0, 11.0])
    low = np.array([9.0, 10.0, 8.0, 9.2, 9.0, 9.5])
    close = np.array([9.5, 10.5, 11.5, 9.8, 11.5, 10.5])

    state = core.compute_liquidity_state(
        high=high,
        low=low,
        close=close,
        lookback_bars=2,
        recency_bars=3,
    )

    assert state["swept_ssl"].tolist() == [False, False, True, False, False, False]
    assert state["reclaimed_ssl"].tolist() == [False, False, False, True, False, False]
    assert state["swept_bsl"].tolist() == [False, False, False, False, True, False]
    assert state["reclaimed_bsl"].tolist() == [False, False, False, False, False, True]
    assert state["recent_liq_bull"].tolist() == [False, False, True, True, True, True]
    assert state["recent_liq_bear"].tolist() == [False, False, False, False, True, True]
