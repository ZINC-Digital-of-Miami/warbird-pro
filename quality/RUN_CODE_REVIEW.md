# Code Review Protocol: Warbird Pro V9 Core

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

## Guardrails

- Line numbers are mandatory. No line number, no finding.
- Read function bodies, not just signatures.
- If unsure, classify as QUESTION, not BUG.
- Grep before claiming a requirement is missing.
- Do not suggest style-only refactors. Flag only correctness, reliability, or contract defects.

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
