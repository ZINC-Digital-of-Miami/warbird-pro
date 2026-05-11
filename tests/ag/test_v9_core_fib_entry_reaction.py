import numpy as np

from scripts.optuna.workspaces.warbird_pro_core import build_core_dataset as core


def test_fib_touch_priority_prefers_786_then_618_then_500_for_long_reaction():
    open_ = np.array([101.0, 101.0])
    high = np.array([102.0, 102.0])
    low = np.array([100.5, 78.0])
    close = np.array([101.0, 80.5])
    atr = np.array([10.0, 10.0])
    direction = np.array([1, 1])
    p500 = np.array([50.0, 50.0])
    p618 = np.array([61.8, 61.8])
    p786 = np.array([78.6, 78.6])

    reaction = core.compute_fib_entry_reaction_features(
        open_=open_,
        high=high,
        low=low,
        close=close,
        atr=atr,
        direction=direction,
        p_pivot=p500,
        p_618=p618,
        p_786=p786,
    )

    assert reaction["fib_touch_level_code"].tolist() == [0.0, 786.0]
    assert reaction["touched786_long"].tolist() == [False, True]
    assert reaction["selected_entry_level"].tolist()[1] == 78.6
    assert reaction["fib_pierce_atr"].tolist()[1] > 0
    assert reaction["fib_close_reclaim_atr"].tolist()[1] > 0


def test_fib_touch_priority_prefers_786_then_618_then_500_for_short_reaction():
    open_ = np.array([99.0, 99.0])
    high = np.array([99.5, 122.0])
    low = np.array([98.0, 98.0])
    close = np.array([99.0, 119.5])
    atr = np.array([10.0, 10.0])
    direction = np.array([-1, -1])
    p500 = np.array([150.0, 150.0])
    p618 = np.array([138.2, 138.2])
    p786 = np.array([121.4, 121.4])

    reaction = core.compute_fib_entry_reaction_features(
        open_=open_,
        high=high,
        low=low,
        close=close,
        atr=atr,
        direction=direction,
        p_pivot=p500,
        p_618=p618,
        p_786=p786,
    )

    assert reaction["fib_touch_level_code"].tolist() == [0.0, 786.0]
    assert reaction["touched786_short"].tolist() == [False, True]
    assert reaction["selected_entry_level"].tolist()[1] == 121.4
    assert reaction["fib_pierce_atr"].tolist()[1] > 0
    assert reaction["fib_close_reclaim_atr"].tolist()[1] > 0
