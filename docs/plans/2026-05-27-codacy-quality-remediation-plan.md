# Warbird Codacy Quality Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` or `superpowers:subagent-driven-development` to implement this plan task-by-task. Codacy is advisory only; do not use Codacy auto-fix.

**Target file:** `docs/plans/2026-05-27-codacy-quality-remediation-plan.md`

**Goal:** Reduce Warbird’s real Codacy defect load by fixing high-risk Python/modeling issues first, then tune noisy rule families only after defect-bearing surfaces are under control.

**Architecture:** Treat Codacy as a dashboard and defect-map source, not an editor. Each phase starts with a local inventory, fixes one named issue family, adds/updates focused tests, then runs Warbird local gates before commit/push.

**Tech Stack:** Codacy Cloud/CLI, GitHub CLI, Python 3, pytest, local Warbird guard scripts, Next/npm lint/build, GitHub branch rulesets.

---

## 1. Current Codacy Snapshot

Dashboard reviewed on `ZINC-Digital-of-Miami/warbird-pro`, branch `main`.

- Total current issues: `2,122`
- Ignored issues: `0`
- Issues/kLoC: `26.881`
- Complexity: `16%`
- Duplication: `14%`
- Coverage: not configured
- Branch warning: Codacy says `main branch is not protected`
- GitHub truth: repo is private and `main` is protected by active ruleset `Warbird Repo Push Checks`; legacy branch-protection API reports unprotected, so Codacy is likely reading the old endpoint.

Top issue categories:
- Error prone: `777`
- Code complexity: `549`
- Best practice: `262`
- Compatibility: `225`
- Security: `126`
- Comprehensibility: `92`
- Unused code: `49`
- Performance: `42`

Top visible Codacy patterns:
- `Enforce Medium Cyclomatic Complexity Threshold`: `273`
- `Use Pyright Static Type Checker`: `211`
- `Enforce Medium Number of Lines of Code (NLOC) Limit`: `202`
- `Avoid Using Assert in Non-Test Code`: `122`
- `Disallow Missing React When Using JSX`: `106`
- `Avoid Using Emphasis Instead of Headings`: `96`
- `Disallow ES2015 Modules`: `72`
- `Detect Python Source Code Errors with Pyflakes`: `63`
- `Avoid Catching Broad Exception`: `56`

Top visible files:
- `scripts/ag/shap_v9.py`: `_write_summary_md` exceeds NLOC limit.
- `scripts/ag/policy_mc_sweep.py`: `_simulate_exit_outcome` exceeds NLOC limit.
- `scripts/duckdb_local/runner.py`: `seed_champion` slightly exceeds complexity limit.
- `scripts/ag/run_diagnostic_shap.py`: `infer_run_integrity` has high cyclomatic complexity.

---

## 2. Guardrails

- Do **not** click Codacy `Fix issues`.
- Do **not** let Codacy suggested fixes write into the repo.
- Do **not** edit Pine unless explicitly approved in that implementation session.
- Work on `main` only.
- Before each phase: run `git status --short --untracked-files=all`.
- Every defect family must produce a defect map before code edits: path, issue class, severity, owner surface, likely root cause, verification command.
- Keep commits small: one issue family per commit.
- If a phase touches V9 Core trainer/ETL/provenance, run:
  - `pytest tests/ag/test_v9_core_indicator_input_contract.py -q`
  - `pytest tests/ag/test_v9_core_training_targets.py -q`
- Before push, run:
  - `./scripts/guards/warbird-agent-precheck.sh --mode pre-push`
  - `./scripts/guards/check-github-merge-readiness.sh`
- No `--no-verify`, no force push, no destructive git.

---

## 3. Issue Families And Priority

### Family A — Static Correctness First

Primary target: Pyright, Pyflakes, import resolution, unused imports, unused variables.

Why first:
- These are most likely to hide real runtime failures.
- They cut across active modeling scripts.
- They should be fixed before large refactors, because type/import defects make refactors less trustworthy.

Implementation lane:
- Generate local/current defect map using Codacy CLI where possible:
  - `./.codacy/cli.sh analyze --tool pylint --format sarif`
  - `./.codacy/cli.sh analyze --tool opengrep --format sarif`
