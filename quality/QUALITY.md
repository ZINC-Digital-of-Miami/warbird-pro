# Quality Constitution: Warbird Pro V9 Core

## Purpose

Warbird Pro V9 Core quality means the model pipeline stays contract-faithful from export to training to diagnostics, and fails closed whenever provenance, split boundaries, or schema assumptions drift. This project does not tolerate silent correctness loss; if evidence is ambiguous, execution must stop.

Deming applies here by building quality into context and gates, not post-hoc inspection: manifest validation, split-bound enforcement, and schema constraints must run before trusting output. Juran applies as fitness for use: a "passing" run is only useful if it binds to the exact CSV hash, enforces the 24-bar label horizon, and preserves feature contract compatibility. Crosby applies because upfront constraints are cheaper than post-run rework on corrupted labels, stale features, or split leakage.

## Coverage Targets

| Subsystem                                                              | Target | Why                                                                                                                                  |
| ---------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| scripts/ag/train_v9_locked.py                                          | 92%    | Label construction and split logic determine ground-truth supervision. A subtle regression here contaminates all downstream metrics. |
| scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py | 90%    | ETL contract drift can silently alter feature semantics or source lineage before training starts.                                    |
| scripts/ag/v9_run_provenance.py                                        | 95%    | Hash and split binding is the fail-closed boundary between trusted and untrusted artifacts.                                          |
| scripts/ag/v9_data_quality_gate.py                                     | 95%    | Duplicate/near-dead/sparse-signal checks are the last line before low-information features poison training.                          |
| scripts/ag/backfill_v9_run_provenance.py                               | 90%    | Backfill must remain idempotent and parity-safe or it can rewrite historical evidence incorrectly.                                   |
| scripts/ag/monte_carlo_v9.py                                           | 80%    | Monte Carlo is downstream analytics, but payoff resolution and predictor path detection must remain correct for promotion decisions. |

## Coverage Theater Prevention

The following do not count as quality in this repo:

- Asserting that CSV files exist without validating manifest hash parity.
- Asserting that a split command ran without checking split_ranges_utc boundaries were actually consumed.
- Testing only "TP-first wins" and skipping same-bar TP/SL conflict behavior.
- Running tests against synthetic schema shapes that omit real exported columns (especially ml_trade_tp1/2/3 and locked ML feature columns).
- Asserting that a model directory exists without checking predictor-path resolution rules.
- Accepting high test counts that never exercise fail-closed paths.

## Fitness-to-Purpose Scenarios

### Scenario 1: Hash-Bound Artifact Drift

**Requirement tag:** [Req: formal — AGENTS.md contract-first + v9_run_provenance hash checks]

**What happened:** The architecture allows a summary file to outlive its training CSV. If csv_sha256 in summary metadata no longer matches the live CSV, downstream SHAP/MC analysis can appear valid while scoring the wrong dataset.

**The requirement:** Any run-summary hash mismatch must be surfaced and block trust promotion.

**How to verify:** Run `test_scenario_1_hash_drift_blocks_summary_binding` in quality/test_functional.py.

---

### Scenario 2: Split-Range Amputation

**Requirement tag:** [Req: formal — scripts/ag/v9_run_provenance.py apply_time_split fail-closed contract]

**What happened:** Without split_ranges_utc, consumers can accidentally score all rows or wrong windows while claiming OOS validation.

**The requirement:** Non-`all` splits must hard-fail when summary split ranges are absent.

**How to verify:** Run `test_scenario_2_missing_split_ranges_fail_closed` in quality/test_functional.py.

---

### Scenario 3: Tail-Window Contamination

**Requirement tag:** [Req: formal — scripts/ag/train_v9_locked.py FORWARD_SCAN_BARS/MIN_FUTURE_BARS]

**What happened:** Entries near the dataset tail cannot observe a full 24-bar future window. Keeping them creates biased labels that appear legitimate.

**The requirement:** Trades with fewer than 24 future bars must be dropped, not labeled.

**How to verify:** Run `test_scenario_3_tail_entries_are_dropped` in quality/test_functional.py.

---

### Scenario 4: Same-Bar TP/SL Ambiguity

**Requirement tag:** [Req: formal — scripts/ag/train_v9_locked.py same-bar pessimistic rule]

**What happened:** Intrabar order is unknown when TP and SL are touched in the same bar. Treating these as wins inflates precision and creates false champion confidence.

