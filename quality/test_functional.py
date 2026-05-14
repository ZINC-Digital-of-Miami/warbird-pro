from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts.ag import backfill_v9_run_provenance as backfill
from scripts.ag.monte_carlo_v9 import (
    SUITE_HEADS,
    _is_suite_root,
    _resolve_payoff_arrays,
    _resolve_predictor_path,
)
from scripts.ag.train_v9_locked import (
    EMBARGO_BARS,
    FORWARD_SCAN_BARS,
    LABEL_COL,
    ML_FEATURES,
    MODEL_FEATURES,
    build_trade_dataset,
    split_trade_positions,
    validate_input_schema,
)
from scripts.ag.v9_data_quality_gate import (
    validate_duplicate_real_signals,
    validate_manifest_hash,
    validate_required_columns,
    validate_signal_health,
)
from scripts.ag.v9_run_provenance import (
    apply_time_split,
    build_csv_provenance,
    check_summary_csv_hash,
    split_bounds_from_summary,
)
from scripts.duckdb_local.workspaces.warbird_pro_core import build_core_dataset as core


BOOL_FEATURE_COLUMNS = {
    "knob_auto_tune_zz",
    "knob_use_pattern_confirm",
    "knob_use_liq_gate",
    "knob_use_ma_gate",
    "knob_use_session_vwap",
    "knob_use_xa_gate",
}

