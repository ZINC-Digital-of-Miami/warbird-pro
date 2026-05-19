# Warbird Hermes Validation Matrix

Use the smallest validator set that covers the Hermes surface touched. Do not
claim a validator passed unless it actually ran and the result is known.

## Universal Hermes Pre-Edit Checks

- `git status --short`
- Read `AGENTS.md` plus this file and `.hermes/rules/hermes-quality-policy.md`.
- Confirm the work does not edit Pine, start training/modeling, run
  TradingView automation, write secrets to repo files, or broaden Supabase/cloud
  scope.
- If package installs are required for MCPs or VS Code packaging, the current
  chat must contain explicit approval before running the install.

## Hermes Config / Hooks / Skills / Integration

When touching `~/.hermes/config.yaml`, `~/.hermes/.env`,
`~/.hermes/agent-hooks/**`, `.hermes/**`, Hermes skills, MCPs, gateway, ACP, or
Hermes integration docs:

1. Keep secrets in `~/.hermes/.env`, not `config.yaml` or repo files.
2. Keep `approvals.mode` fail-closed (`manual` or stricter).
3. Keep `hooks_auto_accept: false`.
4. Keep `computer_use`, `messaging`, and app/media surfaces disabled unless a
   separate explicit task approves them. `delegation` may be enabled only for
   bounded Hermes-first subagent workflows; it must not imply Kilo routing.
5. Run:
   - `hermes config check`
   - `hermes doctor`
   - `hermes memory status`
   - `hermes lsp status`
   - `hermes hooks doctor`
   - `python3 .hermes/scripts/warbird_hermes_context_doctor.py`
6. Run `tc_validator --fast` for docs/config-only Hermes work.
7. If claiming primary model readiness, run `.hermes/scripts/warbird_hermes_model_smoke.sh`
   and confirm no fallback or Copilot Claude Opus/Sonnet route.
8. If claiming VS Code ACP readiness, verify ACP Client panel response
   `VSCODE_ACP_READY`.

## MCP Work

For each MCP server added or changed:

1. Configure one MCP at a time.
2. Keep Supabase scoped/read-only unless a separate task explicitly approves
   mutation.
3. Run `hermes mcp test <name>`.
4. Record any auth blockers honestly. OAuth-required MCPs are not considered
   fully ready until login succeeds.
5. Keep filesystem roots intentional and documented.

## Gateway / Cron / EOD Cleanup

When touching gateway or cron automation:

1. Gateway may run persistently only as the Hermes launchd service for cron,
   webhooks, or API-style automation; messaging app adapters stay disabled.
2. `hooks_auto_accept` remains `false`.
3. EOD cleanup must not be a Hermes pre/post tool hook.
4. EOD cleanup must not kill TradingView.
5. Avoid overlapping schedulers: do not keep a separate crontab gateway watchdog
   or legacy cron-tick LaunchAgent active when `ai.hermes.gateway` owns the
   scheduler.
6. Validate with:
   - `hermes gateway status`
   - `hermes cron status`
   - `python3 .hermes/scripts/warbird_hermes_context_doctor.py`
   - EOD dry-run script

## Documentation-Only Hermes Changes

For docs/rules only:

1. Check local links/paths cited in changed files exist.
2. Check the rule does not contradict `AGENTS.md`.
3. Run repository text guards if available and relevant.
4. Run `npm run build` before push if the docs claim operational truth.
5. Run `tc_validator --fast`.

## Final Gate

`tc_validator` is the completion gate for Warbird Hermes work:

- `tc_validator --fast` for docs/config-only work.
- `tc_validator` full for code/Pine/trainer/ETL/contract work.

If `tc_validator` is missing, install with `./scripts/setup/install_tc_tracker.sh`
and rerun. If install is blocked, completion is blocked.
