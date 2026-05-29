# Agents Umbrella

Status: active as of 2026-05-29. **Devin is the only active agent platform.**

This directory is the single source of truth for agent assets in this
repository. New role definitions, skill registries, and automation scripts
must land here first.

## Why this exists

- Single source of truth for all agent configuration.
- One intentional registry for roles and skills.
- Eliminate drift across sessions via committed guardrails.

## Layout

- `agents/roles/`: role definitions.
- `agents/skills/`: curated skill registry and overlap decisions.
- `agents/mcp/`: portable read-only MCP servers.
- `agents/scripts/`: process cleanup scripts.
- `agents/launchd/`: launchd templates for lightweight automation.
- `agents/manifest.yaml`: single registry for active roles, skills, MCP, and
   automation surfaces.

## Agent Platform

**Devin only.** All other agent platforms (Hermes, Copilot agents, Claude Code
skills) have been retired as of 2026-05-29. Legacy artifacts are listed in
`manifest.yaml` under `retired:`.

Retired surfaces (removed 2026-05-29):
- `.hermes/**` — retired in phase-1 (2026-05-22)
- `.github/agents/` — Copilot agent definitions (removed)
- `.github/skills/` — Copilot/generic skills (removed)
- `.github/copilot-instructions.md` — Copilot redirector (removed)
- `.github/workflows/copilot-review.yml` — auto Copilot review (removed)
- `.copilot-tracking/` — Copilot research tracking (removed)
- `.claude/skills/**` — Claude Code skills (retired in phase-2, 2026-05-22)
- `agents/scripts/decommission_hermes.sh` — no longer needed (removed)

## Checkpoints

- `docs/audits/2026-05-22-agents-umbrella-phase-1.md`
- `agents/roles/phase-2-role-hardening.md`
- `agents/skills/phase-2-custom-skill-migration.md`
