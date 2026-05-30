"""Tests for engine/databento_feed.py — gap-fill, contract roll, feed lifecycle."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from engine.databento_feed import (
    active_mes_contract,
    compute_gap_hours,
    detect_contract_roll,
    gap_fill_decision,
)


# ── Gap-fill cost cap tests ───────────────────────────────────────────────────

def test_gap_fill_auto():
    assert gap_fill_decision(1.0) == "auto"
    assert gap_fill_decision(5.9) == "auto"


def test_gap_fill_warn():
    assert gap_fill_decision(6.0) == "warn"
    assert gap_fill_decision(12.0) == "warn"
    assert gap_fill_decision(24.0) == "warn"


def test_gap_fill_refuse():
    assert gap_fill_decision(24.1) == "refuse"
    assert gap_fill_decision(48.0) == "refuse"
    assert gap_fill_decision(float("inf")) == "refuse"


def test_compute_gap_hours_none():
    assert compute_gap_hours(None) == float("inf")


def test_compute_gap_hours_recent():
    now = datetime.now(timezone.utc)
    result = compute_gap_hours(now)
    assert result < 0.01


# ── Contract roll detection ───────────────────────────────────────────────────

def test_active_mes_contract_format():
    contract = active_mes_contract()
    assert contract.startswith("MES")
    assert len(contract) == 6  # e.g. MESM26
    assert contract[3] in "HMUZ"


def test_detect_contract_roll_returns_bool():
    result = detect_contract_roll()
    assert isinstance(result, bool)
