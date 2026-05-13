from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

import pandas as pd


def _as_set(values: Iterable[str] | None) -> set[str]:
    return set(values or ())


def validate_required_columns(frame: pd.DataFrame, required_columns: Iterable[str]) -> None:
    required = list(required_columns)
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise RuntimeError(f"missing required columns: {missing}")


def validate_manifest_hash(csv_path: Path, manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text())
    expected = str(manifest.get("sha256", "")).strip().lower()

    digest = hashlib.sha256()
    digest.update(csv_path.read_bytes())
    actual = digest.hexdigest().lower()

    if not expected or expected != actual:
        raise RuntimeError(
            f"manifest hash mismatch: expected={expected or '<missing>'} actual={actual}"
        )


def validate_duplicate_real_signals(
    frame: pd.DataFrame,
    signal_columns: Iterable[str],
    allow_constant_columns: Iterable[str] | None = None,
) -> None:
    allowed_constant = _as_set(allow_constant_columns)
    candidates = [
        column
        for column in signal_columns
        if column in frame.columns and column not in allowed_constant
    ]

    for idx, left in enumerate(candidates):
        left_series = frame[left]
        for right in candidates[idx + 1 :]:
            right_series = frame[right]
            if left_series.equals(right_series):
                raise RuntimeError(
                    f"duplicate real signal columns: {left} and {right}"
                )


def validate_signal_health(
    frame: pd.DataFrame,
    continuous_columns: Iterable[str],
    knob_constant_whitelist: Iterable[str] | None = None,
    sparse_event_columns: Iterable[str] | None = None,
    sparse_event_whitelist: Iterable[str] | None = None,
    min_unique_ratio: float = 0.05,
    sparse_event_max_density: float = 0.02,
) -> None:
    whitelist = _as_set(knob_constant_whitelist)
    row_count = max(len(frame), 1)

    for column in continuous_columns:
        if column not in frame.columns:
            continue

        series = frame[column]
        unique_count = int(series.nunique(dropna=True))

        if unique_count <= 1:
            if column in whitelist:
                continue
            raise RuntimeError(f"constant continuous signal: {column}")

        value_freq = series.value_counts(normalize=True, dropna=False)
        dominant_density = float(value_freq.iloc[0]) if not value_freq.empty else 1.0
        if dominant_density >= (1.0 - float(min_unique_ratio)):
            raise RuntimeError(f"near-dead continuous signal: {column}")

    sparse_columns = list(sparse_event_columns or ())
    sparse_whitelist = _as_set(sparse_event_whitelist)
    for column in sparse_columns:
        if column not in frame.columns:
            continue

        nonzero_density = float((frame[column] != 0).mean())
        if nonzero_density <= sparse_event_max_density and column not in sparse_whitelist:
            raise RuntimeError(f"sparse event flag requires whitelist: {column}")