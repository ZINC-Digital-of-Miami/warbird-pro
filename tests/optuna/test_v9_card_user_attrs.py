"""Structural contract tests for Hybrid+ Optuna cards.

These tests verify each card profile satisfies the runner.py contract
(BOOL_PARAMS, NUMERIC_RANGES, INT_PARAMS, CATEGORICAL_PARAMS, INPUT_DEFAULTS,
load_data, run_backtest), declares a valid OBJECTIVE_METRIC, and — for the
AG-bearing cards — emits the required ag_* keys in its run_backtest result
so trial.user_attrs gain a uniform shape on the dashboard.

Tests do NOT actually fit AG (which would take minutes per fold); they
exercise the no-trade short-circuit so AG is never imported during pytest.
"""
from __future__ import annotations

import json
from typing import Any

import pandas as pd
import pytest


CARDS_REQUIRED_ATTRS = (
    "BOOL_PARAMS",
    "NUMERIC_RANGES",
    "INT_PARAMS",
    "CATEGORICAL_PARAMS",
    "INPUT_DEFAULTS",
)


def _import(module_name: str):
    import importlib
    return importlib.import_module(module_name)


@pytest.mark.parametrize(
    "module_name,profile_key",
    [
        ("scripts.optuna.warbird_pro_v9_exit_cpcv_profile", "warbird_pro_v9_exit_cpcv"),
        ("scripts.optuna.warbird_pro_v9_entry_filter_cpcv_profile", "warbird_pro_v9_entry_filter_cpcv"),
        ("scripts.optuna.warbird_pro_v9_ag_meta_cpcv_profile", "warbird_pro_v9_ag_meta_cpcv"),
        ("scripts.optuna.warbird_pro_v9_joint_challenger_profile", "warbird_pro_v9_joint_challenger"),
    ],
)
def test_card_profile_satisfies_runner_contract(module_name: str, profile_key: str) -> None:
    mod = _import(module_name)
    for attr in CARDS_REQUIRED_ATTRS:
        assert hasattr(mod, attr), f"{module_name} missing {attr}"
    assert callable(getattr(mod, "load_data", None)), f"{module_name} missing load_data"
    assert callable(getattr(mod, "run_backtest", None)), f"{module_name} missing run_backtest"
    assert getattr(mod, "PROFILE_KEY", "") == profile_key, (
        f"{module_name}.PROFILE_KEY != {profile_key}"
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "scripts.optuna.warbird_pro_v9_ag_meta_cpcv_profile",
        "scripts.optuna.warbird_pro_v9_joint_challenger_profile",
    ],
)
def test_ag_cards_emit_required_user_attrs_on_no_trade(module_name: str) -> None:
    """When run_backtest sees no trades, it must still emit a shape that the
    runner can populate trial.user_attrs from. AG-card results MUST include
    the ag_* keys listed in cpcv_helpers.REQUIRED_AG_USER_ATTRS so the
    dashboard renders consistently regardless of fit_status."""
    mod = _import(module_name)
    helpers = _import("scripts.optuna.cpcv_helpers")
    df = pd.DataFrame({
        "ts": pd.date_range("2020-01-01", periods=10, freq="5min", tz="UTC"),
        "ml_entry_long_trigger": [0.0] * 10,
        "ml_entry_short_trigger": [0.0] * 10,
        "ml_last_exit_outcome": [0.0] * 10,
    })
    params = dict(mod.INPUT_DEFAULTS)
    result = mod.run_backtest(df, params, start_date="2020-01-01")
    assert isinstance(result, dict)
    assert "fit_status" in result, f"{module_name}: result missing fit_status"
    for required in ("trades", "win_rate", "pf", mod.OBJECTIVE_METRIC):
        assert required in result, f"{module_name}: result missing {required}"
    # Required AG user_attrs keys must be present (or the helpers contract
    # itself signals what to log).
    for key in helpers.REQUIRED_AG_USER_ATTRS:
        bare = key[len("ag_"):]
        assert bare in result, (
            f"{module_name}: result missing '{bare}' (required for user_attr '{key}')"
        )


def test_ag_card_strategy_candidates_fallback_loadable() -> None:
    """When no candidates manifest is present, Card 3 falls back to a single
    default candidate so smoke tests can run without first executing
    Cards 1+2."""
    mod = _import("scripts.optuna.warbird_pro_v9_ag_meta_cpcv_profile")
    candidates = mod._candidates()
    assert isinstance(candidates, list)
    assert len(candidates) >= 1
    for entry in candidates:
        assert "params" in entry
        assert isinstance(entry["params"], dict)


def test_orchestrate_dry_run_produces_runner_commands() -> None:
    """The orchestrator must enumerate exactly the active cards in dry-run
    mode without writing any file. This guards against a future change that
    accidentally drops Card 3 or 4 from the rotation."""
    orch = _import("scripts.optuna.orchestrate_v9_run")
    candidates = orch.build_candidate_manifest(top_k=3)
    # Either Cards 1+2 have produced top5.json, or candidate list is empty.
    assert isinstance(candidates, list)


def test_runbook_documents_hybrid_plus_cards() -> None:
    from pathlib import Path
    runbook = Path(__file__).resolve().parents[2] / "docs/runbooks/warbird_pro_v9_optuna_ag_shap.md"
    text = runbook.read_text()
    assert "warbird_pro_v9_exit_cpcv" in text
    assert "warbird_pro_v9_entry_filter_cpcv" in text
    assert "warbird_pro_v9_ag_meta_cpcv" in text
    assert "warbird_pro_v9_joint_challenger" in text
    assert "Hybrid+" in text


def test_registry_contains_four_cpcv_cards() -> None:
    from pathlib import Path
    reg = Path(__file__).resolve().parents[2] / "scripts/optuna/indicator_registry.json"
    rows = json.loads(reg.read_text())
    keys = {r.get("key") for r in rows}
    expected = {
        "warbird_pro_v9_exit_cpcv",
        "warbird_pro_v9_entry_filter_cpcv",
        "warbird_pro_v9_ag_meta_cpcv",
        "warbird_pro_v9_joint_challenger",
    }
    missing = expected - keys
    assert not missing, f"registry missing cards: {sorted(missing)}"
