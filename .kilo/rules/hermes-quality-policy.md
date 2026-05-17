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
7. Block package-install commands by default in Warbird hook policy unless
   explicit human approval is given in-session.
8. Treat Supabase edge runtime as Deno-first and keep DuckDB/Postgres SQL lanes
   separated.

## Required Hermes Validation For Config/Skill Changes

Run all of the following before claiming completion:

1. `kilo debug config`
2. `hermes config check`
3. `hermes doctor`
4. `hermes memory status`
5. `hermes lsp status`
6. `hermes hooks doctor`

`tc_validator` is required as the final completion gate:

7. `tc_validator --fast` for docs/config-only work
8. `tc_validator` (full) for code/Pine/trainer/ETL/contract work

If `tc_validator` is missing, install with `./scripts/setup/install_tc_tracker.sh`
and rerun. If install is blocked, completion is blocked.

## Hard Rules

- No secret material in repo files.
- No silent enablement of gateway/cron/background messaging lanes.
- No Hermes skill override of `AGENTS.md`, `CLAUDE.md`, or active contract docs.
- No claim of validation pass without command evidence.
