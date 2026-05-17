# Warbird Validation Matrix

Use the smallest validator set that actually covers the touched surface. Do not
claim a validator passed unless it was run and its result is known.

## Universal Pre-Edit Checks

- `git status --short`
- Read the active docs for the touched surface.
- Confirm the work does not start training/modeling, edit Pine, push, install
  dependencies, or run TradingView automation unless explicitly requested.
- If package installs are explicitly requested, capture explicit human approval
  in the session before running `npm/pnpm/yarn add`, `pip install`, or
  `deno add`.

## Kilo / Guardrail / Config Files

When touching `.kilo/**`, `kilo.json*`, Kilo commands, Kilo agents, or Kilo rules:

1. Validate JSON/JSONC/YAML syntax for changed config files.
2. Run `kilo debug config` if global Kilo config is valid.
3. If global Kilo config blocks validation, report the external blocker and still
   validate the changed project config locally.
4. Check that no secrets/API keys were written to repo files.

## Hermes Config / Skills

When touching Hermes config, hooks, skills, or Hermes integration:

1. Keep secrets in `~/.hermes/.env`, not `config.yaml` or repo files.
2. Keep `approvals.mode` fail-closed (`manual` or stricter). Do not enable YOLO
   by default.
3. Keep `hooks_auto_accept: false`.
4. Keep high-risk toolsets disabled unless explicitly needed for the task.
5. Run all Hermes health checks:
   - `hermes config check`
   - `hermes doctor`
   - `hermes memory status`
   - `hermes lsp status`
   - `hermes hooks doctor`

## Documentation-Only Changes

For docs/rules only:

1. Check links/paths cited in changed files exist when they are local paths.
2. Check no active rule contradicts `AGENTS.md` authority.
3. Run repository text guards if available and relevant.
4. Run `npm run build` before push or when the changed docs affect app-rendered
   content. If skipped for pure agent-rule docs, state why.

## Pine Changes

If any `.pine` file is touched, all are mandatory:

1. Pine facade compile check.
2. `./scripts/guards/pine-lint.sh <file>`
3. `./scripts/guards/check-fib-scanner-guardrails.sh`
4. `./scripts/guards/check-contamination.sh`
5. `./scripts/guards/check-no-tv-force.sh`
6. `npm run build`

Do not run indicator/strategy parity unless a new strategy harness has explicit
approval.

## V9 Core ETL / Trainer / Provenance Changes

When touching `scripts/ag/train_v9_locked.py`, `scripts/ag/shap_v9.py`,
`scripts/ag/monte_carlo_v9.py`, `scripts/duckdb_local/workspaces/warbird_pro_core/**`,
`tests/ag/**`, or V9 contract docs:

1. Run impacted tests under `tests/ag/**`.
2. Minimum contract lane:
   - `pytest tests/ag/test_v9_core_indicator_input_contract.py -q`
   - `pytest tests/ag/test_v9_core_training_targets.py -q`
3. Validate no Postgres dependency was introduced into the active V9 pipeline.
4. Validate no raw training data or full research outputs are routed to cloud
   Supabase.
5. Do not launch real training unless explicitly requested.

## Supabase / Cloud Changes

When touching `supabase/**`, API routes, RLS, Edge Functions, or cloud DDL:

1. Verify Supabase Edge changes are Deno-compatible and do not rely on
   Node-native module behavior.
2. Keep backend automation logic in Supabase lanes unless an explicit
   architecture change was approved.
3. Keep DuckDB/Python OLAP SQL logic out of Supabase OLTP migration/query paths.
4. Use `supabase/migrations/` for cloud DDL.
5. Verify RLS expectations for cloud tables.
6. Verify cron routes validate `CRON_SECRET`, export `maxDuration = 60`, and log
   to `job_log` on success and failure.
7. Run `npm run lint` and `npm run build` for frontend/API changes.

## Removed Quality Workbook

Quality workbook runtime/artifact surfaces were removed from this repo. Do not
recreate or route execution through quality-playbook runners unless explicitly
requested.

## `tc_validator` Rule

`tc_validator` is the completion gate for Warbird Kilo/Hermes work.

1. Run `tc_validator --fast` for docs/config-only work, or `tc_validator` (full)
   for code/Pine/trainer/ETL/contract work.
2. If `tc_validator` fails, do not claim completion; fix issues and rerun.
3. If `tc_validator` is missing, install with
   `./scripts/setup/install_tc_tracker.sh`, then rerun `tc_validator`.
4. If install is blocked, the task remains blocked; do not claim completion.
