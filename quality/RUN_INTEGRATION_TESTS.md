# Integration Test Protocol: Warbird Pro V9 Core + Nexus Indicator

## Working Directory

Run all commands from the repository root using relative paths only. Do not use absolute-path `cd` commands.

## Safety Constraints

- Do not edit source files while executing this protocol.
- Write outputs only under quality/results/.
- If any gate fails, stop promotion decisions and report findings.
- Do not run TradingView mutation operations (`pine_save`, `pine_set_source`, `tv_launch`) from this protocol.
- For Nexus Pine edits, use Pine facade compile and local guards only unless the user explicitly approves live TradingView operations.
- Nexus integration checks must not launch training or route through V9 artifacts.

## Pre-Flight Check

Run these checks first:

```bash
./.venv/bin/python --version
[ -f scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.csv ]
[ -f scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.manifest.json ]
[ -d models/warbird_pro_v9/locked_20260512_083803 ]
./.venv/bin/python scripts/ag/tv_connection_doctor.py --json > quality/results/tv_doctor_preflight.json
```

Pass criteria:

- Python interpreter resolves from `.venv`.
- Export CSV and manifest exist.
- At least one locked predictor artifact exists.
- `tv_connection_doctor` returns valid JSON (read-only health signal).

## Field Reference Table (Schema-Copied)

This table is copied from schema definitions and consumed fields in code. Use these exact field names in all quality gates.

### Schema A: Core Export Manifest Contract

Source: scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py (`validate_manifest_contract`)

| Field                   | Type    | Constraints                             |
| ----------------------- | ------- | --------------------------------------- |
| repo_commit             | string  | required, non-null                      |
| symbol                  | string  | required, non-null                      |
| symbol_root             | string  | required, non-null                      |
| timeframe               | string  | required, non-null                      |
| trigger_family          | string  | required, non-null                      |
| source_kind             | string  | required, must start with `DATABENTO_`  |
| source_bars             | string  | required, non-null                      |
| label_column            | string  | required, non-null                      |
| feature_count_locked    | integer | required, must equal `len(ML_FEATURES)` |
| row_count               | integer | required, `>= 1`                        |
| entry_long_count        | integer | required, `>= 0`                        |
| entry_short_count       | integer | required, `>= 0`                        |
| profiling_report_path   | string  | required, non-null                      |
| profiling_rows_profiled | integer | required, `>= 1`                        |

### Schema B: Run Summary Provenance/Split Consumed Fields

Source: scripts/ag/v9_run_provenance.py (`_summary_csv_sha256`, `split_bounds_from_summary`)

| Field                           | Type            | Constraints                                                   |
| ------------------------------- | --------------- | ------------------------------------------------------------- |
| run_provenance.csv_sha256       | string          | optional primary hash source; if present, must match CSV hash |
| csv_sha256                      | string          | fallback hash source when run_provenance hash absent          |
| split_ranges_utc.train.ts_start | datetime string | required for non-`all` split operations                       |
| split_ranges_utc.train.ts_end   | datetime string | required for non-`all` split operations                       |
| split_ranges_utc.val.ts_start   | datetime string | required for non-`all` split operations                       |
| split_ranges_utc.val.ts_end     | datetime string | required for non-`all` split operations                       |
| split_ranges_utc.oos.ts_start   | datetime string | required for non-`all` split operations                       |
| split_ranges_utc.oos.ts_end     | datetime string | required for non-`all` split operations                       |

### Schema C: Export Label-Policy Columns

Source: scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py (`required_label_policy`)

| Field                  | Type                    | Constraints        |
| ---------------------- | ----------------------- | ------------------ |
| ml_entry_long_trigger  | float/bool-like numeric | required in export |
| ml_entry_short_trigger | float/bool-like numeric | required in export |
| ml_trade_entry         | float                   | required in export |
| ml_trade_stop          | float                   | required in export |
| ml_trade_tp1           | float                   | required in export |
| ml_trade_tp2           | float                   | required in export |
| ml_trade_tp3           | float                   | required in export |

## Test Matrix

