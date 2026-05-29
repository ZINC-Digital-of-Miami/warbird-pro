# Skills Registry

Canonical skill decisions live here. **Devin is the only active agent platform.**

## Policy

- New skills are authored under `agents/skills/`.
- All legacy skill trees (`.github/skills/`, `.claude/skills/`) are removed or retired.
- Overlap is resolved by keep-one, retire-duplicates.

## Active Skills (2026-05-29)

- `cdp-down-recovery`
- `tv-preflight`
- `senior-quant-mindset`
- `v9-promote-champion`
- `verify-tv-slot`
- `pine-script-ai-coding-agent`
- `tradingview-indicator-assembler-optuna-ready`
- `v9-core-training-governance`
- `v9-postfit-shap-monte-carlo-gates`
- `warbird-tuning-router`
- `chart-parity-authority` (v2.4.1 — locked rulings for local dashboard)

## Retired (removed 2026-05-29)

All `.github/skills/` directories (14 skills) — these were Copilot/generic
skills that are not Devin-compatible:
- `context-map`, `conventional-commit`, `create-agentsmd`, `doublecheck`,
  `git-commit`, `point-in-time-ml-audit`, `postgresql-code-review`,
  `postgresql-optimization`, `refactor`, `refactor-plan`, `repo-truth-audit`,
  `security-review`, `supabase-database-audit`, `what-context-needed`

All `.claude/skills/` directories — retired in phase-2 (2026-05-22).

Audit records:
- `docs/audits/2026-05-22-skill-overlap-pruning.md`
- `agents/skills/phase-2-custom-skill-migration.md`

## Required Audit Rules

- Every kept skill must have a clear owner, purpose, and last-reviewed date.
- Every retired skill must be listed in an audit note before removal.
- If two skills solve the same task, keep only one canonical copy.
