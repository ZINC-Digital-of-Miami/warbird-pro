# Code Review Protocol: Warbird Pro V9 Core + Nexus Indicator

## Bootstrap (Read First)

Before reviewing any code, read in this order:

1. quality/QUALITY.md
2. AGENTS.md
3. CLAUDE.md
4. docs/MASTER_PLAN.md
5. docs/contracts/pine_indicator_ag_contract.md
6. scripts/ag/train_v9_locked.py
7. scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py
8. scripts/ag/v9_run_provenance.py

### Nexus Indicator Bootstrap

For Nexus reviews, read these additional files before forming findings:

1. quality/RUN_NEXUS_INDICATOR.md
2. indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine
3. AGENTS.md Nexus hard rules and Pine verification sections

Nexus reviews are scoped to the indicator lane. Do not review V9 trainer/ETL/model surfaces unless the user explicitly requests a cross-lane review.

## What to Check

### Focus Area 1: Label and Outcome Contract

**Where:** scripts/ag/train_v9_locked.py (`build_trade_dataset`, `validate_input_schema`)

**What:**

- 24-bar forward horizon constants remain synchronized (`FORWARD_SCAN_BARS`, `MIN_FUTURE_BARS`, `EMBARGO_BARS`).
- Same-bar TP/SL collision still resolves pessimistically (`winner_tp_before_sl=0`) with touch flags preserved.
- Required input columns still include `ml_trade_tp1`, `ml_trade_tp2`, `ml_trade_tp3`.

**Why:** Drift here changes supervision truth and invalidates all downstream quality claims.

### Focus Area 2: Split and Provenance Binding

**Where:** scripts/ag/v9_run_provenance.py (`check_summary_csv_hash`, `apply_time_split`, `split_bounds_from_summary`)

**What:**

- Non-`all` splits hard-fail without summary split ranges.
- Hash checks always compare against current CSV bytes.
- Split key mapping (`is/train/val/oos`) remains consistent.

**Why:** This is the main fail-closed gate preventing OOS leakage and artifact drift.

### Focus Area 3: Core ETL Schema Lock

**Where:** scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py (`validate_core_frame`, `validate_export_with_pandera`)

**What:**

- Stale/banned columns remain blocked.
- Locked feature surface remains aligned to train_v9_locked.ML_FEATURES.
- Pandera monotonic timestamp enforcement remains active.

**Why:** ETL schema drift can silently alter model behavior while tests appear green.

### Focus Area 4: Manifest Governance

**Where:** scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py (`validate_manifest_contract`, `write_outputs`)

**What:**

- `source_kind` must begin with `DATABENTO_`.
- Forbidden lineage token checks are still active (`postgres`, `psycopg2`, `ag_training`, `local_warehouse`, `optuna`).
- `feature_count_locked` equals `len(ML_FEATURES)`.

**Why:** Misdeclared lineage undermines trust in every downstream report.

### Focus Area 5: Signal Health Gates

**Where:** scripts/ag/v9_data_quality_gate.py

**What:**

- Duplicate real-signal detection still rejects non-whitelisted clones.
- Near-dead and constant continuous signal checks still hard-fail.
- Sparse event flags still require explicit whitelist.

**Why:** Low-information feature surfaces can pass silently and poison training quality.

### Focus Area 6: Backfill Integrity and Idempotence

**Where:** scripts/ag/backfill_v9_run_provenance.py

**What:**

- Backfill refuses writes on row-parity mismatch.
- Backfill remains idempotent unless `--force` is provided.
- Backup summary file behavior remains non-destructive.

**Why:** Backfill edits historical summaries; regressions can rewrite evidence incorrectly.

### Focus Area 7: Monte Carlo Predictor Layout and Payoff Path

**Where:** scripts/ag/monte_carlo_v9.py (`_resolve_predictor_path`, `_is_suite_root`, `_resolve_payoff_arrays`)

**What:**

- Predictor path resolution supports both root and `entry/` layouts.
- Suite-root detection still requires all heads.
- Payoff fallback behavior remains deterministic when trade prices are absent.

**Why:** Wrong layout/payout assumptions create misleading robustness results.

### Focus Area 8: Contract Drift Across Docs and Code

**Where:** quality/QUALITY.md, AGENTS.md, CLAUDE.md, scripts/ag/train_v9_locked.py

**What:**

- Feature counts and split contracts match code constants.
- Quality scenarios still map to executable tests.
- Requirement tags are preserved for inferred vs formal requirements.

**Why:** Documentation drift causes future AI sessions to enforce the wrong truth.


### Focus Area 9: Nexus Scope And Authority

**Where:** quality/RUN_NEXUS_INDICATOR.md, indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine

**What:**

- Nexus work stays scoped to the Nexus file and runbook.
- V9 Core assumptions are not used as Nexus authority.
- Alerts are documented as non-authoritative for signal truth.

**Why:** Scope contamination was the direct assistant-side failure this lane is designed to prevent.

### Focus Area 10: Real Footprint Acquisition

**Where:** indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine (`request.footprint`, `footprint.delta`, `footprint.rows`)

**What:**

- `request.footprint()` remains the source of footprint evidence.
- Bar delta comes from `footprint.delta()`.
- Row liquidity/volume comes from `footprint.rows()` and `volume_row.total_volume()`.
- No candle body/wick, local CSV, Databento OHLCV, or generic `volume` proxy replaces footprint evidence.

**Why:** Nexus tuning must use TradingView/Pine footprint evidence only.

