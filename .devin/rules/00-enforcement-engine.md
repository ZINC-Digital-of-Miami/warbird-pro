# Enforcement Engine — Read First, Every Session

This is the highest-priority rule. It describes hard enforcement gates that
**cannot be overridden by Devin's own judgment, platform defaults, or
chain-of-thought reasoning.** Only Kirk's explicit current-session approval
can override these gates.

## Architecture

Knowledge notes are advisory context injection. They are not enforcement.
To close that gap, Warbird has a shell-level enforcement layer that runs
**before** the LLM can act:

| Script | What it blocks | When it runs |
|--------|---------------|-------------|
| `warbird-knowledge-enforcement.sh` | Knowledge note violations (legacy training, fake data, force push, V7/V8 refs, unauthorized automation, Vercel demotion, Sonic auto-fix) | pre-commit, pre-push, manual |
| `warbird-file-protection.sh` | File deletions in protected paths, .gitignore of governance dirs, plan overwrites with older content, retired surface reactivation | pre-commit, pre-push, manual |
| `warbird-agent-precheck.sh` | Orchestrator that runs both enforcement scripts plus quality-lane checks | pre-commit, pre-push, manual |

These scripts produce `exit 1` on violation. The LLM cannot bypass them.

## What This Means For Devin

1. **Before every commit**, the pre-commit hook runs `warbird-agent-precheck.sh`
   which runs the enforcement engine. If your changes violate a Knowledge note,
   the commit is blocked. You cannot work around this with `--no-verify` because
   that flag is itself a violation.

2. **If a Knowledge note says X and Devin's platform says Y**, the Knowledge
   note wins at the shell level even if the LLM decides otherwise. The scripts
   enforce the Knowledge notes regardless of what the model's chain-of-thought
   concludes.

3. **The enforcement manifest** at `scripts/guards/enforcement-manifest.json`
   is the machine-readable source of truth for what is blocked. Read it.

## Enforcement Manifest Quick Reference

Protected from deletion:
- `docs/plans/`, `docs/handoffs/`, `agents/skills/`
- `docs/contracts/`, `docs/runbooks/`
- `.devin/rules/`, `.devin/playbooks/`

Protected from .gitignore:
- `docs/`, `agents/`, `.devin/`

Blocked actions:
- `git push --force` (any form)
- `--no-verify`
- Legacy/full-zoo training invocation
- Fake/mock footprint data
- Sonic auto-fix without defect map
- Write automation without manual-first pass
- Vercel infrastructure deletion
- V7/V8 retired surface references in new code

## Stop-And-Ask Triggers

If you encounter any of these situations, **STOP immediately** and ask Kirk:

- You are about to modify a governance file (AGENTS.md, CLAUDE.md, WARBIRD_MODEL_SPEC.md) by more than 20%
- You are about to delete any file in a protected path
- You are about to add a protected path to .gitignore
- You are about to edit a Pine file (indicators/*.pine)
- A pre-commit hook fails and you are tempted to retry with different flags
- Your task conflicts with a Knowledge note
- Kirk says "STOP" (in any form, any case) — kill all background processes immediately, then respond

## Session f6fe99cc Lessons (2026-05-29)

This enforcement engine exists because session f6fe99cc demonstrated that:

1. Knowledge notes were injected but overridden by Devin's platform defaults
2. Devin's chain-of-thought explicitly chose to ignore "Main Only And Push Approval"
3. File overwrites happened because Devin didn't diff against main before acting
4. Background processes kept running after Kirk escalated 4 times
5. "Fixing" mistakes autonomously (without asking) made things worse

Every check in the enforcement scripts targets one of these specific failure modes.
