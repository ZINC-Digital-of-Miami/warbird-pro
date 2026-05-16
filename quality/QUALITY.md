# Quality Constitution: Warbird Pro V9 Core + Nexus Indicator

## Purpose

Warbird Pro V9 Core quality means the model pipeline stays contract-faithful from export to training to diagnostics, and fails closed whenever provenance, split boundaries, or schema assumptions drift. This project does not tolerate silent correctness loss; if evidence is ambiguous, execution must stop.

Deming applies here by building quality into context and gates, not post-hoc inspection: manifest validation, split-bound enforcement, and schema constraints must run before trusting output. Juran applies as fitness for use: a "passing" run is only useful if it binds to the exact CSV hash, enforces the 24-bar label horizon, and preserves feature contract compatibility. Crosby applies because upfront constraints are cheaper than post-run rework on corrupted labels, stale features, or split leakage.

Nexus indicator quality means the support/research oscillator remains footprint-faithful from TradingView `request.footprint()` through plots, data-window/export-only exports, exhaustion markers, and divergence labels. The Nexus lane must fail closed on unavailable footprint evidence, must not silently substitute OHLCV/candle proxies, and must never route indicator work through V9 Core assumptions unless the user explicitly requests a cross-lane comparison.

## Coverage Targets

| Subsystem                                                              | Target | Why                                                                                                                                  |
| ---------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| scripts/ag/train_v9_locked.py                                          | 92%    | Label construction and split logic determine ground-truth supervision. A subtle regression here contaminates all downstream metrics. |
| scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py | 90%    | ETL contract drift can silently alter feature semantics or source lineage before training starts.                                    |
| scripts/ag/v9_run_provenance.py                                        | 95%    | Hash and split binding is the fail-closed boundary between trusted and untrusted artifacts.                                          |
| scripts/ag/v9_data_quality_gate.py                                     | 95%    | Duplicate/near-dead/sparse-signal checks are the last line before low-information features poison training.                          |
| scripts/ag/backfill_v9_run_provenance.py                               | 90%    | Backfill must remain idempotent and parity-safe or it can rewrite historical evidence incorrectly.                                   |
| scripts/ag/monte_carlo_v9.py                                           | 80%    | Monte Carlo is downstream analytics, but payoff resolution and predictor path detection must remain correct for promotion decisions. |
| indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine | Static contract + Pine compile | Nexus quality is proven by real footprint API use, evidence plots, Pine compile, lint guards, and explicit no-V9 scope discipline. |
| quality/RUN_NEXUS_INDICATOR.md | 100% protocol coverage | The runbook is the canonical Nexus lane for indicator edits, footprint proof, verification gates, and reporting discipline. |

## Coverage Theater Prevention

The following do not count as quality in this repo:

- Asserting that CSV files exist without validating manifest hash parity.
- Asserting that a split command ran without checking split_ranges_utc boundaries were actually consumed.
- Testing only "TP-first wins" and skipping same-bar TP/SL conflict behavior.
- Running tests against synthetic schema shapes that omit real exported columns (especially ml_trade_tp1/2/3 and locked ML feature columns).
- Asserting that a model directory exists without checking predictor-path resolution rules.
- Accepting high test counts that never exercise fail-closed paths.
- Treating Nexus alert toggles as signal authority instead of plotted/evidence state.
- Claiming Nexus footprint proof from compile success alone without citing `request.footprint()`, `footprint.delta()`, `footprint.rows()`, and data-window/export-only `nexus_*` exports.
- Letting V9 Core assumptions, files, or settings contaminate Nexus-only indicator work.

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


## Nexus Indicator Lane Scenarios

### Scenario 11: Nexus Scope Contamination

**Requirement tag:** [Req: user-confirmed — Nexus-only operator correction 2026-05-14]

**What happened:** An assistant can drag V9 Core context into Nexus indicator work and then make irrelevant or misleading claims about the wrong lane.

**The requirement:** Nexus tasks must scope to `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine` and `quality/RUN_NEXUS_INDICATOR.md` unless the user explicitly requests a cross-lane comparison.

**How to verify:** Run `test_nexus_1_quality_lane_runbook_exists_and_scopes_work` in quality/test_functional.py.

---

### Scenario 12: Fake Footprint Substitution

**Requirement tag:** [Req: formal — AGENTS.md Nexus request.footprint evidence rule]

**What happened:** Volume-flow logic can look plausible if it uses candle body/wick or generic volume proxies, but that would invalidate the Nexus footprint research lane.

**The requirement:** Nexus volume, liquidity, delta, gas-out, and exported evidence must derive from TradingView footprint APIs: `request.footprint()`, `footprint.delta()`, `footprint.rows()`, and row total volume.

**How to verify:** Run `test_nexus_2_indicator_uses_real_footprint_api` in quality/test_functional.py and include line-cited proof in Nexus review reports.

---

### Scenario 13: Footprint Evidence Export Drift

**Requirement tag:** [Req: formal — AGENTS.md Nexus `nexus_fp_*` evidence only]