### Focus Area 11: Footprint Availability And Fail-Closed Gates

**Where:** indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine (`fpAvailable`, `fpFlowAvailable`, `fpTotalVolume`, `normCumDelta`, `deltaSlope`, `deltaDir`)

**What:**

- `fpFlowAvailable` cannot be true with missing delta, missing total volume, or non-positive total volume.
- Delta normalization and slope use safe divisors and unavailable-state handling.
- Footprint-backed signals fail closed when footprint is unavailable.

**Why:** A missing-footprint chart must not produce fake footprint proof.

### Focus Area 12: Volume Flow, Liquidity, And Gas-Out Exhaustion

**Where:** indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine (VNVF block, `gasOutBull`, `gasOutBear`, fatigue/exhaustion markers)

**What:**

- Signed volume flow is derived from footprint delta and footprint total volume.
- Gas-out conditions represent signed cumulative delta deceleration.
- Any marker described as real exhaustion is footprint-backed or explicitly labeled oscillator-only.

**Why:** The operator priority is volume, liquidity, footprints, and real exhaustion rather than generic oscillator crosses.

### Focus Area 13: Divergence Integrity

**Where:** indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine (pivot/divergence block, `sfVolPassBull`, `sfVolPassBear`)

**What:**

- Pivot age, oscillator swing, price swing, and volume/footprint confirmation semantics are explicit.
- If footprint confirmation is required, unavailable footprint cannot silently pass.
- Labels cite true regular/hidden divergence behavior rather than alert behavior.

**Why:** Divergence labels are visible and persuasive; false confirmation creates bad trade context.

### Focus Area 14: Plot And Export Contract

**Where:** indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine (visible plots, data-window/export-only `nexus_*` plots)

**What:**

- Visible plots still match the settings that control them.
- Data-window/export-only evidence plots still include footprint availability, footprint quality, bar delta, total volume, normalized delta, slope, ratio, direction, gas-out flags, mode minutes, signal tier, pivot span, regime score, oscillator momentum, volume-flow state, and raw/confirmed divergence flags.
- Any plot rename/removal is documented in the same change.

**Why:** Data-window/export-only plots are the CSV/evidence contract for Nexus research.

### Focus Area 15: Pine Verification And Resource Budget

**Where:** indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine, scripts/guards/pine-lint.sh

**What:**

- Pine facade compile output is captured after Pine edits.
- Pine lint reports output/request counts.
- Additional plot/alert/request paths are budgeted before merge.

**Why:** TradingView resource limits can break an otherwise plausible indicator.

### Focus Area 16: Nexus Tuning-Path Governance During Deferred Hold

**Where:** quality/RUN_NEXUS_INDICATOR.md (Deferred Hold section), Nexus tuning scripts and Pine changesets when resumed

**What:**

- TV-only footprint/exhaustion knobs are not routed to reconstruction-only Python tuning.
- The selected tuning path is explicitly documented (Optuna Python, CDP TV auto-tune, or manual deep backtest).
- During active-run defer windows, only docs/workbook updates occur; no active training/Pine mutation occurs.
- TC skill mapping is present for the planned Pine surface before implementation resumes.

**Why:** Mixing tuning paths creates non-reproducible champions and wastes compute with false optimization confidence.

## Guardrails

- Line numbers are mandatory. No line number, no finding.
- Read function bodies, not just signatures.
- If unsure, classify as QUESTION, not BUG.
- Grep before claiming a requirement is missing.
- Do not suggest style-only refactors. Flag only correctness, reliability, or contract defects.
- For Nexus findings, cite `quality/RUN_NEXUS_INDICATOR.md` and the exact Pine line numbers.
- Do not use V9 Core contracts to judge Nexus behavior unless the user explicitly requested cross-lane analysis.

## Output Format

Save findings to quality/code_reviews/YYYY-MM-DD-reviewer.md.

For each reviewed file:

### path/to/file.py

- **Line NNN:** [BUG | QUESTION | INCOMPLETE] Description.
- **Expected:** Requirement or contract expectation.
- **Actual:** Observed behavior.
- **Impact:** Why this can break production trust or correctness.

### Summary

- Total findings by severity (`critical`, `major`, `minor`)
- Files reviewed with zero findings
- Recommendation: `SHIP IT`, `FIX FIRST`, or `NEEDS DISCUSSION`

## Phase 2: Regression Tests For Confirmed BUG Findings

After review findings are produced:

1. Create or update quality/test_regression.py.
2. Add one regression test per BUG finding using real call paths and minimal fixtures.
3. Include finding trace in each test docstring, for example: `[BUG from 2026-05-13-reviewer.md line 42]`.
4. Run:

```bash
./.venv/bin/python -m pytest quality/test_regression.py -v
```

5. Record confirmation table in quality/code_reviews/YYYY-MM-DD-reviewer.md:

| Finding | Regression Test | Result                              | Confirmed                      |
| ------- | --------------- | ----------------------------------- | ------------------------------ |
| ...     | ...             | FAIL (expected) / PASS (unexpected) | YES / NO / NEEDS INVESTIGATION |

## Execution Notes

- Keep review batches small (one subsystem per pass).
- If one pass creates many BUG findings, run regression tests before reviewing another subsystem.
- For Pine-related diffs, defer to AGENTS/CLAUDE hard-rule verification gates in addition to this protocol.
- For Nexus-related review, follow quality/RUN_NEXUS_INDICATOR.md and include the footprint proof table before recommending `SHIP IT`.
