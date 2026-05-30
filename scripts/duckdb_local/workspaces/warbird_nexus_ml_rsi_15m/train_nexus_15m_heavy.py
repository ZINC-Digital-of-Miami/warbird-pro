#!/usr/bin/env python3
"""Train the isolated Nexus 15m heavy model from audited Pine footprint exports.

This is a Nexus-only trainer. It reads the manifest-backed dataset emitted by
``build_nexus_15m_dataset.py`` from TradingView/Pine `request.footprint()`
evidence columns and fits the first sequential target:
``label_volume_expansion_next_12b``. It does not import, modify, or write any
Warbird V9 Pine, V9 trainer, V9 export, V9 model, or V9 fib surface.
"""
from __future__ import annotations

import os

# Apple Silicon / local full-zoo guards. These must be set before AutoGluon import.
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["LIGHTGBM_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import argparse
import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import re

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, log_loss, roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

WORKSPACE = REPO_ROOT / "scripts" / "duckdb_local" / "workspaces" / "warbird_nexus_ml_rsi_15m"
DEFAULT_MANIFEST = WORKSPACE / "exports" / "nexus_15m_dataset.manifest.json"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "models" / "warbird_nexus_ml_rsi_15m"
DEFAULT_REPORTS_DIR = WORKSPACE / "reports"
TRIGGER_FAMILY = "NEXUS_FOOTPRINT_DELTA"
CAPTURE_METHOD = "TV_NEXUS_15M_CHART_EXPORT"
PRIMARY_TARGET = "label_volume_expansion_next_12b"
PROBLEM_TYPE = "binary"
EVAL_METRIC = "log_loss"
REQUIRED_SPLITS = ("train", "validation", "test")
FORBIDDEN_REFERENCES = ("train_" + "v9_locked", "warbird_" + "pro_v9", "winner_tp_" + "before_sl")

# Research-heavy defaults. The first run used V9's time-series-safe no-bagging
# profile and completed quickly because the Nexus dataset is small. Nexus can
# now use AutoGluon bagged/stacked models as variance-reduction inside the
# historical train segment, but proof still comes only from the chronological
# validation/test segments. Internal k-fold scores are never accepted as OOS
# evidence for Pine/settings decisions.
DEFAULT_TIME_LIMIT_SEC = 14_400
DEFAULT_HPO_TRIALS = 80
DEFAULT_NUM_BAG_FOLDS = 5
DEFAULT_NUM_BAG_SETS = 2
DEFAULT_NUM_STACK_LEVELS = 1
DEFAULT_DYNAMIC_STACKING = "auto"
DEFAULT_FEATURE_IMPORTANCE_SHUFFLES = 10
DEFAULT_MODEL_PROFILE = "neural_scout"
MODEL_PROFILES = ("full_zoo", "neural_scout")
DEFAULT_MIN_ROC_AUC = 0.55
DEFAULT_MIN_AP_LIFT = 0.02
PRICE_CONTEXT_FEATURES = (
    "open", "high", "low", "close",
    "price_tr", "price_atr14", "price_er20", "price_range20_atr", "price_ret_1_atr",
)
SECTION_FEATURES: dict[str, tuple[str, ...]] = {
    "footprint_delta_flow": (
        *PRICE_CONTEXT_FEATURES,
        "nexus_fp_bar_delta", "nexus_fp_total_volume", "nexus_norm_cum_delta",
        "nexus_delta_slope", "nexus_bar_delta_ratio", "nexus_delta_dir",
    ),
    "volume_flow": (
        *PRICE_CONTEXT_FEATURES,
        "nexus_visible_vf_bull", "nexus_visible_vf_bear", "nexus_visible_vf_base",
        "nexus_visible_delta_gasout", "nexus_vf_calc", "nexus_gasout_bull",
        "nexus_gasout_bear", "nexus_fp_total_volume", "nexus_bar_delta_ratio",
    ),
    "oscillator_regime": (
        *PRICE_CONTEXT_FEATURES,
        "nexus_visible_nfe_oscillator", "nexus_visible_signal_line",
        "nexus_visible_ob_level", "nexus_visible_midline", "nexus_visible_os_level",
        "nexus_regime_score", "nexus_osc_momentum", "nexus_signal_tier",
        "nexus_norm_cum_delta", "nexus_delta_slope",
    ),
    "divergence_exhaustion": (
        *PRICE_CONTEXT_FEATURES,
        "nexus_div_reg_bull_raw", "nexus_div_reg_bear_raw",
        "nexus_div_hid_bull_raw", "nexus_div_hid_bear_raw",
        "nexus_div_reg_bull", "nexus_div_reg_bear",
        "nexus_div_hid_bull", "nexus_div_hid_bear",
        "nexus_visible_tier1_exhaustion", "nexus_visible_momentum_fatigue",
        "nexus_gasout_bull", "nexus_gasout_bear", "nexus_signal_tier",
    ),
    "signal_tier_composite": (
        *PRICE_CONTEXT_FEATURES,
        "nexus_signal_tier", "nexus_visible_tier1_exhaustion",
        "nexus_visible_tier2_cross", "nexus_visible_momentum_fatigue",
        "nexus_visible_nfe_oscillator", "nexus_visible_signal_line",
        "nexus_vf_calc", "nexus_regime_score", "nexus_osc_momentum",
        "nexus_fp_total_volume", "nexus_norm_cum_delta", "nexus_delta_slope",
        "nexus_bar_delta_ratio", "nexus_delta_dir",
    ),
    "all_features": (),
}
SECTION_TARGETS: dict[str, str] = {
    "footprint_delta_flow": PRIMARY_TARGET,
    "volume_flow": PRIMARY_TARGET,
    "oscillator_regime": "label_abs_move_ge_0p5atr_5b",
    "divergence_exhaustion": "label_swing_low_next_12b",
    "signal_tier_composite": PRIMARY_TARGET,
    "all_features": PRIMARY_TARGET,
}
SECTION_SEQUENCE = (
    "footprint_delta_flow",
    "volume_flow",
    "oscillator_regime",
    "divergence_exhaustion",
    "signal_tier_composite",
)

CANONICAL_MANIFEST_ROOT = WORKSPACE / "exports"
CANONICAL_DATASET_ROOT = WORKSPACE / "exports"
CANONICAL_DATASET_PATH = CANONICAL_DATASET_ROOT / "nexus_15m_dataset.parquet"
CANONICAL_MODEL_ROOT = DEFAULT_OUTPUT_ROOT
CANONICAL_REPORT_ROOT = DEFAULT_REPORTS_DIR


def _resolve_path(path: Path, *, must_exist: bool) -> Path:
    expanded = path.expanduser()
    try:
        return expanded.resolve(strict=must_exist)
    except FileNotFoundError:
        if must_exist:
            raise
        return expanded.resolve(strict=False)


def _is_within_root(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _restrict_path(
    path: Path,
    *,
    roots: tuple[Path, ...],
    purpose: str,
    must_exist: bool,
    required_suffix: str | None = None,
) -> Path:
    resolved = _resolve_path(path, must_exist=must_exist)
    resolved_roots = tuple(_resolve_path(root, must_exist=False) for root in roots)
    if not any(_is_within_root(resolved, root) for root in resolved_roots):
        allowed = ", ".join(str(root) for root in resolved_roots)
        raise RuntimeError(f"{purpose} must remain under approved roots: {allowed}. Got: {resolved}")
    if required_suffix and not resolved.name.endswith(required_suffix):
        raise RuntimeError(f"{purpose} must end with {required_suffix}: {resolved.name}")
    return resolved


def sha256_file(path: Path) -> str:
    safe_path = _restrict_path(
        path,
        roots=(REPO_ROOT,),
        purpose="Checksum path",
        must_exist=True,
    )
    if not safe_path.is_file():
        raise FileNotFoundError(f"Checksum path is not a file: {safe_path}")
    h = hashlib.sha256()
    with safe_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return "unknown"
    return result.stdout.strip() or "unknown"


def load_manifest(path: Path) -> dict[str, Any]:
    manifest_path = _restrict_path(
        path,
        roots=(CANONICAL_MANIFEST_ROOT,),
        purpose="Manifest path",
        must_exist=True,
        required_suffix=".manifest.json",
    )
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing Nexus dataset manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("trigger_family") != TRIGGER_FAMILY:
        raise RuntimeError(f"Manifest trigger_family must be {TRIGGER_FAMILY}, got {manifest.get('trigger_family')!r}")
    if manifest.get("capture_method") != CAPTURE_METHOD:
        raise RuntimeError(f"Manifest capture_method must be {CAPTURE_METHOD}, got {manifest.get('capture_method')!r}")
    notes = str(manifest.get("notes", ""))
    joined = json.dumps(manifest, sort_keys=True)
    for token in FORBIDDEN_REFERENCES:
        if token in joined:
            raise RuntimeError(f"Manifest contains forbidden cross-lane reference: {token}")
    if "No V9 artifacts used" not in notes:
        raise RuntimeError("Manifest must state: No V9 artifacts used")
    return manifest


def load_dataset(manifest: dict[str, Any]) -> pd.DataFrame:
    declared_dataset_path = _resolve_path(Path(str(manifest.get("dataset_parquet", ""))), must_exist=False)
    expected_dataset_path = _resolve_path(CANONICAL_DATASET_PATH, must_exist=False)
    if declared_dataset_path != expected_dataset_path:
        raise RuntimeError(
            "Manifest dataset_parquet must match the canonical Nexus export path: "
            f"{expected_dataset_path}; got {declared_dataset_path}"
        )
    dataset_path = _restrict_path(
        CANONICAL_DATASET_PATH,
        roots=(CANONICAL_DATASET_ROOT,),
        purpose="Dataset parquet path",
        must_exist=True,
        required_suffix=".parquet",
    )
    if not dataset_path.exists():
        raise FileNotFoundError(f"Missing Nexus dataset parquet: {dataset_path}")
    actual_sha = sha256_file(dataset_path)
    expected_sha = str(manifest.get("dataset_sha256", ""))
    if expected_sha and actual_sha != expected_sha:
        raise RuntimeError(f"Dataset SHA mismatch: manifest={expected_sha} actual={actual_sha}")
    df = pd.read_parquet(dataset_path)
    if "ts" not in df.columns or "split" not in df.columns:
        raise RuntimeError("Dataset must contain ts and split columns")
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df.sort_values("ts").reset_index(drop=True)


def _target_horizon_bars(target: str) -> int:
    match = re.search(r"_next_(\d+)b$", target)
    if match:
        return int(match.group(1))
    match = re.search(r"_(\d+)b$", target)
    if match:
        return int(match.group(1))
    return 1


def _parse_dynamic_stacking(value: str) -> bool | str:
    normalized = str(value).strip().lower()
    if normalized == "auto":
        return "auto"
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise argparse.ArgumentTypeError("dynamic stacking must be one of: auto, true, false")


def resolve_section_target(section: str, requested_target: str | None) -> str:
    if section not in SECTION_FEATURES:
        raise RuntimeError(f"Unknown Nexus section {section!r}; choices={sorted(SECTION_FEATURES)}")
    return str(requested_target or SECTION_TARGETS[section])


def resolve_section_features(section: str, manifest_features: list[str]) -> list[str]:
    if section not in SECTION_FEATURES:
        raise RuntimeError(f"Unknown Nexus section {section!r}; choices={sorted(SECTION_FEATURES)}")
    if section == "all_features":
        return list(manifest_features)
    allowed = list(dict.fromkeys(SECTION_FEATURES[section]))
    missing = [col for col in allowed if col not in manifest_features]
    if missing:
        raise RuntimeError(f"Section {section!r} references features missing from manifest: {missing}")
    return allowed


def baseline_metrics(frame: pd.DataFrame, target: str, train_rate: float) -> dict[str, float]:
    y = frame[target].astype(int).to_numpy()
    p = np.full(len(y), float(np.clip(train_rate, 1e-7, 1.0 - 1e-7)))
    return {
        "baseline_probability": float(train_rate),
        "baseline_log_loss": float(log_loss(y, p, labels=[0, 1])),
        "baseline_average_precision": float(frame[target].mean()),
    }


def section_decision_payload(
    *,
    test_metrics: dict[str, float],
    baseline: dict[str, float],
    min_roc_auc: float,
    min_ap_lift: float,
) -> dict[str, Any]:
    roc_auc = float(test_metrics.get("roc_auc", math.nan))
    average_precision = float(test_metrics.get("average_precision", math.nan))
    logloss_value = float(test_metrics.get("log_loss", math.inf))
    baseline_logloss = float(baseline.get("baseline_log_loss", math.inf))
    baseline_ap = float(baseline.get("baseline_average_precision", 0.0))
    ap_lift = average_precision - baseline_ap
    logloss_lift = baseline_logloss - logloss_value
    pass_gate = (
        math.isfinite(roc_auc)
        and roc_auc >= min_roc_auc
        and math.isfinite(ap_lift)
        and ap_lift >= min_ap_lift
        and math.isfinite(logloss_lift)
        and logloss_lift > 0.0
    )
    return {
        "decision": "save_and_proceed" if pass_gate else "rerun_or_expand_section",
        "passed": bool(pass_gate),
        "min_roc_auc": float(min_roc_auc),
        "min_ap_lift": float(min_ap_lift),
        "roc_auc": roc_auc,
        "average_precision_lift_vs_base_rate": float(ap_lift),
        "log_loss_lift_vs_baseline": float(logloss_lift),
        "reason": (
            "Chronological test beat baseline gates; save this section and proceed."
            if pass_gate
            else "Section did not clear chronological OOS gates; rerun with expanded budget/features before proceeding."
        ),
    }


def validate_heavy_fit_settings(
    *,
    manifest: dict[str, Any],
    target: str,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    num_bag_folds: int,
    num_bag_sets: int,
    num_stack_levels: int,
    hpo_trials: int,
    time_limit: int,
) -> dict[str, Any]:
    if num_bag_folds == 1:
        raise RuntimeError("AutoGluon num_bag_folds=1 is invalid; use 0 or >=2")
    if num_bag_folds < 0 or num_bag_sets < 1 or num_stack_levels < 0:
        raise RuntimeError("Bag folds, bag sets, and stack levels must be non-negative/positive as appropriate")
    if num_stack_levels > 0 and num_bag_folds < 2:
        raise RuntimeError("Stacking requires num_bag_folds >= 2 to avoid overfit stack training")
    if hpo_trials < 0:
        raise RuntimeError("hpo_trials must be >= 0")
    if time_limit < 3_600:
        raise RuntimeError("Research-heavy Nexus runs must allow at least 3600 seconds; use --validate-only for quick checks")

    label_horizon = _target_horizon_bars(target)
    embargo_bars = int(manifest.get("embargo_bars", 0))
    if embargo_bars < label_horizon + 1:
        raise RuntimeError(
            f"Manifest embargo_bars={embargo_bars} is below target horizon+1 ({label_horizon + 1}); "
            "heavy training would risk label leakage"
        )

    if not (train_df["ts"].max() < val_df["ts"].min() < val_df["ts"].max() < test_df["ts"].min()):
        raise RuntimeError("Train/validation/test splits are not strictly chronological")

    return {
        "label_horizon_bars": int(label_horizon),
        "embargo_bars": int(embargo_bars),
        "bagging_policy": (
            "AutoGluon k-fold bagging is allowed only inside the historical train segment; "
            "chronological validation is passed as tuning_data with use_bag_holdout=True, "
            "and the future test split is never used for fitting or ensemble weighting."
        ),
        "proof_policy": "Use chronological validation/test metrics only; never treat internal k-fold scores as OOS proof.",
    }


def prepare_training_frames(
    df: pd.DataFrame,
    manifest: dict[str, Any],
    target: str,
    section: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    feature_cols = resolve_section_features(section, list(manifest.get("feature_columns", [])))
    label_cols = set(manifest.get("label_columns", []))
    if target not in label_cols:
        raise RuntimeError(f"Target {target!r} is not declared in manifest label_columns")
    missing = [col for col in [*feature_cols, target, "split", "nexus_fp_quality_ok"] if col not in df.columns]
    if missing:
        raise RuntimeError(f"Dataset missing required training columns: {missing}")
    leakage = [col for col in feature_cols if col.startswith("label_") or col.startswith("event_") or col.startswith("fwd_") or col in {"time", "ts", "split"}]
    if leakage:
        raise RuntimeError(f"Feature list contains leakage columns: {leakage}")
    non_numeric = [col for col in feature_cols if not pd.api.types.is_numeric_dtype(df[col])]
    if non_numeric:
        raise RuntimeError(f"Feature columns must be numeric for Nexus heavy model: {non_numeric}")

    eligible = df[df["split"].isin(REQUIRED_SPLITS)].copy()
    eligible = eligible[eligible["nexus_fp_quality_ok"].fillna(0).astype(float).gt(0)].copy()
    eligible = eligible[eligible[target].notna()].copy()
    eligible[target] = pd.to_numeric(eligible[target], errors="raise").astype(int)
    for col in feature_cols:
        eligible[col] = pd.to_numeric(eligible[col], errors="coerce")
        if np.isinf(eligible[col].to_numpy(dtype=float, na_value=np.nan)).any():
            raise RuntimeError(f"Feature column contains +/-inf: {col}")
    if eligible.empty:
        raise RuntimeError("No eligible footprint-quality rows available for training")

    splits = {name: eligible[eligible["split"] == name].copy() for name in REQUIRED_SPLITS}
    thin = {name: len(frame) for name, frame in splits.items() if len(frame) < 50}
    if thin:
        raise RuntimeError(f"Training split too thin: {thin}")
    for name, frame in splits.items():
        classes = sorted(int(v) for v in frame[target].dropna().unique())
        if classes != [0, 1]:
            raise RuntimeError(f"{name} split for {target} must contain both 0/1 classes, got {classes}")
    return splits["train"], splits["validation"], splits["test"], feature_cols


def _class_counts(frame: pd.DataFrame, target: str) -> dict[str, int]:
    return {str(k): int(v) for k, v in frame[target].value_counts(dropna=False).sort_index().items()}


def _split_payload(frame: pd.DataFrame, target: str) -> dict[str, Any]:
    return {
        "rows": int(len(frame)),
        "positive_rows": int(frame[target].sum()),
        "positive_rate": float(frame[target].mean()),
        "class_counts": _class_counts(frame, target),
        "ts_start": frame["ts"].min().isoformat() if len(frame) else None,
        "ts_end": frame["ts"].max().isoformat() if len(frame) else None,
    }


def _positive_proba(proba: pd.DataFrame | pd.Series | np.ndarray) -> np.ndarray:
    if isinstance(proba, pd.DataFrame):
        for candidate in (1, "1", True, "True"):
            if candidate in proba.columns:
                return proba[candidate].to_numpy(dtype=float)
        return proba.iloc[:, -1].to_numpy(dtype=float)
    if isinstance(proba, pd.Series):
        return proba.to_numpy(dtype=float)
    arr = np.asarray(proba, dtype=float)
    if arr.ndim == 2:
        return arr[:, -1]
    return arr


def _metrics(y_true: pd.Series, y_prob: np.ndarray) -> dict[str, float]:
    y = y_true.astype(int).to_numpy()
    clipped = np.clip(y_prob.astype(float), 1e-7, 1.0 - 1e-7)
    y_pred = (clipped >= 0.5).astype(int)
    out: dict[str, float] = {
        "log_loss": float(log_loss(y, clipped, labels=[0, 1])),
        "brier_score": float(brier_score_loss(y, clipped)),
        "accuracy_at_0p5": float(accuracy_score(y, y_pred)),
        "positive_rate_pred_at_0p5": float(y_pred.mean()),
        "mean_positive_probability": float(clipped.mean()),
    }
    if len(np.unique(y)) == 2:
        out["roc_auc"] = float(roc_auc_score(y, clipped))
        out["average_precision"] = float(average_precision_score(y, clipped))
    else:
        out["roc_auc"] = math.nan
        out["average_precision"] = math.nan
    return out


def model_hyperparameters(profile: str) -> dict[str, Any]:
    if profile == "full_zoo":
        return {
            "GBM": [{"num_threads": 1}, {"num_threads": 1, "extra_trees": True}],
            "CAT": {"thread_count": 1},
            "XGB": {"n_jobs": 1},
            "RF": [{"criterion": "gini"}, {"criterion": "entropy"}],
            "XT": [{"criterion": "gini"}, {"criterion": "entropy"}],
            "NN_TORCH": {},
            "FASTAI": {},
        }
    if profile == "neural_scout":
        return {
            "FASTAI": {},
            "NN_TORCH": {},
            "GBM": {
                "num_threads": 1,
                "learning_rate": 0.05,
                "num_leaves": 31,
                "feature_fraction": 0.9,
                "min_data_in_leaf": 50,
                "ag_args": {"name_suffix": "Scout"},
            },
            "CAT": {
                "thread_count": 1,
                "iterations": 400,
                "learning_rate": 0.05,
                "depth": 6,
                "l2_leaf_reg": 3.0,
                "ag_args": {"name_suffix": "Scout"},
            },
            "XGB": {
                "n_jobs": 1,
                "n_estimators": 400,
                "learning_rate": 0.05,
                "max_depth": 4,
                "min_child_weight": 5,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "ag_args": {"name_suffix": "Scout"},
            },
        }
    raise RuntimeError(f"Unknown model_profile={profile!r}; choices={MODEL_PROFILES}")


def model_profile_contract(profile: str) -> dict[str, Any]:
    hp = model_hyperparameters(profile)
    if profile == "neural_scout":
        return {
            "profile": profile,
            "full_hpo_families": ["FASTAI", "NN_TORCH"],
            "fixed_scout_families": ["GBM", "CAT", "XGB"],
            "dropped_families": ["RF", "XT"],
            "reason": "Sections 01-02 OOS leaderboards were dominated by neural families; trees are fixed tiny scouts only.",
        }
    return {
        "profile": profile,
        "full_hpo_families": list(hp),
        "fixed_scout_families": [],
        "dropped_families": [],
        "reason": "Full zoo profile retained for audit/reproduction.",
    }


def _write_markdown(summary: dict[str, Any], path: Path) -> None:
    safe_path = _restrict_path(
        path,
        roots=(CANONICAL_MODEL_ROOT, CANONICAL_REPORT_ROOT),
        purpose="Markdown summary path",
        must_exist=False,
        required_suffix=".md",
    )
    lines = [
        "# Nexus 15m Heavy Training Run\n",
        "\n## Scope\n",
        f"- Trigger family: `{summary['trigger_family']}`\n",
        f"- Section: `{summary['section']}`\n",
        f"- Target: `{summary['target']}`\n",
        f"- Dataset: `{summary['dataset_path']}`\n",
        f"- Output dir: `{summary['output_dir']}`\n",
        "- Scope lock: Nexus-only; no V9 Pine/trainer/export/model/fib surface used.\n",
        "\n## Split Counts\n",
        "| Split | Rows | Positives | Positive rate | Start | End |\n",
        "| --- | ---: | ---: | ---: | --- | --- |\n",
    ]
    for name in ("train", "validation", "test"):
        item = summary["splits"][name]
        lines.append(f"| {name} | {item['rows']} | {item['positive_rows']} | {item['positive_rate']:.4f} | {item['ts_start']} | {item['ts_end']} |\n")
    lines.extend([
        "\n## Model Settings\n",
        f"- Presets: `{summary['fit_settings']['presets']}`\n",
        f"- Eval metric: `{summary['fit_settings']['eval_metric']}`\n",
        f"- Time limit seconds: `{summary['fit_settings']['time_limit_sec']}`\n",
        f"- HPO trials per family: `{summary['fit_settings']['hpo_num_trials']}`\n",
        f"- Bag folds: `{summary['fit_settings']['num_bag_folds']}` x `{summary['fit_settings']['num_bag_sets']}` sets\n",
        f"- Stack levels: `{summary['fit_settings']['num_stack_levels']}`\n",
        f"- Dynamic stacking: `{summary['fit_settings']['dynamic_stacking']}`\n",
        f"- Use bag holdout: `{summary['fit_settings']['use_bag_holdout']}`\n",
        f"- Feature-importance shuffles: `{summary['fit_settings']['feature_importance_shuffles']}`\n",
        f"- Model profile: `{summary['fit_settings']['model_profile']}`\n",
        f"- Full HPO families: `{summary['fit_settings']['model_profile_contract']['full_hpo_families']}`\n",
        f"- Fixed scout families: `{summary['fit_settings']['model_profile_contract']['fixed_scout_families']}`\n",
        f"- Dropped families: `{summary['fit_settings']['model_profile_contract']['dropped_families']}`\n",
        "\n## Leakage / Look-Forward Guard\n",
        f"- Label horizon bars: `{summary['leakage_guard']['label_horizon_bars']}`\n",
        f"- Embargo bars: `{summary['leakage_guard']['embargo_bars']}`\n",
        f"- Bagging policy: {summary['leakage_guard']['bagging_policy']}\n",
        f"- Proof policy: {summary['leakage_guard']['proof_policy']}\n",
        "\n## Baseline / Section Decision\n",
        f"- Baseline log loss: `{summary['baseline_metrics']['baseline_log_loss']}`\n",
        f"- Baseline average precision: `{summary['baseline_metrics']['baseline_average_precision']}`\n",
        f"- Decision: `{summary['section_decision']['decision']}`\n",
        f"- Decision reason: {summary['section_decision']['reason']}\n",
        "\n## Test Metrics\n",
    ])
    for key, value in summary["test_metrics"].items():
        lines.append(f"- `{key}`: `{value}`\n")
    lines.extend([
        "\n## Leaderboard\n",
        f"- Top model: `{summary['leaderboard_top_model']}`\n",
        f"- Top score test: `{summary['leaderboard_top_score_test']}`\n",
        f"- Top score validation: `{summary['leaderboard_top_score_val']}`\n",
        "\n## Top Feature Importance\n",
    ])
    for feature, payload in list(summary["feature_importance_top10"].items())[:10]:
        importance = payload.get("importance") if isinstance(payload, dict) else payload
        lines.append(f"- `{feature}`: `{importance}`\n")
    safe_path.parent.mkdir(parents=True, exist_ok=True)
    safe_path.write_text("".join(lines))


def fit_heavy_model(
    *,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: list[str],
    target: str,
    out_dir: Path,
    time_limit: int,
    hpo_trials: int,
    num_bag_folds: int,
    num_bag_sets: int,
    num_stack_levels: int,
    dynamic_stacking: bool | str,
    feature_importance_shuffles: int,
    model_profile: str,
) -> tuple[Any, dict[str, Any]]:
    from autogluon.tabular import TabularPredictor

    out_dir.parent.mkdir(parents=True, exist_ok=True)
    predictor = TabularPredictor(
        label=target,
        path=str(out_dir),
        eval_metric=EVAL_METRIC,
        problem_type=PROBLEM_TYPE,
    ).fit(
        train_data=train_df[feature_cols + [target]],
        tuning_data=val_df[feature_cols + [target]],
        use_bag_holdout=num_bag_folds >= 2,
        time_limit=time_limit,
        presets="best_quality",
        calibrate=True,
        num_bag_folds=num_bag_folds,
        num_bag_sets=num_bag_sets,
        num_stack_levels=num_stack_levels,
        dynamic_stacking=dynamic_stacking,
        delay_bag_sets=False,
        ag_args_ensemble={"fold_fitting_strategy": "sequential_local"},
        hyperparameter_tune_kwargs=(
            {
                "searcher": "random",
                "scheduler": "local",
                "num_trials": hpo_trials,
            }
            if hpo_trials > 0
            else None
        ),
        hyperparameters=model_hyperparameters(model_profile),
        verbosity=2,
        num_gpus=0,
    )
    predictor.persist()
    test_data = test_df[feature_cols + [target]]
    leaderboard = predictor.leaderboard(test_data, extra_info=True, silent=True)
    leaderboard.to_csv(out_dir / "leaderboard.csv", index=False)
    feature_importance = predictor.feature_importance(test_data, num_shuffle_sets=feature_importance_shuffles)
    feature_importance.to_csv(out_dir / "feature_importance.csv")
    proba = predictor.predict_proba(test_data)
    y_prob = _positive_proba(proba)
    pd.DataFrame(
        {
            "ts": test_df["ts"].astype(str).to_numpy(),
            "y_true": test_df[target].astype(int).to_numpy(),
            "p_positive": y_prob,
        }
    ).to_csv(out_dir / "test_predictions.csv", index=False)
    model_summary = {
        "leaderboard_top_model": str(leaderboard.iloc[0]["model"]) if len(leaderboard) else None,
        "leaderboard_top_score_test": float(leaderboard.iloc[0]["score_test"]) if len(leaderboard) else None,
        "leaderboard_top_score_val": float(leaderboard.iloc[0]["score_val"]) if len(leaderboard) else None,
        "test_metrics": _metrics(test_df[target], y_prob),
        "feature_importance_top10": feature_importance.head(10).to_dict(orient="index"),
    }
    return predictor, model_summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    ap.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    ap.add_argument("--section", default="all_features", choices=sorted(SECTION_FEATURES))
    ap.add_argument("--target", default=None, help="Override the default target for the selected section.")
    ap.add_argument("--list-sections", action="store_true")
    ap.add_argument("--time-limit", type=int, default=DEFAULT_TIME_LIMIT_SEC)
    ap.add_argument("--hpo-trials", type=int, default=DEFAULT_HPO_TRIALS)
    ap.add_argument("--num-bag-folds", type=int, default=DEFAULT_NUM_BAG_FOLDS)
    ap.add_argument("--num-bag-sets", type=int, default=DEFAULT_NUM_BAG_SETS)
    ap.add_argument("--num-stack-levels", type=int, default=DEFAULT_NUM_STACK_LEVELS)
    ap.add_argument("--dynamic-stacking", type=_parse_dynamic_stacking, default=DEFAULT_DYNAMIC_STACKING)
    ap.add_argument("--model-profile", choices=MODEL_PROFILES, default=DEFAULT_MODEL_PROFILE)
    ap.add_argument("--feature-importance-shuffles", type=int, default=DEFAULT_FEATURE_IMPORTANCE_SHUFFLES)
    ap.add_argument("--min-roc-auc", type=float, default=DEFAULT_MIN_ROC_AUC)
    ap.add_argument("--min-ap-lift", type=float, default=DEFAULT_MIN_AP_LIFT)
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()

    if args.list_sections:
        print(json.dumps({name: {"target": SECTION_TARGETS[name], "features": list(resolve_section_features(name, list(SECTION_FEATURES[name]) if name != "all_features" else [])) if name != "all_features" else "manifest_all"} for name in SECTION_FEATURES}, indent=2))
        return 0

    if args.manifest != DEFAULT_MANIFEST:
        raise RuntimeError(
            f"--manifest override is disabled for security hardening; use the canonical manifest: {DEFAULT_MANIFEST}"
        )
    if args.output_root != DEFAULT_OUTPUT_ROOT:
        raise RuntimeError(
            f"--output-root override is disabled for security hardening; use the canonical output root: {DEFAULT_OUTPUT_ROOT}"
        )
    if args.reports_dir != DEFAULT_REPORTS_DIR:
        raise RuntimeError(
            f"--reports-dir override is disabled for security hardening; use the canonical reports dir: {DEFAULT_REPORTS_DIR}"
        )
    if args.target is not None:
        raise RuntimeError("--target override is disabled for security hardening; section target mapping is enforced")

    manifest_path = _restrict_path(
        DEFAULT_MANIFEST,
        roots=(CANONICAL_MANIFEST_ROOT,),
        purpose="CLI manifest path",
        must_exist=True,
        required_suffix=".manifest.json",
    )
    manifest = load_manifest(manifest_path)
    target = resolve_section_target(args.section, None)
    df = load_dataset(manifest)
    train_df, val_df, test_df, feature_cols = prepare_training_frames(df, manifest, target, args.section)

    print("Nexus 15m heavy training preflight", flush=True)
    print(f"  dataset: {manifest['dataset_parquet']}", flush=True)
    print(f"  section: {args.section}", flush=True)
    print(f"  target:  {target}", flush=True)
    print(f"  rows:    train={len(train_df):,} val={len(val_df):,} test={len(test_df):,}", flush=True)
    print(f"  pos:     train={train_df[target].mean():.4f} val={val_df[target].mean():.4f} test={test_df[target].mean():.4f}", flush=True)
    print(f"  features:{len(feature_cols)}", flush=True)
    print("  scope:   Nexus-only; no V9 artifacts used", flush=True)

    leakage_guard = validate_heavy_fit_settings(
        manifest=manifest,
        target=target,
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        num_bag_folds=args.num_bag_folds,
        num_bag_sets=args.num_bag_sets,
        num_stack_levels=args.num_stack_levels,
        hpo_trials=args.hpo_trials,
        time_limit=args.time_limit,
    )
    print(f"  bagging: folds={args.num_bag_folds} sets={args.num_bag_sets} stack_levels={args.num_stack_levels}", flush=True)
    print(f"  dynamic_stacking={args.dynamic_stacking} hpo_trials={args.hpo_trials}", flush=True)
    print(f"  model_profile={args.model_profile} contract={model_profile_contract(args.model_profile)}", flush=True)
    print(f"  leakage_guard: embargo={leakage_guard['embargo_bars']} horizon={leakage_guard['label_horizon_bars']}", flush=True)

    if args.validate_only:
        print("validate-only PASS", flush=True)
        return 0

    safe_output_root = _restrict_path(
        DEFAULT_OUTPUT_ROOT,
        roots=(CANONICAL_MODEL_ROOT,),
        purpose="CLI output root",
        must_exist=False,
    )
    safe_reports_dir = _restrict_path(
        DEFAULT_REPORTS_DIR,
        roots=(CANONICAL_REPORT_ROOT,),
        purpose="CLI reports dir",
        must_exist=False,
    )
    ts_tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = safe_output_root / f"heavy_{ts_tag}" / args.section / target
    safe_reports_dir.mkdir(parents=True, exist_ok=True)
    print("\nNEXUS HEAVY AG run", flush=True)
    print(f"  output dir: {out_dir}", flush=True)
    print(f"  time-limit: {args.time_limit}s", flush=True)
    print(f"  HPO trials: {args.hpo_trials} per family", flush=True)
    print(f"  bag folds:  {args.num_bag_folds} x {args.num_bag_sets} sets", flush=True)
    print(f"  stack:      {args.num_stack_levels} dynamic={args.dynamic_stacking}", flush=True)
    print(f"  profile:    {args.model_profile}", flush=True)
    print(f"  eval:       {EVAL_METRIC}", flush=True)
    print(f"  OMP_NUM_THREADS={os.environ.get('OMP_NUM_THREADS')} KMP_DUPLICATE_LIB_OK={os.environ.get('KMP_DUPLICATE_LIB_OK')}", flush=True)

    _, model_summary = fit_heavy_model(
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        feature_cols=feature_cols,
        target=target,
        out_dir=out_dir,
        time_limit=args.time_limit,
        hpo_trials=args.hpo_trials,
        num_bag_folds=args.num_bag_folds,
        num_bag_sets=args.num_bag_sets,
        num_stack_levels=args.num_stack_levels,
        dynamic_stacking=args.dynamic_stacking,
        feature_importance_shuffles=args.feature_importance_shuffles,
        model_profile=args.model_profile,
    )
    run_dir = out_dir.parent
    base_metrics = baseline_metrics(test_df, target, float(train_df[target].mean()))
    decision = section_decision_payload(
        test_metrics=model_summary["test_metrics"],
        baseline=base_metrics,
        min_roc_auc=args.min_roc_auc,
        min_ap_lift=args.min_ap_lift,
    )
    summary = {
        "trained_at_utc": ts_tag,
        "training_started": True,
        "trigger_family": TRIGGER_FAMILY,
        "capture_method": CAPTURE_METHOD,
        "section": args.section,
        "target": target,
        "problem_type": PROBLEM_TYPE,
        "eval_metric": EVAL_METRIC,
        "dataset_path": manifest["dataset_parquet"],
        "dataset_sha256": manifest.get("dataset_sha256"),
        "manifest_path": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "source_csv": manifest.get("source_csv"),
        "source_sha256": manifest.get("source_sha256"),
        "output_dir": str(run_dir),
        "model_dir": str(out_dir),
        "feature_count": len(feature_cols),
        "feature_columns": feature_cols,
        "splits": {
            "train": _split_payload(train_df, target),
            "validation": _split_payload(val_df, target),
            "test": _split_payload(test_df, target),
        },
        "section_contract": {
            "section_sequence": list(SECTION_SEQUENCE),
            "default_target_for_section": SECTION_TARGETS[args.section],
            "section_feature_count": len(feature_cols),
        },
        "fit_settings": {
            "presets": "best_quality",
            "eval_metric": EVAL_METRIC,
            "time_limit_sec": int(args.time_limit),
            "hpo_num_trials": int(args.hpo_trials),
            "calibrate": True,
            "use_bag_holdout": bool(args.num_bag_folds >= 2),
            "num_bag_folds": int(args.num_bag_folds),
            "num_bag_sets": int(args.num_bag_sets),
            "num_stack_levels": int(args.num_stack_levels),
            "dynamic_stacking": args.dynamic_stacking,
            "delay_bag_sets": False,
            "feature_importance_shuffles": int(args.feature_importance_shuffles),
            "model_profile": args.model_profile,
            "model_profile_contract": model_profile_contract(args.model_profile),
            "min_roc_auc": float(args.min_roc_auc),
            "min_ap_lift": float(args.min_ap_lift),
            "hyperparameter_families": list(model_hyperparameters(args.model_profile)),
        },
        "leakage_guard": leakage_guard,
        "baseline_metrics": base_metrics,
        "section_decision": decision,
        "repo_commit": repo_commit(),
        "scope_lock": "Nexus-only; No V9 Pine/trainer/export/model/fib surface used.",
        **model_summary,
    }
    summary_path = _restrict_path(
        run_dir / "nexus_15m_heavy_training_summary.json",
        roots=(CANONICAL_MODEL_ROOT,),
        purpose="JSON summary path",
        must_exist=False,
        required_suffix=".json",
    )
    summary_md_path = _restrict_path(
        run_dir / "nexus_15m_heavy_training_summary.md",
        roots=(CANONICAL_MODEL_ROOT,),
        purpose="Markdown summary path",
        must_exist=False,
        required_suffix=".md",
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    _write_markdown(summary, summary_md_path)
    latest_json = _restrict_path(
        safe_reports_dir / "heavy_training_latest.json",
        roots=(CANONICAL_REPORT_ROOT,),
        purpose="Latest JSON report path",
        must_exist=False,
        required_suffix=".json",
    )
    latest_md = _restrict_path(
        safe_reports_dir / "heavy_training_latest.md",
        roots=(CANONICAL_REPORT_ROOT,),
        purpose="Latest Markdown report path",
        must_exist=False,
        required_suffix=".md",
    )
    latest_json.parent.mkdir(parents=True, exist_ok=True)
    latest_json.write_text(json.dumps(summary, indent=2, default=str))
    _write_markdown(summary, latest_md)
    print(f"\nwrote {summary_path}", flush=True)
    print(f"wrote {summary_md_path}", flush=True)
    print(f"latest report: {latest_md}", flush=True)
    print(f"top model: {summary['leaderboard_top_model']} score_test={summary['leaderboard_top_score_test']}", flush=True)
    print(f"section decision: {summary['section_decision']['decision']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
