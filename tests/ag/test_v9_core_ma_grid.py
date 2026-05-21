from scripts.duckdb_local.workspaces.warbird_pro_core import build_core_dataset as core


def test_ma_grid_matches_user_contract():
    assert core.MA_FAST_BASE == 21
    assert core.MA_SLOW_BASE == 9
    assert core.MA_FAST_GRID == tuple(range(11, 32))
    assert core.MA_SLOW_GRID == tuple(range(4, 15))


def test_ma_grid_profiles_cover_base_and_configured_perturbations():
    profiles = core.generate_indicator_profiles("ma-grid")
    pairs = {(p["knob_length_ema"], p["knob_length_ma"]) for p in profiles}

    assert (21, 9) in pairs
    assert {p["knob_length_ema"] for p in profiles} == set(range(11, 32))
    assert {p["knob_length_ma"] for p in profiles} == set(range(4, 15))

    ema_non_base = {p["knob_length_ema"] for p in profiles if p["knob_length_ema"] != 21}
    sma_non_base = {p["knob_length_ma"] for p in profiles if p["knob_length_ma"] != 9}
    assert len(ema_non_base) == 20
    assert len(sma_non_base) == 10
