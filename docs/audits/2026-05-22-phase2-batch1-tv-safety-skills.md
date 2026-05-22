# Phase 2 Batch 1 Audit: TV Safety Skills

Date: 2026-05-22
Status: complete

## Scope

Phase-2 custom-skill migration batch 1 from legacy `.claude/skills/` into
canonical `agents/skills/`.

## Candidates

1. `verify-tv-slot`
2. `tradingview-chart-control`

## Decisions

1. `verify-tv-slot`: keep and migrate
   - canonical target: `agents/skills/verify-tv-slot/SKILL.md`
   - updated for current active V9/Nexus production-locked slot policy
2. `tradingview-chart-control`: drop
   - source directory existed but was empty (no skill body, no references)
   - retired as non-actionable legacy surface

## Actions

1. Added canonical skill file:
   - `agents/skills/verify-tv-slot/SKILL.md`
2. Updated registries/policies:
   - `agents/manifest.yaml`
   - `agents/skills/README.md`
   - `agents/skills/phase-2-custom-skill-migration.md`
   - `MEMORY.md`
3. Retired legacy batch-1 sources:
   - `.claude/skills/verify-tv-slot/SKILL.md`
   - `.claude/skills/verify-tv-slot/` (directory)
   - `.claude/skills/tradingview-chart-control/` (empty directory)

## Verification

Required after batch actions:

1. `./scripts/guards/warbird-agent-precheck.sh --mode manual`
2. `tc_validator --fast`

## Risk Notes

- Remaining `.claude/skills/` custom-only entries still require migration
  batches; drift risk is reduced but not eliminated until phase-2 completion.
