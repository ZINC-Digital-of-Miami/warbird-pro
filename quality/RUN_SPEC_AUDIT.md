# Spec Audit Protocol: Warbird Pro V9 Core + Nexus Indicator (Council of Three)

## The Definitive Audit Prompt

Use the prompt below unchanged with three independent AI auditors.

---

**Context files to read first:**

1. AGENTS.md
2. CLAUDE.md
3. quality/QUALITY.md
4. docs/MASTER_PLAN.md
5. docs/contracts/pine_indicator_ag_contract.md
6. scripts/ag/train_v9_locked.py
7. scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py
8. scripts/ag/v9_run_provenance.py
9. scripts/ag/v9_data_quality_gate.py
10. scripts/ag/backfill_v9_run_provenance.py
11. scripts/ag/monte_carlo_v9.py

**Task:**
Act as the Tester. Read the actual code and compare implementation behavior against the contracts and requirements in the context files.

**Requirement confidence tiers:**

- `formal`: written contract in AGENTS/CLAUDE/docs/contracts/quality/QUALITY formal tags
- `user-confirmed`: explicitly confirmed by operator/user statements in active docs
- `inferred`: deduced from defensive behavior or implementation patterns

When reporting findings, include the requirement tag in this format:
`[Req: formal|user-confirmed|inferred — source]`

For inferred requirements, append `NEEDS REVIEW`.

**Rules:**

- ONLY list defects.
- Every defect must cite file path and line number.
- If no line number, do not include the finding.
- Grep before claiming a requirement is missing.
- Read function bodies before claiming behavior.
- Classify each finding as one of: `MISSING`, `DIVERGENT`, `UNDOCUMENTED`, `PHANTOM`.
- Do not include style-only suggestions.

**Project-specific scrutiny areas:**

1. In `scripts/ag/train_v9_locked.py`, verify that label generation still enforces 24-bar horizon and same-bar TP/SL pessimism exactly as documented.
2. In `scripts/ag/train_v9_locked.py`, verify `REQUIRED_INPUT_COLUMNS` and `ML_FEATURES` lock still align with build output and summary contracts.
3. In `scripts/ag/v9_run_provenance.py`, verify non-`all` splits fail closed when split ranges are missing.
4. In `scripts/ag/v9_run_provenance.py`, verify summary hash matching logic cannot silently pass on mismatched hashes.
5. In `scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py`, verify manifest contract still enforces `source_kind` prefix `DATABENTO_` and forbidden lineage tokens.
6. In `scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py`, verify export schema checks still enforce monotonic timestamps and required label-policy columns.
7. In `scripts/ag/v9_data_quality_gate.py`, verify sparse-event and near-dead signal guards match quality constitution scenarios.
8. In `scripts/ag/backfill_v9_run_provenance.py`, verify idempotence and row-parity safeguards cannot be bypassed by default execution.
9. In `scripts/ag/monte_carlo_v9.py`, verify predictor layout resolution and suite-root detection work for both single-head and model-suite artifact layouts.
10. Cross-check docs and code for feature-surface consistency (82 ML features / 88 model features) and report any divergence.

**Output format:**

### path/to/file.py

- **Line NNN:** [MISSING|DIVERGENT|UNDOCUMENTED|PHANTOM] [Req: tier — source] Description.
  Spec says: ...
  Code does: ...
  Impact: ...

---


## Nexus Indicator Audit Prompt

Use this prompt unchanged when the requested audit is Nexus-scoped.

---

**Context files to read first:**

1. AGENTS.md
2. quality/QUALITY.md
3. quality/RUN_NEXUS_INDICATOR.md
4. quality/RUN_CODE_REVIEW.md
5. indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine

**Task:**
Audit the Nexus indicator lane only. Do not audit V9 Core, V9 Pine, model training, Optuna, Supabase, or dashboard surfaces unless the user explicitly requested a cross-lane comparison. Compare the implementation against the Nexus quality lane and report only defects.

**Rules:**

- ONLY list defects.
- Every defect must cite file path and line number.
- If no line number, do not include the finding.
- Grep before claiming a requirement is missing.
- Read the full Pine file before claiming behavior.
- Classify each finding as one of: `MISSING`, `DIVERGENT`, `UNDOCUMENTED`, `PHANTOM`.
- Do not include style-only suggestions.
- Alerts are non-authoritative; only flag alerts if they interfere with footprint/plot/evidence truth.

**Nexus-specific scrutiny areas:**

1. Verify the file remains the Nexus indicator lane and not a V9 surface.
2. Verify footprint evidence comes from `request.footprint()`, `footprint.delta()`, `footprint.rows()`, and row total volume.
3. Verify volume flow does not substitute candle body/wick or generic OHLCV proxies for footprint evidence.
4. Verify `fpFlowAvailable` fails closed on missing delta, missing total volume, or non-positive volume.
5. Verify `normCumDelta`, `deltaSlope`, and `deltaDir` are safe under warmup and unavailable-footprint states.
6. Verify gas-out exhaustion claims are backed by signed footprint delta deceleration.
7. Verify divergence filters state whether unavailable footprint can pass, and whether that matches `quality/RUN_NEXUS_INDICATOR.md`.
8. Verify hidden `nexus_*` plots preserve the footprint evidence export contract.
9. Verify alert logic cannot redefine signal truth.
10. Verify any Pine edit was followed by Pine facade compile, pine lint, contamination/no-TV-force guards, and build evidence.

**Output format:**

### path/to/file

- **Line NNN:** [MISSING|DIVERGENT|UNDOCUMENTED|PHANTOM] [Req: tier — source] Description.
  Spec says: ...
  Code does: ...
  Impact: ...

---

## Running The Council Of Three

1. Execute the definitive prompt in three separate models/tools.
2. Keep auditors independent (no cross-auditor context sharing).
3. Save raw outputs to:

- quality/spec_audits/YYYY-MM-DD-auditor1.md
- quality/spec_audits/YYYY-MM-DD-auditor2.md
- quality/spec_audits/YYYY-MM-DD-auditor3.md

## Triage Process

Merge findings by confidence:

| Confidence         | Found By     | Action                                                     |
| ------------------ | ------------ | ---------------------------------------------------------- |
| Highest            | 3/3 auditors | Treat as real defect unless direct code evidence disproves |
| High               | 2/3 auditors | Verify and fix or update spec                              |
| Needs verification | 1/3 auditor  | Run verification probe before acting                       |

### Verification Probe (For Disputed Facts)

When auditors disagree, run a read-only probe prompt:

- Provide disputed claim
- Provide exact file and function references
- Ask verifier to return direct line-cited ground truth only

Do not resolve by majority vote alone.

## Finding Disposition Categories

For each confirmed finding, assign exactly one:

1. Spec bug (spec is wrong)
2. Design decision (needs human judgment)
3. Real code bug (requires code fix)
4. Documentation gap (code exists, spec missing)
5. Missing test (behavior correct but untested)
6. Inferred requirement wrong (remove or rewrite inferred requirement)

## Fix Execution Rules

- Fix in small subsystem batches.
- After each batch: run targeted tests and re-audit changed files.
- Do not submit one giant multi-subsystem fix prompt.

## Output Artifacts

Save:

- Individual audit reports under quality/spec_audits/
- Merged triage file: quality/spec_audits/YYYY-MM-DD-triage.md

Triage file must include:

| Finding ID | Classification | Confidence | Disposition | Owner Action |
| ---------- | -------------- | ---------- | ----------- | ------------ |
| ...        | ...            | ...        | ...         | ...          |