- If Pyright is not locally installed, decide whether to add a repo-pinned dev tool or use Codacy-only readout. Do not silently depend on global tools.
- Fix only true defects first: bad imports, missing optional guards, wrong `None` assumptions, stale symbols, unreachable paths.
- Do not “fix” type warnings by adding broad `Any` or blanket ignores unless the defect map explains why.

Acceptance:
- Local Python syntax checks pass.
- Targeted pytest passes for touched modules.
- Codacy issue count for Pyright/Pyflakes/import families drops or no new issues are introduced.

### Family B — Modeling Complexity Hotspots

Primary target: high-complexity and high-NLOC functions in active AG/modeling code.

Start here after Family A:
- `scripts/ag/policy_mc_sweep.py::_simulate_exit_outcome`
- `scripts/ag/run_diagnostic_shap.py::infer_run_integrity`
- `scripts/ag/shap_v9.py::_write_summary_md`
- `scripts/duckdb_local/runner.py::seed_champion`

How to refactor:
- Preserve public CLI behavior and output schemas.
- Extract pure helpers with names that describe the business rule:
  - TP/SL hit detection
  - promoted fast-runner exit handling
  - run-integrity fold summary loading
  - SHAP markdown section rendering
- Add tests before refactor where coverage is thin.
- For `policy_mc_sweep.py`, avoid running full E2E by default; split fast unit tests from fixture-heavy tests.

Acceptance:
- Complexity/NLOC drops on the target functions.
- Existing output artifacts remain schema-compatible.
- Relevant tests pass:
  - `pytest tests/ag/test_policy_mc_sweep_cli.py -k "help or gate_d or ranker or gate_f" -q`
  - targeted new tests for extracted helpers
  - impacted `tests/ag/**` or `tests/duckdb_local/**`

### Family C — Error-Prone Runtime Semantics

Primary target: asserts in non-test code, broad exceptions, hardcoded datetime formats, shell quoting.

Why third:
- These are real reliability risks, but some may be intentional guard behavior.
- They require judgment, not bulk cleanup.

Implementation lane:
- Replace runtime `assert` with explicit exceptions carrying Warbird-specific context.
- Narrow broad `except Exception` blocks where the expected exception type is knowable.
- Where broad catch is intentional, add a short comment and/or local suppression only after documenting why.
- Review shell warnings for real command-injection/word-splitting risk before touching scripts.

Acceptance:
- No behavior changes to successful paths.
- Failure messages become clearer.
- Tests cover at least one expected failure path per changed runtime guard.

### Family D — Security And Dependency Surface

Primary target: Codacy `Security 126`, Trivy, OpenGrep, dependency alerts.

Implementation lane:
- Separate dependency issues from source-code SAST issues.
- Run:
  - `npm audit --audit-level=moderate`
  - `./.codacy/cli.sh analyze package-lock.json --tool trivy --format sarif`
  - `./.codacy/cli.sh analyze --tool opengrep --format sarif`
- Fix critical/high findings immediately if reproducible.
- For medium/low findings, add to defect map and batch only when changes are localized.

Acceptance:
- No open Dependabot alert regresses.
- Trivy remains clean for `package-lock.json`.
- No broad SAST suppression without documented root cause.

### Family E — Codacy Rule Noise / False Positives

Primary target: compatibility rules that are wrong for modern Warbird JS/React/TS.

Examples:
- `Disallow Missing React When Using JSX`
- `Disallow ES2015 Modules`
- `Disallow Block-Scoped Variables`
- `Disallow Destructuring`
- `Disallow Template Literals`

Implementation lane:
- Do not rewrite modern JS into old syntax.
- Audit which Codacy tool emits each rule.
- Disable or scope noisy rules in Codacy/tool config only when the rule conflicts with the repo’s actual stack.
- Keep useful JS rules active: import resolution, unsafe access, security, build-breaking syntax.

Acceptance:
- Codacy issue count drops without weakening real lint/build coverage.
- `npm run lint` and `npm run build` still pass.
- Config changes are documented in the plan or a follow-up note.

### Family F — Coverage Setup

Primary target: Codacy coverage card currently says coverage is not configured.

