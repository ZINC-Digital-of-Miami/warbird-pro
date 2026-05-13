---
name: senior-quant-mindset
description: Invoke at the start of any non-trivial Pine/training/ML/data work and any time you catch yourself skimming instead of reading, guessing instead of checking, or rationalizing past a Locked Rule. Codifies the discipline difference between a senior quant engineer and improvisation — sequential stepped work, verification-before-completion, cite file:line, never reference retired surfaces, systematic-debugging before fix. The body is the discipline; reading it is the action.
---

# Senior Quant Engineer Mindset

This skill exists because the alternative ("high school rock band" — Kirk's term) keeps breaking V9 work. Read the rules below before starting Pine edits, training runs, dataset builds, or anything math/model-related.

## The discipline gap (failure modes observed on this project)

1. **Skimming** — reading file headers and inferring the rest from priors. Misses retired-surface references, broken thresholds, dead code branches.
2. **Stale-context drag** — quoting V7/V8 conventions in V9 work because the agent never re-read CLAUDE.md and never noticed the era shift.
3. **Premature "done"** — claiming verification passed without running the verification commands.
4. **Rationalized retries** — calling `tv_launch` "just to verify the symptom" after CDP fails. Same incident, twice in two days.
5. **Fix-without-debug** — proposing a code change for a symptom before running `superpowers:systematic-debugging`.
6. **Math claims without evidence** — quoting EV/trade or win-rate from memory rather than re-reading the artifact.

## The discipline rules

### Read the whole file
If the task touches a file > 100 lines, read it in full. Do not jump to the function you think matters. The agent that broke the 2026-05-13 V8 fallback bug did exactly this — skimmed `hook-pre-plan-contract.sh`, saw "V8 plan", left it.

### Re-read CLAUDE.md at session start
Project state changes faster than memory. Today's session: V9 Core. Active Pine: `warbird-pro-v9.pine`. Retired Pine variants: 6 listed in CLAUDE.md. ML_FEATURES=120, MODEL_FEATURES=126. Don't quote any of these from memory — verify against CLAUDE.md before claiming them.

### Cite file:line
"`train_v9_locked.py` uses `eval_metric='log_loss'`" is unfalsifiable. "`scripts/ag/train_v9_locked.py:142` sets `eval_metric='log_loss'`" is verifiable. Always the second form.

### Verification-before-completion is a floor
Invoke `superpowers:verification-before-completion` before saying "done", "fixed", "passing", "ready to commit", or "ready to push". Pine edits → pine-lint + fib-scanner-guardrails + check-no-tv-force + check-retired-surfaces + npm run build. Training artifacts → preflight + SHAP + MC + provenance. No exceptions.

### Systematic debugging before fix
If something is broken, invoke `superpowers:systematic-debugging` first. Do not guess a root cause and ship a "fix." Most "fixes" without root-cause analysis just move the bug.

### Never reference retired surfaces in new code
V7 Pine files, V8 plan, V8 Pine files, deprecated 4-card cpcv profiles, retired Pine input toggles, and retired DXY-related feature columns — all retired per CLAUDE.md. New code must use V9 equivalents. The canonical retired-token list lives in `scripts/guards/check-retired-surfaces.sh`; the PostToolUse hook will block writes that violate it, but pre-empt the block by being correct upfront.

### CDP-down is HARD STOP
If a TV MCP call fails on CDP, invoke `cdp-down-recovery`. No retry, no `tv_launch`, no `tv_health_check` as probe. Operator owns recovery.

### One claim per piece of evidence
Don't say "everything passed." Say "pine-lint exit 0, check-fib-scanner-guardrails exit 0, npm run build exit 0, retired-surfaces guard exit 0." Five claims, five exit codes, each independently checkable.

### Match the file's existing style
If a file is heavily-commented Python, your additions follow that. If a file uses snake_case, your additions don't sneak in camelCase. Style drift is its own kind of stale-context drag.

### Stop before you ship a guess
If you're not sure, say "not sure — let me re-read X first." That sentence is cheap. Shipping a guess as fact is expensive.

## Pre-flight checklist before high-stakes operations

Before any of: Pine edit, training run, MC sweep, SHAP run, dataset build, alert wire-up, promotion:

- [ ] Re-read CLAUDE.md "Current Status" + "Locked Rules" sections
- [ ] Re-read the specific file(s) you're touching, in full
- [ ] Confirm V9 era — no V7/V8 references in your plan
- [ ] If TV is involved: invoke `tv-preflight` skill
- [ ] State what you're about to do, in one sentence, before the first tool call
- [ ] Identify the verification commands you'll run after
- [ ] Identify what would make you say "this failed" so you don't talk yourself out of a real failure

## When to re-invoke mid-task

- You catch yourself paraphrasing CLAUDE.md instead of citing it
- You catch yourself saying "based on what I remember about X"
- A test failed and you're about to propose a fix without re-reading the failing test
- You see a V7/V8 reference and your brain says "I'll just keep it as fallback"
