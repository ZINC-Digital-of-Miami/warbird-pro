# Phase 2 Batch 2 Audit: Pine Foundation Skills

Date: 2026-05-22
Status: complete

## Scope

Phase-2 batch-2 migration for Pine foundation and assembler skills from legacy
`.claude/skills/` into canonical `agents/skills/`.

## Candidates

1. `pine-script-ai-coding-agent`
2. `tradingview-indicator-assembler-optuna-ready`
3. `tc-*` legacy placeholders

## Decisions

1. `pine-script-ai-coding-agent`: keep and migrate
   - canonical path: `agents/skills/pine-script-ai-coding-agent/SKILL.md`
2. `tradingview-indicator-assembler-optuna-ready`: keep and migrate
   - canonical path: `agents/skills/tradingview-indicator-assembler-optuna-ready/SKILL.md`
3. `tc-*` placeholders: drop
   - all `tc-*` directories under `.claude/skills/` were empty
   - stale index file `.claude/skills/tc-README.md` retired with the placeholder set

## Actions

1. Copied both non-empty skill directories (including `references/`) into
   `agents/skills/`.
2. Added `owner` + `last_reviewed` metadata to migrated skill frontmatter.
3. Updated migrated assembler skill repo-operating notes to align with current
   protected Pine surfaces and dynamic budget-check policy.
4. Updated registries:
   - `agents/manifest.yaml`
   - `agents/skills/README.md`
   - `agents/skills/phase-2-custom-skill-migration.md`
   - `MEMORY.md`
5. Removed legacy sources from `.claude/skills/` for the migrated and dropped
   batch-2 surfaces.

## Verification

Required checks after batch actions:

1. `./scripts/guards/warbird-agent-precheck.sh --mode manual`
2. `tc_validator --fast`

## Risk Notes

- Remaining `.claude/skills/` entries are now concentrated in training,
  Optuna, and domain-specific surfaces; drift risk is reduced but still active
  until remaining phase-2 batches complete.
