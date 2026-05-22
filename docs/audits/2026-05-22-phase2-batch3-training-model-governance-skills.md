# Phase 2 Batch 3 Audit: Training And Model-Governance Skills

Date: 2026-05-22
Status: complete

## Scope

Phase-2 batch-3 migration for training, Optuna, and Pine-tuning helper skills
from legacy `.claude/skills/` source material into canonical `agents/skills/`.

## Candidates

1. `training-ag-best-practices`
2. `training-ag-feature-finder`
3. `training-full-zoo`
4. `training-gbm-only`
5. `training-hard-gate`
6. `training-indicator-optimization`
7. `training-monte-carlo`
8. `training-pre-audit`
9. `training-quant-trading`
10. `training-shap`
11. `training-supabase-data`
12. `training-tv-backtesting`
13. `preflight-training`
14. `optuna-setup`
15. `optuna-optimization-specialist`
16. `pine-tuning-optimizations`

## Decisions

1. Rebuild, do not copy one-for-one.
   - legacy source files mix useful lessons with retired commands and paths.
2. Keep active V9/Core training guidance as:
   - `agents/skills/v9-core-training-governance/SKILL.md`
3. Keep active V9 post-fit governance as:
   - `agents/skills/v9-postfit-shap-monte-carlo-gates/SKILL.md`
4. Keep tuning-path selection guidance as:
   - `agents/skills/warbird-tuning-router/SKILL.md`
5. Do not migrate stale wrapper guidance verbatim when it depends on:
   - `scripts/ag/train_ag_baseline.py`
   - local Postgres `ag_training`
   - FRED/macro/cloud feature stacking
   - stale `scripts/optuna/` paths
   - retired v7/v8 strategy parity flows
6. Preserve all valid AG/Optuna implementations, runners, workspaces, and
   artifacts. This batch changes the canonical agent-skill guidance surface
   only.

## Actions

1. Added three canonical skills under `agents/skills/`.
2. Added `owner` and `last_reviewed` metadata to each new skill.
3. Updated registries and phase tracking:
   - `agents/manifest.yaml`
   - `agents/skills/README.md`
   - `agents/skills/phase-2-custom-skill-migration.md`
   - `MEMORY.md`
4. Left ignored local `.claude/skills/` migration-source files untouched. They
   are not tracked and are not active registry surfaces; phase-2 evidence now
   lives in `agents/skills/` and this audit.
5. Did not delete or edit active AG/Optuna code, study databases, workspaces,
   model artifacts, Pine files, or training scripts.

## Rationale

The old batch-3 wrappers were unsafe to migrate verbatim because many sections
still instructed agents to launch or preflight retired warehouse workflows. The
canonical batch-3 replacement keeps the durable lessons but points active work
to:

- `scripts/ag/train_v9_locked.py`
- `scripts/ag/shap_v9.py`
- `scripts/ag/monte_carlo_v9.py`
- `scripts/duckdb_local/`
- the current V9/Core authority docs and tests

## Verification

Completed checks after batch actions:

1. PASS: `./scripts/guards/warbird-agent-precheck.sh --mode manual`
   - local quality lane passed
   - `npm run lint` passed
   - `npm run build` passed
   - V9 contract tests passed: `6 passed`
   - tuner jsonl safety tests passed: `2 passed, 63 deselected`
2. PASS: `tc_validator --fast`
   - fast local quality lane passed
   - agents umbrella, manifest, skills, roles, Quant role, and process-reaper
     surface checks passed
3. PASS: migrated canonical skill names are present and are not duplicated in
   the legacy `.claude/skills` mirror:
   - `v9-core-training-governance`
   - `v9-postfit-shap-monte-carlo-gates`
   - `warbird-tuning-router`
4. PASS: `git diff --check`
5. PASS: `git diff --name-status` showed no tracked deletions.

## Risk Notes

- Remaining phase-2 batch-4 local source material is domain-specific or
  legacy-only (`_tc_raw`, `quality-playbook`, `supabase-ml-ops`).
- V9 training/model promotion claims still require run-specific evidence; these
  skills only route and gate the work.
