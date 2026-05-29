# Quality Gates

## Before Any Commit

```bash
./scripts/guards/warbird-agent-precheck.sh --mode manual
```

This runs the **Knowledge Enforcement Engine** and **File Protection Engine** first, then the quality lane. If enforcement fails, the commit is blocked before any quality checks run.

## Before Claiming PR Is Mergeable

```bash
./scripts/guards/check-github-merge-readiness.sh
```

## Standard Gates

- `npm run lint` — standard lint gate
- `npm run build` — must pass before every push

## V9 Core Trainer/ETL Changes

Also run:

```bash
pytest tests/ag/test_v9_core_indicator_input_contract.py -q
pytest tests/ag/test_v9_core_training_targets.py -q
```

## Code Quality Checks

- **SonarQube (Sonic)** — primary linter, review, audit, and reporting surface.
- The SonarQube GitHub Actions workflow is the primary hosted gate and must run
  `npm ci`, `npm run lint`, `npm run build`, repo guard checks, Pine static
  lint, Python contract tests with coverage, and the SonarQube Cloud scan in
  one job.
- The scanner must wait for the Sonar Quality Gate so a red gate fails the
  GitHub Actions job.
- GitHub ruleset `Warbird Repo Push Checks` requires both `SonarQube Cloud Scan`
  and `SonarCloud Code Analysis` on `main`.
- Treat SonarQube as the first defect report to triage for remediation work.
- Keep lint/build/test/guard commands as executable verification after approved fixes.

## Docs-Only Work

Run `npm run lint` and `npm run build` when docs claim operational truth.
