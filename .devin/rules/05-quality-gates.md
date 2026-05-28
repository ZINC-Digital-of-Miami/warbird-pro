# Quality Gates

## Before Any Commit

```bash
./scripts/guards/warbird-agent-precheck.sh --mode manual
```

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

- **SonarQube (Sonic)** — installed in GitHub as the primary code quality gate. Replacing Codacy.
- Review SonarQube findings on PRs alongside lint/build results.

## Docs-Only Work

Run `npm run lint` and `npm run build` when docs claim operational truth.