Implementation lane:
- Do not make coverage a blocker for the first remediation pass.
- Add coverage only after Python defect and complexity phases stabilize.
- Preferred first step: Python coverage for focused `tests/ag/**` and `tests/duckdb_local/**`, not frontend-wide coverage.

Acceptance:
- Coverage upload path is documented.
- Coverage generation does not require cloud training data or private local artifacts.

---

## 4. Multi-Phase Execution Plan

### Phase 0 — Baseline And Defect Map

- Create this plan file at `docs/plans/2026-05-27-codacy-quality-remediation-plan.md`.
- Capture current local state:
  - `git status --short --untracked-files=all`
  - `git branch --show-current`
  - `git rev-parse --short HEAD`
- Capture GitHub protection discrepancy:
  - `gh api repos/ZINC-Digital-of-Miami/warbird-pro/branches/main --jq '{name,protected,protection}'`
  - `gh api repos/ZINC-Digital-of-Miami/warbird-pro/rulesets`
- Capture Codacy baseline manually from dashboard or Codacy CLI.
- Produce a defect-map section inside the plan or companion audit note.

### Phase 1 — Static Correctness

- Fix real Python static correctness defects first.
- Avoid style-only edits.
- Add missing tests for changed import/type behavior.
- Commit message: `fix(quality): resolve python static correctness findings`.

### Phase 2 — Complexity Hotspots

- Refactor the four visible hotspot functions in smallest safe slices.
- Commit separately by module if needed:
  - `refactor(ag): split policy exit simulation helpers`
  - `refactor(ag): split diagnostic shap integrity checks`
  - `refactor(ag): split shap markdown rendering`
  - `refactor(duckdb): simplify champion seeding`
- Preserve output schemas and CLI flags.

### Phase 3 — Error-Prone Runtime Semantics

- Replace unsafe asserts and broad exception catches in active code.
- Leave archived/reference surfaces alone unless Codacy still counts them and `.codacy.yaml` should exclude them.
- Commit message: `fix(quality): harden runtime guard failures`.

### Phase 4 — Security Verification

- Re-run Trivy/audit/OpenGrep.
- Fix only reproducible findings.
- If Codacy security count remains high because of false positives, document each pattern before suppressing.

### Phase 5 — Rule Noise And Coverage

- Tune obsolete JS/React compatibility rules.
- Add coverage reporting design only after quality issue families are stable.
- Do not prioritize coverage before correctness and complexity.

---

## 5. Agent Assignment

Recommended:
- **Codex primary implementer** for repo edits, tests, commits, and push protocol.
- **Opus/Copilot reviewer only** for second-pass review on complex refactors.
- **Codacy advisory only** for issue discovery and post-change confirmation.
- **Do not allow Codacy auto-fix**.

Reason:
- Codacy has useful issue inventory but lacks Warbird context.
- The high-value targets are active modeling scripts with domain semantics.
- Auto-fix is too likely to flatten behavior, weaken exceptions, or create broad churn.

---

## 6. Verification Matrix

Minimum per phase:
- `git diff --check`
- Python changed-file compile:
  - `python3 -m py_compile <changed.py>`
- Targeted pytest for touched surfaces.
- `npm run lint`
- `npm run build`
- `./scripts/guards/check-contamination.sh`
- `./scripts/guards/check-no-tv-force.sh`
- `./scripts/guards/check-canonical-zoo.sh`
- `./scripts/guards/check-fib-scanner-guardrails.sh`

Before push:
- `./scripts/guards/warbird-agent-precheck.sh --mode pre-push`
- `./scripts/guards/check-github-merge-readiness.sh`
- `git push origin main` only after explicit approval.

---

## 7. Assumptions

- The plan belongs under `docs/plans/`, matching the existing Warbird plan folder.
- First implementation pass should target Python/modeling defects, not documentation style warnings.
- Codacy’s branch-protection warning is lower priority than issue remediation because GitHub already reports active ruleset protection.
- Pine is out of scope unless explicitly approved in the implementation session.
- Full Codacy MCP is unavailable in this Codex session; local Codacy CLI and dashboard review are the available Codacy surfaces.
