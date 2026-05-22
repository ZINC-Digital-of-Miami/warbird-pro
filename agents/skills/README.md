# Skills Registry

Canonical skill decisions live here.

## Policy

- New skills are authored under `agents/skills/`.
- Legacy skill trees are treated as migration sources only.
- Overlap is resolved by keep-one, retire-duplicates.

## 2026-05-22 Curation Snapshot

Keep (active, curated):

- project safety and governance guidance from `.github/instructions/`
- custom quant/trading safety skills migrated under `agents/skills/`:
  - `cdp-down-recovery`
  - `tv-preflight`
  - `senior-quant-mindset`
  - `v9-promote-champion`
  - `verify-tv-slot`
- read-only MCP-oriented helpers that are not tied to Hermes runtime

Retire or migrate from legacy mirrors:

- `.hermes/skills/**` (removed in 2026-05-22 phase-1)
- duplicate Pine primer stacks mirrored in multiple locations
- duplicate generic utility skills mirrored in both `.github/skills` and
  `.claude/skills` (removed from `.claude/skills` in 2026-05-22 de-dup pass)

Audit record: `docs/audits/2026-05-22-skill-overlap-pruning.md`.
Phase-2 plan: `agents/skills/phase-2-custom-skill-migration.md`.
Batch-1 audit: `docs/audits/2026-05-22-phase2-batch1-tv-safety-skills.md`.

## Required Audit Rules

- Every kept skill must have a clear owner, purpose, and last-reviewed date.
- Every retired skill must be listed in an audit note before removal.
- If two skills solve the same task, keep only one canonical copy.
