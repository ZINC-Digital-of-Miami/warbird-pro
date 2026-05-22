# Agents Umbrella

Status: active as of 2026-05-22.

This directory is the single source of truth for IDE agent assets in this
repository. New multi-agent docs, role definitions, skill registries, and
automation scripts must land here first.

## Why this exists

- Remove drift across `.github`, `.claude`, `.hermes`, and `.kilocode`.
- Keep one intentional registry for roles and skills.
- Eliminate manual daily cleanup by running low-cost process cleanup
  automatically.

## Layout

- `agents/roles/`: custom role definitions and role hardening checkpoints.
- `agents/skills/`: curated skill registry and overlap decisions.
- `agents/mcp/`: portable read-only MCP servers that do not require Hermes.
- `agents/scripts/`: install/decommission and process cleanup scripts.
- `agents/launchd/`: launchd templates for lightweight automation.
- `agents/manifest.yaml`: single registry for active roles, skills, MCP, and
   automation surfaces.

## Sequential Execution Plan

1. Phase 1 (this change):
   - establish canonical `agents/` surface
   - add no-manual process cleanup automation
   - add Hermes decommission script
   - wire existing guard lane to run cleanup silently
2. Phase 2 (separate):
   - role hardening and intentional keep/drop curation
   - rebuild kept roles for current 2026-05 Warbird workflow
   - remove shell/template role content
3. Phase 3:
   - migrate or retire legacy mirror surfaces (`.github/.claude/.hermes/.kilocode`)
   - keep only compatibility shims that are still needed

Current migration status:

- `.hermes/**` retired in phase-1.
- `.kilocode/skills/**` retired in phase-1.
- `.claude/skills/**` completed phase-2 curation on 2026-05-22; remaining
  ignored local files are migration evidence only, not active registry
  surfaces.

## Checkpoints

- `docs/audits/2026-05-22-agents-umbrella-phase-1.md`
- `agents/roles/phase-2-role-hardening.md`
- `agents/skills/phase-2-custom-skill-migration.md`
