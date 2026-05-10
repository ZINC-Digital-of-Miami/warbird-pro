#!/usr/bin/env python3
"""Warbird Pro V9 Core AutoGluon Optuna card.

This card is the operator-facing Optuna wrapper for the V9 Core lane. It can
record a cheap smoke/validation trial into `warbird_pro_core/study.db` so the
hub has a real dashboard card before the full 1y AutoGluon run is approved.

Full training still belongs behind the explicit Core gate. The default mode is
therefore `smoke`, which validates the existing smoke CSV and writes one Optuna
trial with schema/label metrics. It does not fit AutoGluon.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Any

import optuna
import pandas as pd
from optuna.exceptions import ExperimentalWarning as OptunaExperimentalWarning

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.ag.report_v9_core_smoke import build_report
from scripts.ag.train_v9_locked import LABEL_COL
from scripts.optuna.paths import study_db_path, workspace_dir

CARD_KEY = "warbird_pro_core"
CARD_TITLE = "2026-05-09 - Warbird Pro Autogluon Core"
PROFILE_MODULE = "scripts.optuna.cards.core_training.2026_05_09_warbird_pro_autogluon_core"
OBJECTIVE_METRIC = "core_validation_gate_score"

WORKSPACE = workspace_dir(CARD_KEY)
STUDY_DB = study_db_path(CARD_KEY)
DEFAULT_CSV = REPO_ROOT / "artifacts" / "v9_core_smoke_may2025" / "mes_5m_core.csv"
DEFAULT_MANIFEST = DEFAULT_CSV.with_name("mes_5m_core.manifest.json")

# Runner-compatible adapter surface. The Core card is not an HPO search space;
# direct CLI execution below is the preferred path.
BOOL_PARAMS: list[str] = []
NUMERIC_RANGES: dict[str, tuple[float, float]] = {}
INT_PARAMS: set[str] = set()
CATEGORICAL_PARAMS: dict[str, list[Any]] = {}
INPUT_DEFAULTS: dict[str, Any] = {}


def _storage_url(db_path: Path) -> str:
    return f"sqlite:///{db_path}"


def _ensure_inputs(csv_path: Path, manifest_path: Path) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Core CSV not found: {csv_path}. Build it first with "
            "scripts/optuna/workspaces/warbird_pro_core/build_core_dataset.py."
        )
    if not manifest_path.exists():
        raise FileNotFoundError(f"Core manifest not found: {manifest_path}")


def validation_result(csv_path: Path, manifest_path: Path, max_hold_bars: int) -> dict[str, Any]:
    _ensure_inputs(csv_path, manifest_path)
    report = build_report(csv_path, manifest_path, max_hold_bars=max_hold_bars)
    label_counts = report.get("label_counts", {})
    if str(0) not in label_counts or str(1) not in label_counts:
        raise RuntimeError(f"{LABEL_COL} smoke validation requires both classes; got {label_counts}")
    return report


def _trial_attrs(report: dict[str, Any], mode: str) -> dict[str, Any]:
    nonzero_counts = report.get("nonzero_counts", {})
    return {
        "card_key": CARD_KEY,
        "card_title": CARD_TITLE,
        "mode": mode,
        "fit_status": "validated_not_trained",
        "objective_metric": OBJECTIVE_METRIC,
        "objective_score": 1.0,
        "label": LABEL_COL,
        "row_count": int(report["row_count"]),
        "trades": int(report["resolved_trade_count"]),
        "win_rate": float(report["winner_rate"]),
        "winner_count": int(report["winner_count"]),
        "loss_count": int(report["loss_count"]),
        "entry_long_count": int(report["entry_long_count"]),
        "entry_short_count": int(report["entry_short_count"]),
        "feature_count_locked": int(report["feature_count_locked"]),
        "csv_sha256": str(report["csv_sha256"]),
        "manifest_sha256": str(report["manifest_sha256"]),
        "manifest_sha256_matches_csv": bool(report["manifest_sha256_matches_csv"]),
        "ts_first": str(report["ts_first"]),
        "ts_last": str(report["ts_last"]),
        "ml_xa_dxy_code_nonzero": int(nonzero_counts.get("ml_xa_dxy_code", 0)),
        "ml_xa_dxy_diverge_nonzero": int(nonzero_counts.get("ml_xa_dxy_diverge", 0)),
        "ml_fp_delta_pct_nonzero": int(nonzero_counts.get("ml_fp_delta_pct", 0)),
        "ml_cvd_div_bull_nonzero": int(nonzero_counts.get("ml_cvd_div_bull", 0)),
        "ml_cvd_div_bear_nonzero": int(nonzero_counts.get("ml_cvd_div_bear", 0)),
        "ml_absorption_candidate_nonzero": int(nonzero_counts.get("ml_absorption_candidate", 0)),
        "ml_flush_candidate_nonzero": int(nonzero_counts.get("ml_flush_candidate", 0)),
    }


def write_optuna_trial(
    report: dict[str, Any],
    *,
    db_path: Path,
    study_name: str,
    mode: str,
) -> int:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    study = optuna.create_study(
        study_name=study_name,
        storage=_storage_url(db_path),
        direction="maximize",
        load_if_exists=True,
    )
    if hasattr(study, "set_metric_names"):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", OptunaExperimentalWarning)
            try:
                study.set_metric_names([OBJECTIVE_METRIC])
            except Exception:
                pass

    study.set_user_attr("project", "warbird-pro")
    study.set_user_attr("card_key", CARD_KEY)
    study.set_user_attr("card_title", CARD_TITLE)
    study.set_user_attr("profile_module", PROFILE_MODULE)
    study.set_user_attr("label", LABEL_COL)
    study.set_user_attr("training_status", "not_started")
    study.set_user_attr("gate_status", "smoke_validated" if mode == "smoke" else "validated")

    trial = study.ask()
    for key, value in _trial_attrs(report, mode).items():
        trial.set_user_attr(key, value)
    study.tell(trial, 1.0)
    return int(trial.number)


def load_data() -> pd.DataFrame:
    _ensure_inputs(DEFAULT_CSV, DEFAULT_MANIFEST)
    return pd.read_csv(DEFAULT_CSV, parse_dates=["ts"])


def run_backtest(df: pd.DataFrame, params: dict[str, Any], start_date: str) -> dict[str, Any]:
    _ = (df, params, start_date)
    report = validation_result(DEFAULT_CSV, DEFAULT_MANIFEST, max_hold_bars=24)
    return {
        "trades": int(report["resolved_trade_count"]),
        "win_rate": float(report["winner_rate"]),
        "pf": 0.0,
        "max_dd_abs": 0.0,
        "gross_profit": float(report["winner_count"]),
        "gross_loss": float(report["loss_count"]),
        "objective_score": 1.0,
        "quality_events": int(report["resolved_trade_count"]),
        "fit_status": "validated_not_trained",
        "row_count": int(report["row_count"]),
        "entry_long_count": int(report["entry_long_count"]),
        "entry_short_count": int(report["entry_short_count"]),
    }


def objective_score(result: dict[str, Any]) -> float:
    return float(result.get("objective_score", 0.0))


def get_card_manifest() -> dict[str, Any]:
    return {
        "key": CARD_KEY,
        "title": CARD_TITLE,
        "profile_module": PROFILE_MODULE,
        "study_db": str(STUDY_DB),
        "default_csv": str(DEFAULT_CSV),
        "status": "smoke_wrapper_wired",
        "trains_autogluon": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=CARD_TITLE)
    ap.add_argument("--mode", choices=["smoke", "validate-only"], default="smoke")
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--study-db", type=Path, default=STUDY_DB)
    ap.add_argument("--study-name", default=CARD_TITLE)
    ap.add_argument("--max-hold-bars", type=int, default=24)
    ap.add_argument("--out-json", type=Path, default=None)
    args = ap.parse_args()

    report = validation_result(args.csv, args.manifest, args.max_hold_bars)
    trial_no = write_optuna_trial(
        report,
        db_path=args.study_db,
        study_name=args.study_name,
        mode=args.mode,
    )

    payload = {
        "card": get_card_manifest(),
        "mode": args.mode,
        "study_name": args.study_name,
        "study_db": str(args.study_db),
        "trial_number": trial_no,
        "report": report,
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