**What happened:** Data-window/export-only plots are easy to rename, remove, or accidentally demote to `display.none` because they do not affect visible chart appearance, but they are the export contract for footprint evidence.

**The requirement:** Data-window/export-only exports must preserve footprint availability, footprint quality (`nexus_fp_quality_ok`), bar delta, total volume, normalized cumulative delta, delta slope, bar delta ratio, delta direction, gas-out flags, mode minutes, signal tier, pivot span, regime score, oscillator momentum, volume-flow state, and raw/confirmed divergence flags unless downstream docs/tests are updated in the same change; the `nexus_*` plot lines must use `display.data_window`, not `display.none`, so TradingView CSV export exposes them.

**How to verify:** Run `test_nexus_3_export_only_footprint_plots_exist` in quality/test_functional.py.

---

### Scenario 14: Oscillator-Only Exhaustion Masquerading As Real Exhaustion

**Requirement tag:** [Req: user-confirmed — operator priority: volume, liquidity, footprints, real exhaustion]

**What happened:** Oscillator weakening can produce fatigue-looking marks without proving footprint sellers or buyers actually ran out of gas.

**The requirement:** Any signal described as real exhaustion must cite footprint gas-out/deceleration (`gasOutBull` / `gasOutBear`) or clearly label itself oscillator-only.

**How to verify:** Use the static review checklist in `quality/RUN_NEXUS_INDICATOR.md` and include the footprint proof table in the task report.

---

### Scenario 15: Divergence Without Footprint Confirmation

**Requirement tag:** [Req: user-confirmed — operator priority: real divergence]

**What happened:** Price/oscillator pivots can create divergence labels even when footprint/volume evidence is missing or allowed to silently pass.

**The requirement:** Divergence review must explicitly document whether `sfVolPassBull` / `sfVolPassBear` require footprint/volume confirmation or allow unavailable footprint to pass, and any change must be verified against the Nexus proof standard.

**How to verify:** Use the Nexus runbook's divergence checklist and Council of Three Nexus audit prompt.

---

### Scenario 16: Alerts Treated As Signal Authority

**Requirement tag:** [Req: user-confirmed — operator statement: alerts are not used]

**What happened:** Alert booleans can distract review toward notification behavior while the operator only cares about volume, liquidity, footprints, exhaustion, and divergence.

**The requirement:** Nexus quality reviews must treat alerts as non-authoritative UI conveniences. Signal truth comes from footprint-derived calculations and plotted/evidence state.

**How to verify:** Run `test_nexus_4_quality_protocols_reference_nexus_lane` in quality/test_functional.py and review alert logic only for non-interference.

---

### Scenario 17: Pine Verification Theater

**Requirement tag:** [Req: formal — Pine compilation rule + AGENTS.md Pine Verification]

**What happened:** An assistant can claim the indicator works after reading code or planning a patch without compiling Pine or running guards.

**The requirement:** Nexus Pine changes require Pine facade compile, pine lint, contamination/no-TV-force guards, and build output before completion claims.

**How to verify:** Run `test_nexus_5_runbook_requires_real_verification_gates` in quality/test_functional.py and execute the commands in `quality/RUN_NEXUS_INDICATOR.md` for Pine edits.

---

### Scenario 18: Request/Output Budget Drift

**Requirement tag:** [Req: formal — AGENTS.md Pine budget rules]

**What happened:** Adding visible or data-window/export-only plots, alertconditions, or additional footprint/security requests can silently exceed TradingView resource budgets or reduce available headroom.

**The requirement:** Every Nexus Pine edit must price output-consuming calls and request paths before and after the change.

**How to verify:** Run `./scripts/guards/pine-lint.sh indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine` and report request/output counts.

---

### Scenario 19: Footprint-Quality Fail-Closed Contract

**Requirement tag:** [Req: formal — Nexus footprint-quality checkpoint 2026-05-15]

**What happened:** `fpFlowAvailable` proves a footprint row exists on the current bar, but exhaustion and divergence need enough continuous footprint history to compute normalized cumulative delta, slope, and bar-delta ratio without gap-contaminated state. Alerts were also removed because the operator does not use them and they are not signal authority.

**The requirement:** `fpQualityOk` must gate delta direction, gas-out, fatigue, Tier 1/Tier 2 signal tier, and divergence confirmation when volume confirmation is enabled. Data-window/export-only exports must include `nexus_fp_quality_ok` and remain exportable with `display.data_window`. The Pine file must not contain `GRP_ALERT`, `alertcondition(`, or `alert(` after alert-surface removal.

**How to verify:** Run `test_nexus_6_footprint_quality_gates_exhaustion_and_divergence`, `test_nexus_7_alert_surface_removed_and_cross_dots_ui_only`, and `test_nexus_8_signal_tier_uses_only_footprint_gated_signals` in `quality/test_functional.py`, then run the full Nexus Pine compile/lint/guard/build lane.

---

### Scenario 20: Lag And False-Signal Diagnostic Export Contract