**The requirement:** Same-bar TP/SL collisions must set winner_tp_before_sl=0 while preserving touch-event labels.

**How to verify:** Run `test_scenario_4_same_bar_tp_sl_collision_is_pessimistic` in quality/test_functional.py.

---

### Scenario 5: Feature-Contract Drift

**Requirement tag:** [Req: formal — scripts/ag/train_v9_locked.py ML_FEATURES lock + validate_core_frame stale bans]

**What happened:** Reintroduced stale columns (for example ml_xa_dx_code) or missing locked features can silently change semantics while pipelines still run.

**The requirement:** Core-frame validation must reject stale/banned columns and missing locked feature surfaces.

**How to verify:** Run `test_scenario_5_core_gate_rejects_stale_columns` in quality/test_functional.py.

---

### Scenario 6: Source-Lineage Contamination

**Requirement tag:** [Req: formal — build_core_dataset validate_manifest_contract DATABENTO + forbidden lineage tokens]

**What happened:** If manifests reference non-approved source kinds or forbidden lineage tokens, downstream claims about source-of-truth become untrustworthy.

**The requirement:** Manifest validation must reject non-DATABENTO source kinds and forbidden lineage tokens.

**How to verify:** Run `test_scenario_6_manifest_rejects_forbidden_lineage_tokens` in quality/test_functional.py.

---

### Scenario 7: Silent Signal Death

**Requirement tag:** [Req: inferred — scripts/ag/v9_data_quality_gate.py validate_signal_health near-dead checks]

**What happened:** A feature can remain technically present while collapsing to one dominant value, yielding low-information training that looks normal at a glance.

**The requirement:** Near-dead continuous signals must fail quality gates unless explicitly whitelisted.

**How to verify:** Run `test_scenario_7_near_dead_signal_is_rejected` in quality/test_functional.py.

---

### Scenario 8: Sparse Event Abuse

**Requirement tag:** [Req: inferred — scripts/ag/v9_data_quality_gate.py sparse_event_whitelist contract]

**What happened:** Ultra-sparse event flags can pass unnoticed and contribute no robust learning signal while still increasing feature surface complexity.

**The requirement:** Sparse event features below density floor require explicit whitelist approval.

**How to verify:** Run `test_scenario_8_sparse_event_requires_whitelist` in quality/test_functional.py.

---

### Scenario 9: Cross-Profile Time Leakage

**Requirement tag:** [Req: formal — scripts/ag/train_v9_locked.py split_trade_positions timestamp-group split]

**What happened:** In ma-grid profile mode, the same timestamp appears across profiles. Row-wise splits can leak the same market instant into train and validation.

**The requirement:** Splitting must be driven by unique timestamps so each timestamp belongs to exactly one split.

**How to verify:** Run `test_scenario_9_profile_mode_splits_by_timestamp_not_row` in quality/test_functional.py.

---

### Scenario 10: Export Ordering Corruption

**Requirement tag:** [Req: formal — build_core_dataset validate_export_with_pandera monotonic ts]

**What happened:** Non-monotonic timestamp ordering can preserve row count while invalidating time-series assumptions used by labeling and split logic.

**The requirement:** Export validation must fail when ts is not monotonically increasing.

**How to verify:** Run `test_scenario_10_export_schema_rejects_non_monotonic_timestamps` in quality/test_functional.py.

## AI Session Quality Discipline

1. Read quality/QUALITY.md before editing V9 Core training, ETL, provenance, or diagnostics code.
2. Treat non-`all` split execution without split_ranges_utc as invalid by default.
3. Run new functional tests plus touched subsystem tests before completion.
4. Fail closed on manifest/source/hash ambiguity; do not auto-heal contracts silently.
5. Keep requirement tags in new scenarios/tests: `[Req: formal|user-confirmed|inferred — source]`.
6. Add or update tests when introducing new defensive checks.
7. Record unresolved inferred requirements for human confirmation rather than presenting them as formal truth.

## The Human Gate

Human approval is required for:

- Promoting any run artifact to production/live alert behavior.
- Changing Pine indicator behavior or live TradingView operations.
- Accepting deviations from source-kind, split-bound, or provenance contracts.
- Redefining threshold policies (for example sparse density floors, strict entry floors) without operator signoff.
- Resolving disagreements between formal requirements and inferred code behavior.
