# Phase 2: Custom Skill Migration

Status: in progress (batch-1 started 2026-05-22).

## Objective

Move remaining custom-only legacy skills from `.claude/skills/` into
`agents/skills/` in controlled batches, with audit records and explicit
keep/drop decisions.

## Current Baseline

- Generic overlap between `.github/skills/` and `.claude/skills/` is removed.
- `agents/skills/` currently holds the active curated safety set.
- Remaining `.claude/skills/` entries are custom-only and pending migration.

## Batch Sequence

1. TradingView safety and workflow wrappers
   - candidate surfaces: `verify-tv-slot`, `tradingview-chart-control`
   - 2026-05-22 outcome:
     - migrated `verify-tv-slot` to `agents/skills/verify-tv-slot/SKILL.md`
     - retired legacy `.claude/skills/verify-tv-slot/`
     - dropped `.claude/skills/tradingview-chart-control/` (empty directory,
       no skill body to migrate)
2. Pine foundations and advanced helpers
   - candidate surfaces: `tc-*`, `pine-script-ai-coding-agent`,
     `tradingview-indicator-assembler-optuna-ready`
3. Training pipeline and model-governance helpers
   - candidate surfaces: `training-*`, `preflight-training`,
     `optuna-*`, `pine-tuning-optimizations`
4. Domain-specific or legacy-only wrappers
   - candidate surfaces: `_tc_raw`, `quality-playbook`, `supabase-ml-ops`

## Keep/Drop Gate Per Skill

For each candidate skill:

1. Owner and active user need are explicit.
2. Content aligns with current V9/Core + agents umbrella contract.
3. No overlap with existing `.github/skills/` or `agents/skills/` entries.
4. Safety boundaries are fail-closed and tool scope is minimal.
5. Last-reviewed date is added in the migrated canonical copy.

If any gate fails, mark the skill as drop/defer in the audit log and do not
migrate blindly.

## Verification For Each Batch

1. `./scripts/guards/warbird-agent-precheck.sh --mode manual`
2. `tc_validator --fast`
3. Repo-wide overlap check confirms no duplicate top-level skill names across
   canonical and legacy surfaces for migrated entries.

## Audit Requirements

Each batch must append a dated audit note in `docs/audits/` covering:

- migrated skills
- dropped/deferred skills
- rationale and risk
- verification outputs and blockers

## Definition of Done

- `agents/skills/` is the only active custom skill surface.
- Remaining `.claude/skills/` entries are either migrated with parity or
  retired with audit evidence.
- No duplicate skill-name ownership remains across active surfaces.
