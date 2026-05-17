# Hermes-First Quality Policy

This file records the active Warbird quality policy after decommissioning and
removing the local quality-playbook runtime/artifact surface.

## Current State

- Hermes is installed and managed at `~/.hermes/hermes-agent`.
- Canonical CLI path is `~/.local/bin/hermes`.
- Warbird guardrail hooks are active:
  - `~/.hermes/agent-hooks/warbird-terminal-guard.sh`
  - `~/.hermes/agent-hooks/warbird-validator-inject.sh`
- Quality workbook runtime surfaces are retired.
- Local quality workbook runtime/artifact files were intentionally removed.

## Decision

Warbird runs a Hermes-first quality lane.

- Keep guardrails in Hermes config + shell hooks.
- Use `.kilo/rules/validation-matrix.md` as the validator routing authority.
- Do not route new work through quality-playbook runners or phase workflows.

## Hermes Baseline Requirements

1. Keep secrets in `~/.hermes/.env` only.
2. Keep `approvals.mode` fail-closed (`manual` or stricter).
3. Keep `hooks_auto_accept: false`.
4. Keep high-risk automation toolsets disabled by default (browser/computer use,
   web crawling, delegation, messaging, cron automation) unless explicitly
   required for a task.
5. Keep Warbird skill source canonical at
   `/Volumes/Satechi Hub/warbird-pro/.kilocode/skills`.
6. Do not enable YOLO/approval-off modes for Warbird sessions.

## Required Hermes Validation For Config/Skill Changes

Run all of the following before claiming completion:

1. `kilo debug config`
2. `hermes config check`
3. `hermes doctor`
4. `hermes memory status`
5. `hermes lsp status`
6. `hermes hooks doctor`

If a named validator is requested but unavailable (for example `tc_validator`),
state that explicitly and run the closest concrete checks from the validation
matrix.

## Hard Rules

- No secret material in repo files.
- No silent enablement of gateway/cron/background messaging lanes.
- No Hermes skill override of `AGENTS.md`, `CLAUDE.md`, or active contract docs.
- No claim of validation pass without command evidence.
