from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import duckdb
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = REPO_ROOT / "scripts" / "duckdb_local" / "workspaces" / "anofox_research"
DEFAULT_CORE_EXPORT = (
    REPO_ROOT
    / "scripts"
    / "duckdb_local"
    / "workspaces"
    / "warbird_pro_core"
    / "exports"
    / "es_15m_core.csv"
)
DEFAULT_CORE_MANIFEST = DEFAULT_CORE_EXPORT.with_suffix(".manifest.json")
DEFAULT_DATASET_CSV = WORKSPACE / "anofox_es_15m_context.csv"
DEFAULT_DATASET_MANIFEST = WORKSPACE / "anofox_es_15m_context.manifest.json"
DEFAULT_STUDY_DB = WORKSPACE / "anofox_research.duckdb"

ALLOWED_MODELS = {"AutoTheta", "DynamicOptimizedTheta", "AutoARIMA", "Naive"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_safe(payload), indent=2, sort_keys=True) + "\n")


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def ensure_anofox(con: duckdb.DuckDBPyConnection, install: bool = True) -> dict[str, Any]:
    info: dict[str, Any] = {"extension": "anofox_forecast", "loaded": False}
    try:
        con.execute("LOAD anofox_forecast")
    except Exception as load_error:
        if not install:
            raise
        info["initial_load_error"] = str(load_error)
        con.execute("INSTALL anofox_forecast FROM community")
        con.execute("LOAD anofox_forecast")

    info["loaded"] = True
    try:
        rows = con.execute(
            """
            SELECT extension_name, loaded, installed, install_path
            FROM duckdb_extensions()
            WHERE extension_name = 'anofox_forecast'
            """
        ).fetchall()
        if rows:
            name, loaded, installed, install_path = rows[0]
            info.update(
                {
                    "extension_name": name,
                    "duckdb_loaded": bool(loaded),
                    "duckdb_installed": bool(installed),
                    "install_path": install_path,
                }
            )
    except Exception as status_error:
        info["status_error"] = str(status_error)
    return info


def parse_model_list(raw: str) -> list[str]:
    models = [item.strip() for item in raw.split(",") if item.strip()]
    invalid = sorted(set(models) - ALLOWED_MODELS)
    if invalid:
        raise ValueError(f"Unsupported AnoFox model(s): {invalid}. Allowed: {sorted(ALLOWED_MODELS)}")
    return models