**Requirement tag:** [Req: user-confirmed — operator priority: real accuracy, real delta, real alpha]

**What happened:** The first 15m diagnostic showed lag/false-signal concerns and proved that a human cannot tune all Nexus lengths/options by hand. The export lacked separate raw/confirmed divergence fields, pivot-confirmation lag, and supporting state columns needed to diagnose false positives one component at a time.

**The requirement:** Nexus must export raw divergence flags, confirmed divergence flags, `nexus_pivot_span`, `nexus_regime_score`, `nexus_osc_momentum`, and `nexus_vf_calc` as `display.data_window` plots before heavy sequential training. These exports must not alter visible signal behavior and must remain Nexus-only.

**How to verify:** Run `test_nexus_10_lag_false_signal_diagnostic_exports_exist` in `quality/test_functional.py`, price Pine output budget with `pine-lint.sh`, and re-export TradingView data before any heavy model run.

---

### Scenario 21: Nexus 15m Pre-Training Label Audit Gate

**Requirement tag:** [Req: user-confirmed — heavy training must be sequential and real-data only]

**What happened:** The expanded export showed usable footprint evidence, but the first naive split placed most footprint-quality rows outside train. Starting a heavy model without a manifest-backed dataset, label audit, leakage exclusions, and footprint-quality split boundaries would waste hours and risk false confidence.

**The requirement:** Before any heavy Nexus 15m model run, build the isolated `warbird_nexus_ml_rsi_15m` dataset from a TradingView/Pine export, write a manifest, mark incomplete future labels as missing, split chronologically over the footprint-quality subset with embargo, and publish a pre-training label audit. V9 files, trainers, exports, and model artifacts must not be touched.

**How to verify:** Run `test_nexus_11_isolated_15m_builder_pretraining_gate_exists` in `quality/test_functional.py`, execute `scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/build_nexus_15m_dataset.py`, and inspect `reports/pretrain_label_audit.md` before training.

---

### Scenario 22: Deferred Nexus Meter Plan Preservation During Active Training

**Requirement tag:** [Req: user-confirmed — preserve Nexus live-meter/tuning governance now, implement after run]

**What happened:** The operator approved preserving the post-training Nexus live pressure/gas/confidence meter roadmap and tuning-path governance in the workbook, while explicitly forbidding disruption to active training and in-flight artifacts.

**The requirement:** During active runs, changes are docs-only and must preserve:

- freeze boundaries for Pine + active training scripts
- three-path tuning routing (Python Optuna vs CDP TV auto-tune vs manual deep backtest)
- TC skill mapping for each planned Pine implementation surface
- post-run resume gates and verification requirements

No active training surfaces may be changed under this scenario.

**How to verify:**

- Confirm deferred hold section exists in `quality/RUN_NEXUS_INDICATOR.md`.
- Confirm section includes tuning-path decision lock and TC skill enforcement matrix.
- Confirm no edits were made to active Nexus training/Pine surfaces in the defer window.

## AI Session Quality Discipline

1. Read quality/QUALITY.md before editing V9 Core training, ETL, provenance, or diagnostics code.
2. Treat non-`all` split execution without split_ranges_utc as invalid by default.
3. Run new functional tests plus touched subsystem tests before completion.
4. Fail closed on manifest/source/hash ambiguity; do not auto-heal contracts silently.
5. Keep requirement tags in new scenarios/tests: `[Req: formal|user-confirmed|inferred — source]`.
6. Add or update tests when introducing new defensive checks.
7. Record unresolved inferred requirements for human confirmation rather than presenting them as formal truth.
8. Read quality/RUN_NEXUS_INDICATOR.md before any Nexus indicator work.
9. For Nexus work, do not mention, inspect, or modify V9 surfaces unless the user explicitly requests a cross-lane comparison.
10. Treat Nexus alerts as non-authoritative; evidence comes from footprint calculations and plots.
11. Do not claim Nexus footprint behavior is working without Pine compile/guard evidence for Pine edits or static Nexus tests for quality-doc-only changes.
12. Treat `fpQualityOk` as the current Nexus fail-closed proof gate for footprint-derived signal tiers, gas-out, fatigue, and divergence confirmation.
13. Before heavy Nexus training, verify lag/false-signal diagnostic exports are present so settings can be tested sequentially instead of guessed manually.
14. Do not launch heavy Nexus 15m training until the isolated dataset manifest and pre-training label audit exist and the footprint-quality split is sane.

## The Human Gate

Human approval is required for:

- Promoting any run artifact to production/live alert behavior.
- Changing Pine indicator behavior or live TradingView operations.
- Accepting deviations from source-kind, split-bound, or provenance contracts.
- Redefining threshold policies (for example sparse density floors, strict entry floors) without operator signoff.
- Resolving disagreements between formal requirements and inferred code behavior.
- Changing Nexus footprint, exhaustion, divergence, data-window/export-only export, or TradingView live behavior.
- Treating unavailable Nexus footprint evidence as acceptable for real exhaustion or divergence without explicit operator approval.