| #   | Check                                     | Method                                                                  | Pass Criteria                                               |
| --- | ----------------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------- |
| 1   | Data quality gate contracts               | `pytest tests/ag/test_v9_data_quality_gate.py`                          | All tests pass                                              |
| 2   | Provenance/split contracts                | `pytest tests/ag/test_v9_run_provenance.py`                             | All tests pass                                              |
| 3   | Core pandera/manifest contracts           | `pytest tests/ag/test_v9_core_pandera_contract.py`                      | All tests pass                                              |
| 4   | Quality functional suite                  | `pytest quality/test_functional.py`                                     | All tests pass, zero errors                                 |
| 5   | Trainer validate-only smoke               | `train_v9_locked.py --validate-only --smoke-ok`                         | Exits 0, prints split/label summary                         |
| 6   | Monte Carlo predictor wiring smoke        | `monte_carlo_v9.py --n-paths 10`                                        | Exits 0, writes metrics json                                |
| 7   | Manifest hash verification                | Inline Python check using `validate_manifest_hash`                      | No mismatch exception                                       |
| 8   | Summary hash and split-range verification | Inline Python check using `check_summary_csv_hash` + `apply_time_split` | Hash matches and split source is `summary_split_ranges_utc` |
| 9   | Full repo regression safety               | `pytest tests/ag tests/duckdb_local`                                    | No regressions in existing tests                            |
| 10  | Nexus quality lane static contracts       | `pytest quality/test_functional.py -k nexus`                            | Nexus runbook, footprint API, hidden export, and protocol-link tests pass |
| 11  | Nexus Pine facade compile                 | Pine facade `translate_light` request for Nexus file                    | Compiler response contains no Pine errors                   |
| 12  | Nexus Pine lint/resource budget           | `./scripts/guards/pine-lint.sh indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine` | Output/request counts are reported and no hard errors occur |
| 13  | Nexus contamination/no-TV-force guards    | `./scripts/guards/check-contamination.sh` + `./scripts/guards/check-no-tv-force.sh` | No contamination or banned TV recovery paths detected       |


## Nexus Indicator Verification Lane

Use this lane whenever the task touches Nexus quality docs, Nexus tests, or `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`.

### Nexus Docs/Tests Only

```bash
./.venv/bin/python -m pytest quality/test_functional.py -k nexus -q
npm run build
```

Pass criteria:

- Nexus static contract tests pass with zero errors.
- Build completes successfully.
- No Pine verification claim is made because Pine was not changed.

### Nexus Pine Edit Gate

```bash
curl -s -X POST "https://pine-facade.tradingview.com/pine-facade/translate_light?user_name=admin&v=3" \
  -H 'Referer: https://www.tradingview.com/' \
  -F "source=<indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine" > quality/results/nexus-pine-compile.json
./scripts/guards/pine-lint.sh indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine > quality/results/nexus-pine-lint.log
./scripts/guards/check-contamination.sh > quality/results/nexus-contamination.log
./scripts/guards/check-no-tv-force.sh > quality/results/nexus-no-tv-force.log
npm run build > quality/results/nexus-npm-build.log 2>&1
```

Pass criteria:

- Pine facade returns no compile errors.
- Pine lint reports output/request counts and no hard failures.
- Contamination and no-TV-force guards pass.
- Build passes.
- Final report includes the footprint proof table from `quality/RUN_NEXUS_INDICATOR.md`.

### Nexus Footprint Proof Artifacts

For any Pine edit, save or report:

| Artifact | Required Content |
| -------- | ---------------- |
| Compile output | Raw Pine facade response or summarized no-error response |
| Lint output | Output-consuming calls and request-path counts |
| Footprint proof table | `request.footprint`, `footprint.delta`, `footprint.rows`, row volume, availability gate, gas-out, divergence, hidden plots |
| Scope statement | Explicit `V9 not touched` statement unless cross-lane work was requested |

## Parallel Execution Plan

Use provider-safe parallelism for independent checks (no shared write targets). Run from repo root:

