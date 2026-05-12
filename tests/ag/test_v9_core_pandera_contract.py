from __future__ import annotations

import json

import pytest
from pandera.config import ValidationDepth, config_context

from scripts.duckdb_local.workspaces.warbird_pro_core import build_core_dataset as core


def test_core_builder_workspace_points_to_duckdb_local() -> None:
    assert core.WORKSPACE == core.REPO_ROOT / "scripts" / "duckdb_local" / "workspaces" / "warbird_pro_core"
    assert "scripts/optuna" not in str(core.EXPORTS_DIR)


def _valid_manifest() -> dict[str, object]:
    return {
        "repo_commit": "abc123",
        "symbol": "ES",
        "symbol_root": "ES",
        "timeframe": "15",
        "trigger_family": core.TRIGGER_FAMILY,
        "source_kind": "DATABENTO_ES_CORE_ETL",
        "source_bars": "data/es_1m.parquet",
        "label_column": core.LABEL_COL,
        "feature_count_locked": len(core.ML_FEATURES),
        "row_count": 1,
        "entry_long_count": 0,
        "entry_short_count": 0,
        "profiling_report_path": "es_15m_core.profile.html",
        "profiling_rows_profiled": 1,
    }


def test_manifest_contract_forces_pandera_validation_enabled() -> None:
    manifest = _valid_manifest()
    manifest["source_kind"] = "TRADINGVIEW_INDICATOR_CSV"

    with config_context(validation_enabled=False):
        with pytest.raises(Exception):
            core.validate_manifest_contract(manifest)


def test_manifest_contract_forces_schema_and_data_validation_depth() -> None:
    manifest = _valid_manifest()
    manifest["source_kind"] = "TRADINGVIEW_INDICATOR_CSV"

    with config_context(validation_depth=ValidationDepth.SCHEMA_ONLY):
        with pytest.raises(Exception):
            core.validate_manifest_contract(manifest)


def test_manifest_contract_rejects_optuna_lineage() -> None:
    manifest = _valid_manifest()
    manifest["profiling_report_path"] = "/repo/scripts/optuna/workspaces/warbird_pro_core/profile.html"

    with pytest.raises(RuntimeError, match="forbidden lineage tokens"):
        core.validate_manifest_contract(manifest)


def test_committed_core_manifest_profile_path_is_duckdb_local() -> None:
    manifest_path = core.EXPORTS_DIR / "es_15m_core.manifest.json"
    manifest = json.loads(manifest_path.read_text())
    profile_path = manifest["profiling_report_path"]

    assert "scripts/optuna" not in profile_path
    assert "scripts/duckdb_local" in profile_path
    assert core.Path(profile_path).exists()
