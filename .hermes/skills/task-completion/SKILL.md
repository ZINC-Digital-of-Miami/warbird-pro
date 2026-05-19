---
name: task-completion
description: >
  Task completion checklist. Use when finishing any task to ensure all work is verified,
  documented, and reported before claiming completion. Invoke with /task-completion.
---

# Task Completion Checklist

Run this when you believe a task is done, BEFORE telling the user it's complete.

## Step 1: Run the Right Verification Gate

Do not blindly run `npm run build` for every task. Select the verification lane for the touched surface:

- **Hermes / agent setup work in Warbird:** run `git status --short`, `hermes config check`, `hermes doctor`, `hermes memory status`, `hermes lsp status`, `hermes hooks doctor`, and `tc_validator --fast`. If MCP was touched, also run `hermes mcp test <server>`.
- **`.pine` changes:** run the Pine compile/check path, `scripts/guards/pine-lint.sh <file>`, `scripts/guards/check-fib-scanner-guardrails.sh`, `scripts/guards/check-contamination.sh`, `scripts/guards/check-no-tv-force.sh`, and `npm run build`.
- **Frontend/runtime changes:** run `npm run build` and any relevant lint/test gate.
- **Python ETL/trainer/contract changes:** run the impacted `tests/ag/**` plus the minimum V9 contract tests named in `AGENTS.md`.

If the relevant gate fails, the task is NOT done.

## Step 2: Verify the Change

- Re-read every file you modified
- Confirm the change does what was requested — nothing more, nothing less
- Confirm no unrelated code was modified
- Confirm no new dependencies were added without approval

## Step 3: Check Hard Rules

- No mock/fake/demo data anywhere in changes
- No Prisma/Drizzle/ORM imports
- No legacy naming (`bhg_`, `BHG`, `mkt_futures_`)
- No `npx vercel --prod` in any scripts
- Correct table prefixes used
- Cron routes have all required boilerplate

## Step 4: Report to User

Provide a clear summary:
- **Files changed:** list every file with a one-line description
- **What was done:** describe the change
- **What was NOT done:** note anything out of scope that was observed but not touched
- **Concerns:** flag anything the user should know about

## Step 5: Wait for Confirmation

Do NOT proceed to the next task until the user confirms this one is complete.