```bash
set -euo pipefail
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTDIR="quality/results/${STAMP}"
mkdir -p "$OUTDIR"

# Group 1: independent contract suites in parallel
./.venv/bin/python -m pytest tests/ag/test_v9_data_quality_gate.py -q > "$OUTDIR/01_data_quality.log" 2>&1 &
P1=$!
./.venv/bin/python -m pytest tests/ag/test_v9_run_provenance.py -q > "$OUTDIR/02_provenance.log" 2>&1 &
P2=$!
./.venv/bin/python -m pytest tests/ag/test_v9_core_pandera_contract.py -q > "$OUTDIR/03_pandera.log" 2>&1 &
P3=$!
wait $P1 $P2 $P3

# Group 2: quality playbook suite + smoke validation
./.venv/bin/python -m pytest quality/test_functional.py -q > "$OUTDIR/04_quality_functional.log" 2>&1 &
P4=$!
./.venv/bin/python scripts/ag/train_v9_locked.py \
  --csv scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.csv \
  --validate-only --smoke-ok > "$OUTDIR/05_train_validate_only.log" 2>&1 &
P5=$!
wait $P4 $P5

# Group 3: Monte Carlo smoke and broad regression test lane
./.venv/bin/python scripts/ag/monte_carlo_v9.py \
  --predictor-path models/warbird_pro_v9/locked_20260512_083803 \
  --csv scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.csv \
  --split oos \
  --run-summary models/warbird_pro_v9/locked_20260512_083803/v9_winner_clf_summary.json \
  --n-paths 10 \
  --seed 7 \
  --output-dir "$OUTDIR/mc_smoke" > "$OUTDIR/06_mc_smoke.log" 2>&1 &
P6=$!
./.venv/bin/python -m pytest tests/ag tests/duckdb_local -q > "$OUTDIR/07_full_existing.log" 2>&1 &
P7=$!
wait $P6 $P7
```

## Deep Post-Run Verification

After command execution:

1. Confirm each log file exists and contains terminal success markers (`passed`, `resolved trades`, `summary_split_ranges_utc`, etc.).
2. Confirm Monte Carlo output directory contains JSON metrics artifacts.
3. Run explicit manifest hash check:

```bash
./.venv/bin/python - <<'PY'
from pathlib import Path
from scripts.ag.v9_data_quality_gate import validate_manifest_hash
csv_path = Path('scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.csv')
manifest_path = csv_path.with_suffix('.manifest.json')
validate_manifest_hash(csv_path, manifest_path)
print('manifest_hash=ok')
PY
```

4. Run summary hash and split-range check:

```bash
./.venv/bin/python - <<'PY'
import json
import pandas as pd
from pathlib import Path
from scripts.ag.v9_run_provenance import check_summary_csv_hash, apply_time_split

csv_path = Path('scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.csv')
summary_path = Path('models/warbird_pro_v9/locked_20260512_083803/v9_winner_clf_summary.json')
summary = json.loads(summary_path.read_text())
check = check_summary_csv_hash(csv_path, summary)
if check.get('checked') and not check.get('matches'):
    raise SystemExit('summary hash mismatch')

df = pd.read_csv(csv_path, usecols=['ts'])
split_df, source = apply_time_split(df, split='oos', ts_col='ts', summary=summary)
if source != 'summary_split_ranges_utc':
    raise SystemExit(f'unexpected split source: {source}')
print(f'summary_hash=ok split_rows={len(split_df)}')
PY
```

5. Confirm no test errors occurred (not just zero failures).

## Execution UX (When Running This Protocol)

### Phase 1: Plan

Before execution, present:

- Numbered run table with estimated duration
- Expected artifacts under quality/results/<timestamp>
- Explicit warning if live external dependencies are unavailable

### Phase 2: Progress

For each test/check:

- `✓` pass, `✗` fail, `⧗` in progress
- One-line status update with elapsed time
- On failure: one-line root assertion/error summary

### Phase 3: Results

Report:

- Pass/fail counts
- Table of failed checks and direct log file references
- Promotion recommendation: `SHIP IT`, `FIX FIRST`, or `NEEDS INVESTIGATION`

## Reporting Format

Save summary report to quality/results/YYYY-MM-DD-integration.md.

| Check | Result    | Evidence                         |
| ----- | --------- | -------------------------------- |
| ...   | PASS/FAIL | `quality/results/<stamp>/...log` |

Include:

- Failed checks with root cause
- Any contract drift discovered
- Recommended next action