STRING_FEATURE_COLUMNS = {
    "knob_nq_symbol",
    "knob_6e_symbol",
    "knob_zn_symbol",
    "knob_vix_symbol",
    "knob_zn_gate_direction",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _write_small_csv(path: Path) -> None:
    path.write_text("ts,value\n2026-01-01T00:00:00+00:00,1\n")


def _feature_defaults() -> dict[str, object]:
    values: dict[str, object] = {}
    for column in ML_FEATURES:
        if column in STRING_FEATURE_COLUMNS:
            values[column] = "TEST"
        elif column in BOOL_FEATURE_COLUMNS:
            values[column] = False
        else:
            values[column] = 0.0
    values["knob_nq_symbol"] = "CME_MINI:NQ1!"
    values["knob_6e_symbol"] = "CME:6E1!"
    values["ml_atr14"] = 2.0
    return values


def _core_export_frame(row_count: int = 8) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    start = pd.Timestamp("2026-01-01T00:00:00Z")
    for idx in range(row_count):
        rec = _feature_defaults()
        rec.update(
            {
                "ts": start + pd.Timedelta(minutes=15 * idx),
                "open": 100.0 + idx,
                "high": 101.0 + idx,
                "low": 99.0 + idx,
                "close": 100.5 + idx,
                "volume": 1000.0 + idx,
                "ml_entry_long_trigger": 1.0 if idx == 0 else 0.0,
                "ml_entry_short_trigger": 0.0,
                "ml_trade_entry": 100.0 if idx == 0 else 0.0,
                "ml_trade_stop": 98.0 if idx == 0 else 0.0,
                "ml_trade_tp1": 101.0 if idx == 0 else 0.0,
                "ml_trade_tp2": 102.0 if idx == 0 else 0.0,
                "ml_trade_tp3": 103.0 if idx == 0 else 0.0,
            }
        )
        rows.append(rec)
    return pd.DataFrame(rows)


def _trade_frame(
    *,
    row_count: int = 30,
    entry_idx: int = 0,
    long_entry: bool = True,
    tp_values: tuple[float, float, float] = (101.0, 102.0, 103.0),
    custom_bars: dict[int, tuple[float, float, float]] | None = None,
) -> pd.DataFrame:
    bars = custom_bars or {}
    rows: list[dict[str, object]] = []
    start = pd.Timestamp("2026-01-01T00:00:00Z")
    for idx in range(row_count):
        high, low, close = bars.get(idx, (100.5, 99.5, 100.0))
        rec = _feature_defaults()
        rec.update(
            {
                "ts": start + pd.Timedelta(minutes=15 * idx),
                "high": high,
                "low": low,
                "close": close,
                "ml_entry_long_trigger": 1.0 if idx == entry_idx and long_entry else 0.0,
                "ml_entry_short_trigger": 1.0 if idx == entry_idx and not long_entry else 0.0,
                "ml_trade_entry": 100.0 if idx == entry_idx else 0.0,
                "ml_trade_stop": 98.0 if idx == entry_idx else 0.0,
                "ml_trade_tp1": tp_values[0] if idx == entry_idx else 0.0,
                "ml_trade_tp2": tp_values[1] if idx == entry_idx else 0.0,
                "ml_trade_tp3": tp_values[2] if idx == entry_idx else 0.0,
            }
        )
        rows.append(rec)
    return pd.DataFrame(rows)


def _valid_manifest() -> dict[str, object]:
    return {
        "repo_commit": "abc123",
        "symbol": "ES",
        "symbol_root": "ES",
        "timeframe": "15",
        "trigger_family": core.TRIGGER_FAMILY,
        "source_kind": "DATABENTO_ES_CORE_ETL",
        "source_bars": "data/es_1m_20260503.parquet",
        "label_column": core.LABEL_COL,
        "feature_count_locked": len(core.ML_FEATURES),
        "row_count": 100,
        "entry_long_count": 55,
        "entry_short_count": 45,
        "profiling_report_path": "scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.profile.html",
        "profiling_rows_profiled": 100,
    }


def _summary_with_ranges() -> dict[str, object]:
    return {
        "run_provenance": {"csv_sha256": "abc"},
        "split_ranges_utc": {
            "train": {
                "ts_start": "2026-01-01T00:00:00+00:00",
                "ts_end": "2026-01-31T00:00:00+00:00",
            },
            "val": {
                "ts_start": "2026-02-01T00:00:00+00:00",
                "ts_end": "2026-02-28T00:00:00+00:00",
            },
            "oos": {
                "ts_start": "2026-03-01T00:00:00+00:00",
                "ts_end": "2026-03-31T00:00:00+00:00",
            },
        },
    }


class TestSpecRequirements:
    def test_spec_1_locked_feature_surface_counts(self) -> None:
        """[Req: formal — train_v9_locked locked feature surface] Feature counts stay fixed."""
        assert len(ML_FEATURES) == 78
        assert len(MODEL_FEATURES) == 84

    @pytest.mark.parametrize(
        ("mode", "expected_count"),
        [
            ("base", 1),
            ("ma-grid", len(core.MA_FAST_GRID) * len(core.MA_SLOW_GRID)),
        ],
    )
    def test_spec_2_generate_indicator_profiles_contract(self, mode: str, expected_count: int) -> None:
        """[Req: formal — build_core_dataset profile mode contract] Profile modes produce deterministic surfaces."""
        profiles = core.generate_indicator_profiles(mode)
        assert len(profiles) == expected_count

    def test_spec_3_manifest_contract_accepts_valid_payload(self) -> None:
        """[Req: formal — build_core_dataset manifest schema] Valid manifests pass contract checks."""
        core.validate_manifest_contract(_valid_manifest())

    @pytest.mark.parametrize(
        "bad_source_kind",
        ["TRADINGVIEW_INDICATOR_CSV", "CSV", "UNKNOWN_PIPELINE"],
    )
    def test_spec_4_manifest_source_kind_requires_databento_prefix(self, bad_source_kind: str) -> None:
        """[Req: formal — source_kind must start with DATABENTO_] Non-approved source kinds are rejected."""
        manifest = _valid_manifest()
        manifest["source_kind"] = bad_source_kind

        with pytest.raises(Exception):
            core.validate_manifest_contract(manifest)

    def test_spec_5_validate_input_schema_requires_label_input_columns(self) -> None:
        """[Req: formal — label-construction tp columns required] Missing tp ladder inputs are fatal."""
        frame = _trade_frame()
        frame = frame.drop(columns=["ml_trade_tp2"])

        with pytest.raises(RuntimeError, match="missing required columns"):
            validate_input_schema(frame)

    def test_spec_6_validate_input_schema_rejects_stale_columns(self) -> None:
        """[Req: formal — stale column ban] Deprecated columns are blocked."""
        frame = _trade_frame()
        frame["ml_xa_dx_code"] = 0.0

        with pytest.raises(RuntimeError, match="stale/banned"):
            validate_input_schema(frame)

    def test_spec_7_build_csv_provenance_reads_manifest_hash(self, tmp_path: Path) -> None:
        """[Req: formal — provenance hash binding] Manifest hash parity is captured in provenance payload."""
        csv_path = tmp_path / "es_15m_core.csv"
        _write_small_csv(csv_path)
        manifest = {"sha256": _sha256(csv_path), "symbol": "ES", "timeframe": "15"}
        csv_path.with_suffix(".manifest.json").write_text(json.dumps(manifest))

        payload = build_csv_provenance(csv_path)

        assert payload["manifest_declared_csv_sha256"] == payload["csv_sha256"]
        assert payload["manifest_csv_sha256_matches"] is True

    def test_spec_8_apply_time_split_all_does_not_require_summary(self) -> None:
        """[Req: formal — split=all behavior] Full split bypasses summary dependency."""
        frame = pd.DataFrame(
            {
                "ts": [
                    "2026-01-01T00:00:00+00:00",
                    "2026-01-02T00:00:00+00:00",
                ],
                "value": [1.0, 2.0],
            }
        )

        split_df, source = apply_time_split(frame, split="all", ts_col="ts", summary=None)

        assert source == "all"
        assert len(split_df) == len(frame)

    @pytest.mark.parametrize("split", ["val", "oos"])
    def test_spec_9_non_all_splits_require_summary(self, split: str) -> None:
        """[Req: formal — split fail-closed policy] Non-all splits require summary split ranges."""
        frame = pd.DataFrame({"ts": ["2026-01-01T00:00:00+00:00"], "value": [1.0]})

        with pytest.raises(RuntimeError, match="requires run summary"):
            apply_time_split(frame, split=split, ts_col="ts", summary=None)

    @pytest.mark.parametrize(
        ("split", "expected_start"),
        [
            ("is", "2026-01-01T00:00:00+00:00"),
            ("train", "2026-01-01T00:00:00+00:00"),
            ("val", "2026-02-01T00:00:00+00:00"),
            ("oos", "2026-03-01T00:00:00+00:00"),
        ],
    )
    def test_spec_10_split_bounds_support_all_declared_split_keys(self, split: str, expected_start: str) -> None:
        """[Req: formal — split key mapping] is/train/val/oos keys map to expected summary ranges."""
        summary = _summary_with_ranges()

        ts_start, _ts_end = split_bounds_from_summary(summary, split)

        assert ts_start is not None
        assert ts_start.isoformat() == expected_start


class TestFitnessScenarios:
    def test_scenario_1_hash_drift_blocks_summary_binding(self, tmp_path: Path) -> None:
        """[Req: formal — scenario 1] Summary hash mismatch is surfaced as non-matching provenance."""
        csv_path = tmp_path / "es_15m_core.csv"
        _write_small_csv(csv_path)

        summary = {"csv_sha256": "deadbeef"}
        check = check_summary_csv_hash(csv_path, summary)

        assert check["checked"] is True
        assert check["matches"] is False

    def test_scenario_2_missing_split_ranges_fail_closed(self) -> None:
        """[Req: formal — scenario 2] Missing split ranges hard-fail non-all split selection."""
        frame = pd.DataFrame(
            {
                "ts": ["2026-01-01T00:00:00+00:00", "2026-03-01T00:00:00+00:00"],
                "value": [1.0, 2.0],
            }
        )

        with pytest.raises(RuntimeError, match="missing split_ranges_utc"):
            apply_time_split(frame, split="is", ts_col="ts", summary={})

    def test_scenario_3_tail_entries_are_dropped(self) -> None:
        """[Req: formal — scenario 3] Entries without the full forward horizon are dropped."""
        frame = _trade_frame(row_count=20, entry_idx=0)

        trades = build_trade_dataset(frame)

        assert trades.empty

    def test_scenario_4_same_bar_tp_sl_collision_is_pessimistic(self) -> None:
        """[Req: formal — scenario 4] Same-bar TP/SL collisions are loss outcomes with preserved touch flags."""
        frame = _trade_frame(
            row_count=30,
            entry_idx=0,
            tp_values=(101.0, 101.0, 101.0),
            custom_bars={1: (102.0, 95.0, 100.0)},
        )

        trades = build_trade_dataset(frame)

        assert not trades.empty
        assert (trades[LABEL_COL] == 0).all()
        assert (trades["tp_hit"] == 1).all()
        assert (trades["stop_hit"] == 1).all()

    def test_scenario_5_core_gate_rejects_stale_columns(self) -> None:
        """[Req: formal — scenario 5] Core frame validation fails on stale banned columns."""
        frame = _core_export_frame()
        frame["ml_xa_dx_code"] = 0.0

        with pytest.raises(RuntimeError, match="stale/banned"):
            core.validate_core_frame(frame, gate_mode="schema")

    def test_scenario_6_manifest_rejects_forbidden_lineage_tokens(self) -> None:
        """[Req: formal — scenario 6] Manifest payload fails when forbidden lineage tokens appear."""
        manifest = _valid_manifest()
        manifest["source_bars"] = "postgres://example.internal/es_core"

        with pytest.raises(RuntimeError, match="forbidden lineage tokens"):
            core.validate_manifest_contract(manifest)

    def test_scenario_7_near_dead_signal_is_rejected(self) -> None:
        """[Req: inferred — scenario 7] Near-dead continuous features fail quality gates."""
        frame = pd.DataFrame({"signal": [1.0] * 99 + [2.0]})

        with pytest.raises(RuntimeError, match="near-dead continuous signal"):
            validate_signal_health(frame, continuous_columns=["signal"], min_unique_ratio=0.05)

    def test_scenario_8_sparse_event_requires_whitelist(self) -> None:
        """[Req: inferred — scenario 8] Sparse event flags require explicit whitelist approval."""
        frame = pd.DataFrame(
            {
                "dense_signal": [float(i % 5) for i in range(100)],
                "sparse_event": [0] * 99 + [1],
            }
        )

        with pytest.raises(RuntimeError, match="sparse event flag requires whitelist"):
            validate_signal_health(
                frame,
                continuous_columns=["dense_signal"],
                sparse_event_columns=["sparse_event"],
                sparse_event_whitelist=set(),
                sparse_event_max_density=0.02,
            )

    def test_scenario_9_profile_mode_splits_by_timestamp_not_row(self) -> None:
        """[Req: formal — scenario 9] Profile mode splits keep each timestamp in a single split."""
        rows = []
        start = pd.Timestamp("2026-01-01T00:00:00Z")
        for idx in range(140):
            ts = start + pd.Timedelta(minutes=15 * idx)
            rows.append({"ts": ts, "profile_id": "pA"})
            rows.append({"ts": ts, "profile_id": "pB"})
        trades = pd.DataFrame(rows)

        train_pos, val_pos, test_pos = split_trade_positions(
            trades,
            train_frac=0.60,
            val_frac=0.20,
            embargo_bars=EMBARGO_BARS,
            label_horizon_bars=FORWARD_SCAN_BARS,
        )

        membership: dict[int, str] = {}
        for idx in train_pos:
            membership[int(idx)] = "train"
        for idx in val_pos:
            membership[int(idx)] = "val"
        for idx in test_pos:
            membership[int(idx)] = "test"

        ts_to_split: dict[pd.Timestamp, str] = {}
        for idx, row in trades.iterrows():
            split_name = membership.get(int(idx))
            if split_name is None:
                continue
            ts = pd.Timestamp(row["ts"])
            if ts not in ts_to_split:
                ts_to_split[ts] = split_name
            else:
                assert ts_to_split[ts] == split_name

        assert len(train_pos) > 0
        assert len(test_pos) > 0

    def test_scenario_10_export_schema_rejects_non_monotonic_timestamps(self) -> None:
        """[Req: formal — scenario 10] Export validation fails when timestamps are not monotonic."""
        frame = _core_export_frame(row_count=6)
        frame.loc[0, "ts"], frame.loc[1, "ts"] = frame.loc[1, "ts"], frame.loc[0, "ts"]

        with pytest.raises(RuntimeError, match="monotonically increasing"):
            core.validate_export_with_pandera(frame)


class TestBoundariesAndEdgeCases:
    def test_boundary_1_required_columns_detection(self) -> None:
        """[Req: inferred — validate_required_columns] Missing required fields are detected."""
        frame = pd.DataFrame({"ts": ["2026-01-01T00:00:00+00:00"]})

        with pytest.raises(RuntimeError, match="missing required columns"):
            validate_required_columns(frame, ["ts", "ml_entry_long_trigger"])

    def test_boundary_2_duplicate_real_signals_are_rejected(self) -> None:
        """[Req: inferred — validate_duplicate_real_signals] Duplicate non-whitelisted signals fail."""
        frame = pd.DataFrame(
            {
                "signal_a": [1.0, 2.0, 3.0],
                "signal_b": [1.0, 2.0, 3.0],
                "knob_length_ma": [50.0, 50.0, 50.0],
            }
        )

        with pytest.raises(RuntimeError, match="duplicate real signal columns"):
            validate_duplicate_real_signals(
                frame,
                signal_columns=["signal_a", "signal_b", "knob_length_ma"],
                allow_constant_columns={"knob_length_ma"},
            )

    def test_boundary_3_constant_whitelisted_knob_is_allowed(self) -> None:
        """[Req: inferred — validate_signal_health whitelist] Constant whitelisted knobs are permitted."""
        frame = pd.DataFrame({"knob": [50.0, 50.0, 50.0], "signal": [0.1, 0.2, 0.3]})

        validate_signal_health(
            frame,
            continuous_columns=["knob", "signal"],
            knob_constant_whitelist={"knob"},
        )

    def test_boundary_4_constant_non_whitelisted_signal_is_rejected(self) -> None:
        """[Req: inferred — validate_signal_health constant guard] Constant non-whitelisted continuous signals fail."""
        frame = pd.DataFrame({"signal": [1.0, 1.0, 1.0]})

        with pytest.raises(RuntimeError, match="constant continuous signal"):
            validate_signal_health(frame, continuous_columns=["signal"])

    def test_boundary_5_load_bars_requires_ts_or_ts_event_columns(self, tmp_path: Path) -> None:
        """[Req: inferred — load_bars defensive parser] Source files without ts fields fail fast."""
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("open,high,low,close,volume\n1,2,0,1,10\n")

        with pytest.raises(SystemExit, match="missing columns"):
            core.load_bars(bad_csv)

    def test_boundary_6_normalize_to_timeframe_resamples_subminute_clock(self) -> None:
        """[Req: inferred — normalize_to_timeframe branch] 1-minute bars are aggregated to target timeframe."""
        start = pd.Timestamp("2026-01-01T00:00:00Z")
        frame = pd.DataFrame(
            {
                "ts": [start + pd.Timedelta(minutes=i) for i in range(30)],
                "open": np.arange(30, dtype=float),
                "high": np.arange(30, dtype=float) + 1.0,
                "low": np.arange(30, dtype=float) - 1.0,
                "close": np.arange(30, dtype=float) + 0.5,
                "volume": np.ones(30, dtype=float),
            }
        )

        out = core.normalize_to_timeframe(frame, timeframe_min=15)

        assert len(out) == 2
        assert float(out.iloc[0]["open"]) == float(frame.iloc[0]["open"])
        assert float(out.iloc[0]["volume"]) == 15.0

    def test_boundary_7_normalize_to_timeframe_passthrough_for_coarse_clock(self) -> None:
        """[Req: inferred — normalize_to_timeframe branch] Coarse data bypasses resampling path."""
        start = pd.Timestamp("2026-01-01T00:00:00Z")
        frame = pd.DataFrame(
            {
                "ts": [start + pd.Timedelta(minutes=5 * i) for i in range(8)],
                "open": np.arange(8, dtype=float),
                "high": np.arange(8, dtype=float) + 1.0,
                "low": np.arange(8, dtype=float) - 1.0,
                "close": np.arange(8, dtype=float) + 0.5,
                "volume": np.ones(8, dtype=float),
            }
        )

        out = core.normalize_to_timeframe(frame, timeframe_min=5)

        assert len(out) == len(frame)
        assert out["ts"].iloc[0] == frame["ts"].iloc[0]

    def test_boundary_8_liquidity_recency_window_excludes_exact_boundary(self) -> None:
        """[Req: inferred — compute_liquidity_state recency guard] recency uses strict less-than boundary."""
        state = core.compute_liquidity_state(
            high=np.array([10.0, 11.0, 12.0, 10.0, 10.0]),
            low=np.array([9.0, 10.0, 8.0, 7.5, 8.0]),
            close=np.array([9.5, 10.5, 9.2, 7.8, 8.0]),
            lookback_bars=2,
            recency_bars=2,
        )

        assert state["recent_liq_bull"].tolist() == [False, False, True, True, False]

    def test_boundary_9_fib_reaction_without_touch_stays_neutral(self) -> None:
        """[Req: inferred — compute_fib_entry_reaction_features] No touch leaves neutral reaction code."""
        reaction = core.compute_fib_entry_reaction_features(
            open_=np.array([100.0, 101.0]),
            high=np.array([101.0, 102.0]),
            low=np.array([99.5, 100.5]),
            close=np.array([100.5, 101.5]),
            atr=np.array([2.0, 2.0]),
            direction=np.array([1, 1]),
            p_pivot=np.array([95.0, 95.0]),
            p_618=np.array([94.0, 94.0]),
            p_786=np.array([93.0, 93.0]),
        )

        assert reaction["fib_touch_level_code"].tolist() == [0.0, 0.0]
        assert reaction["fib_reaction_code"].tolist() == [0.0, 0.0]

    def test_boundary_10_split_bounds_rejects_unsupported_split_key(self) -> None:
        """[Req: inferred — split_bounds_from_summary guard] Unsupported split names fail immediately."""
        with pytest.raises(RuntimeError, match="Unsupported split"):
            split_bounds_from_summary(_summary_with_ranges(), "future")

    def test_boundary_11_payoff_array_falls_back_when_trade_prices_absent(self) -> None:
        """[Req: inferred — _resolve_payoff_arrays fallback] Missing price columns use deterministic fallback payoff."""
        trades = pd.DataFrame({"winner_tp_before_sl": [1, 0, 1]})

        win, loss = _resolve_payoff_arrays(trades, fallback_sl_pts=7.0, fallback_tp_pts=14.0, slippage_ticks=1.0)

        assert len(win) == 3
        assert len(loss) == 3
        assert np.allclose(win, 673.0)
        assert np.allclose(loss, -377.0)

    def test_boundary_12_resolve_predictor_path_prefers_entry_subdir_layout(self, tmp_path: Path) -> None:
        """[Req: inferred — _resolve_predictor_path layout support] entry/ predictor layout resolves correctly."""
        run_dir = tmp_path / "locked_run"
        entry_dir = run_dir / "entry"
        entry_dir.mkdir(parents=True)
        (entry_dir / "predictor.pkl").write_text("stub")

        resolved = _resolve_predictor_path(run_dir)

        assert resolved == entry_dir

    def test_boundary_13_suite_root_requires_all_heads(self, tmp_path: Path) -> None:
        """[Req: inferred — _is_suite_root guard] Suite root is true only when all head predictors exist."""
        run_dir = tmp_path / "suite_run"
        for head in SUITE_HEADS:
            head_dir = run_dir / head
            head_dir.mkdir(parents=True)
            (head_dir / "predictor.pkl").write_text("stub")

        assert _is_suite_root(run_dir) is True

        (run_dir / SUITE_HEADS[0] / "predictor.pkl").unlink()
        assert _is_suite_root(run_dir) is False

    def test_boundary_14_backfill_idempotence_detection_requires_full_payload(self) -> None:
        """[Req: inferred — backfill idempotence guard] Backfill detects already-populated provenance payloads."""
        complete = {
            "run_provenance": {"csv_sha256": "abc"},
            "split_ranges_utc": {"train": {}, "val": {}, "oos": {}},
            "csv_sha256": "abc",
        }
        incomplete = {
            "run_provenance": {"csv_sha256": "abc"},
            "split_ranges_utc": {"train": {}, "val": {}, "oos": {}},
            "csv_sha256": "",
        }

        assert backfill._already_backfilled(complete) is True
        assert backfill._already_backfilled(incomplete) is False

    def test_boundary_15_manifest_hash_validation_detects_drift(self, tmp_path: Path) -> None:
        """[Req: inferred — validate_manifest_hash] Hash drift between csv and manifest is rejected."""
        csv_path = tmp_path / "es_15m_core.csv"
        _write_small_csv(csv_path)
        manifest_path = csv_path.with_suffix(".manifest.json")
        manifest_path.write_text(json.dumps({"sha256": "deadbeef"}))

        with pytest.raises(RuntimeError, match="manifest hash mismatch"):
            validate_manifest_hash(csv_path, manifest_path)
