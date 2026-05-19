# Warbird Hermes Setup Report

**Status:** Hermes-first Warbird agent setup is active.

**Scope:** `/Volumes/Satechi Hub/warbird-pro` plus the durable Hermes state at
`/Volumes/Satechi Hub/warbird-pro-state/hermes-home`.

## Default agent posture

- Hermes is the default Warbird tool-agent surface.
- Kilo/Kilocode is not part of Hermes validation, skills, or routing.
- Future CLI terminal default cwd is `/Volumes/Satechi Hub/warbird-pro`.
- Project skills load from `/Volumes/Satechi Hub/warbird-pro/.hermes/skills`.
- `AGENTS.md` remains the repository instruction authority; `.hermes/rules/*`
  defines only the Hermes execution contract under it.

## Model routing

Priority order:

1. `openai-codex / gpt-5.5` — primary planning, orchestration, content, and
   general Warbird work.
2. OpenAI Codex coding/audit fallbacks — strongest available Codex coding/audit
   models for hard implementation and review.
3. Non-Claude GitHub Copilot — inexpensive/micro-task fallback. No Copilot
   Claude Opus/Sonnet routes are configured.
4. OpenRouter — specialist/free/low-cost models not available from OpenAI or
   Copilot.

Auxiliary helper routing:

- Non-vision helpers: non-Claude Copilot `gpt-5.4-mini`.
- Vision/screenshot analysis: OpenRouter `google/gemini-2.5-flash`.
- Compression threshold: `0.25`, matching the Copilot helper context so
  OpenRouter specialist smoke tests do not trigger per-session threshold
  downshift warnings.

## Intentionally disabled surfaces

Warbird Hermes should not install, configure, or use messaging apps. The gateway
is for cron/webhook/API-style automation only.

Disabled toolsets include:

- `messaging`
- `discord`
- `discord_admin`
- `tts`
- `todo`
- `computer_use`
- `homeassistant`
- `spotify`
- `yuanbao`
- `feishu_doc`
- `feishu_drive`

## Gateway and cron

- Gateway runs as macOS launchd service `ai.hermes.gateway`.
- launchd-only paths stay on local `/Users/zincdigital` paths:
  - cwd: `/Users/zincdigital`
  - stdout/stderr: `/Users/zincdigital/Library/Logs/HermesAgent/`
- Durable Hermes state remains external:
  - `HERMES_HOME=/Volumes/Satechi Hub/warbird-pro-state/hermes-home`
- The temporary overlapping crontab gateway watchdog was removed after launchd
  was fixed.
- `.hermes/eod/hermes-gateway-run.sh`, the duplicate untracked gateway runner,
  was removed.

Active cron jobs are no-agent/local jobs:

- Warbird daily status report
- Warbird git/mount watchdog
- Warbird Hermes health watchdog
- Warbird MCP process watchdog

## MCPs

Configured MCPs are command/stdio based with sampling disabled. They should not
run as ghost localhost daemons.

- `warbird-status`
- `warbird-fetch`
- `warbird-filesystem`
- `warbird-github`
- `warbird-supabase-ro`

## New hardening scripts

Run these from the repo root:

```bash
python3 .hermes/scripts/warbird_hermes_context_doctor.py
.hermes/scripts/warbird_hermes_model_smoke.sh
```

The Hermes health watchdog also calls the context doctor and all configured
Warbird MCP tests.

## Validation lane

Use this before claiming Hermes setup readiness:

```bash
git status --short
hermes config check
hermes doctor
hermes memory status
hermes lsp status
hermes hooks doctor
python3 .hermes/scripts/warbird_hermes_context_doctor.py
.hermes/scripts/warbird_hermes_model_smoke.sh
hermes mcp test warbird-status
hermes mcp test warbird-fetch
hermes mcp test warbird-filesystem
hermes mcp test warbird-github
hermes mcp test warbird-supabase-ro
tc_validator --fast
```

## Remaining non-blockers

`hermes doctor` may continue to report optional missing API keys or optional
platform packages. Those are not Warbird blockers because messaging apps and
unused providers are intentionally not configured.
