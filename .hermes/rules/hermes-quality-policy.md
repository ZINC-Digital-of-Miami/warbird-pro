# Warbird Hermes Quality Policy

**Status:** Active Hermes authority for Warbird
**Scope:** Hermes config, hooks, skills, MCPs, gateway/cron, memory, ACP, and local Hermes tooling

Hermes is its own Warbird execution layer. `AGENTS.md` remains the repo
instruction authority; this file defines only the Hermes execution contract
beneath it.

## Primary Model Lane

- Primary planning/brainstorming/content model path: `openai-codex / gpt-5.5`.
- Primary hard-coding and audit path: OpenAI Codex OAuth through Hermes Codex
  Responses mode, using the strongest available Codex coding/audit model for
  the task (currently `openai-codex / gpt-5.3-codex` as the first hard-coding
  fallback).
- Config values:
  - `provider: openai-codex`
  - `model: gpt-5.5`
  - `api_mode: codex_responses`
  - `base_url: https://chatgpt.com/backend-api/codex`
- Provider priority order is **OpenAI Codex → GitHub Copilot → OpenRouter**.
- Use Copilot for inexpensive/micro tasks and models available through the
  user's Copilot subscription, but **do not route Copilot work through Claude
  Opus or Claude Sonnet models**. Copilot Claude Haiku may be used only if
  explicitly selected later; current Warbird defaults prefer GPT/Gemini Copilot
  models instead.
- Use OpenRouter for models not available through OpenAI/Copilot and for strong
  free/low-cost specialists after the OpenRouter account is funded. Current
  targeted OpenRouter families include Kimi K2.6, Hy3 Preview, DeepSeek V4
  Pro/Flash, Gemini 2.5 Flash/Flash-Lite, GPT-OSS, Qwen3 Coder, Nemotron, and
  GLM free/low-cost variants.
- Nous Portal OAuth is available for the user's free Nous account, but it is not
  ahead of the configured Warbird priority order unless explicitly promoted.
- Current fallback order starts with `openai-codex / gpt-5.3-codex`,
  `openai-codex / gpt-5.4`, then non-Claude Copilot GPT/Gemini models, then
  OpenRouter specialists/free models.
- Non-vision auxiliary helper calls use non-Claude Copilot (`gpt-5.4-mini`) to
  keep the default helper path stable and zero-monthly-fee; vision remains
  pinned to OpenRouter Gemini 2.5 Flash for screenshot/image analysis.
- Do not describe fallback success as primary-model readiness.

Primary-readiness smoke tests:

```bash
hermes chat -Q --provider openai-codex -m gpt-5.5 --ignore-rules \
  -q 'Reply exactly: OPENAI_CODEX_CONNECTED'
hermes chat -Q --provider openai-codex -m gpt-5.5 -t file,terminal --ignore-rules \
  -q 'Reply exactly: OPENAI_CODEX_TOOLS_CONNECTED. Do not call any tools.'
```

## Hermes Baseline Requirements

1. Keep secrets in `~/.hermes/.env` only. Never commit tokens or service keys.
2. Keep `approvals.mode` fail-closed (`manual` or stricter).
3. Keep `hooks_auto_accept: false`.
4. Keep high-risk toolsets disabled unless explicitly approved for a task.
5. `computer_use` stays disabled for Warbird by default because terminal,
   browser, file tools, and filesystem MCP cover host access without the
   TradingView automation risk.
6. Gateway may run as a persistent launchd service for Hermes cron, webhooks,
   and API-style automation only. Do **not** install, configure, or use messaging
   app adapters for Warbird Hermes.
7. Scheduled Warbird watchdog/report jobs may run through the Hermes gateway cron
   ticker, but they must stay lightweight and `--no-agent` unless explicitly
   approved.
8. No Hermes skill may override `AGENTS.md`, `CLAUDE.md`, or active contract docs.
9. Self-improvement means memory curation and skill drafts. It is not model
   weight training or autonomous promotion of unreviewed skills.
10. The `todo` toolset stays disabled for Warbird Hermes sessions because ACP
   context compaction can duplicate visible plan/checklist cards. Use concise
   prose progress instead.

## Enabled Warbird Tool Profile

Safe daily work keeps these enabled:

- `terminal`
- `file`
- `code_execution`
- `skills`
- `memory`
- `session_search`
- `clarify`

Approved for this Hermes setup work and normal Warbird inspection:

- `web` using fetch-only/no-signup tooling where possible
- `browser` using local browser automation
- `image_gen` through the configured OpenAI/Codex image path
- `cronjob` for bounded scheduled jobs
- `vision` with auxiliary routing pinned to OpenRouter Gemini 2.5 Flash for
  image/screenshot analysis

Still disabled by default:

- `computer_use`
- `delegation`
- `messaging`
- `tts`
- `video`
- `video_gen`
- `homeassistant`
- `spotify`
- `yuanbao`
- `moa`

## MCP Policy

Configured MCPs must be added one at a time and tested before use:

1. filesystem MCP rooted at `/Users/zincdigital` and `/Volumes/Satechi Hub`
2. GitHub MCP using `GITHUB_TOKEN` from `~/.hermes/.env`
3. Supabase MCP scoped to the Warbird project and read-only by default
4. fetch MCP for account-free URL retrieval
5. custom Warbird status MCP under `.hermes/mcp/warbird-status/`

Do not enable mutating Supabase MCP tools by default. Cloud Supabase remains
runtime/support only and must not receive raw training data, labels, or full
research artifacts.

## ACP Policy

- `hermes acp --check` proves CLI-side ACP readiness only.
- VS Code end-to-end ACP readiness requires the ACP Client panel to connect to
  `Hermes Agent` and return exactly `VSCODE_ACP_READY`.
- The local `warbird-hermes` VS Code extension exists only as a click target for
  Hermes ACP. It must not bypass ACP permissions or Hermes approval settings.

## Required Hermes Validation

For Hermes config, hook, skill, MCP, gateway, ACP, or integration work, run:

```bash
git status --short
hermes config check
hermes doctor
hermes memory status
hermes lsp status
hermes hooks doctor
tc_validator --fast
```

If the work claims primary-model readiness, also run the OpenAI Codex smoke
tests above and confirm exact responses without fallback.

If the work claims VS Code ACP readiness, verify the ACP Client panel returns
`VSCODE_ACP_READY`.

This policy does not define or require validation for any non-Hermes agent
surface.

## Hard Rules

- No secret material in repo files.
- No silent enablement of gateway, messaging, delegation, or computer-use lanes.
- No package-install commands without explicit approval in the current session.
- No claim of validation pass without command evidence.
- No quality-playbook runtime resurrection.
- No TradingView recovery automation through Hermes.
