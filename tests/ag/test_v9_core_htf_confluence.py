import numpy as np
import pandas as pd

from scripts.duckdb_local.workspaces.warbird_pro_core import build_core_dataset as core


def test_direction_aware_htf_fib_price_mirrors_bearish_projection():
    htf_high = np.array([110.0, 110.0])
    htf_low = np.array([90.0, 90.0])
    htf_range = htf_high - htf_low
    fib_bull = np.array([True, False])

    projected = core.direction_aware_htf_fib_price(htf_high, htf_low, htf_range, core.FIB_382, fib_bull)

    assert np.allclose(projected, np.array([97.64, 102.36]))


def test_htf_confluence_uses_corresponding_directional_levels_for_shorts():
    ts = pd.date_range("2026-05-01 00:00:00+00:00", periods=6, freq="1h")
    df = pd.DataFrame(
        {
            "ts": ts,
            "open": np.full(len(ts), 100.0),
            "high": np.full(len(ts), 110.0),
            "low": np.full(len(ts), 90.0),
            "close": np.full(len(ts), 100.0),
            "volume": np.full(len(ts), 1.0),
        }
    )
    fib_range = np.full(len(ts), 20.0)
    fib_bull = np.full(len(ts), False)
    p_382 = np.full(len(ts), 102.36)
    p_pivot = np.full(len(ts), 100.0)
    p_618 = np.full(len(ts), 97.64)

    conf = core.htf_confluence(
        df,
        p_pivot,
        p_382,
        p_618,
        fib_range,
        fib_bull,
        htf_conf_tol_pct=0.01,
        htf_1h_lookback=2,
    )

    assert conf[-1] == 3.0
