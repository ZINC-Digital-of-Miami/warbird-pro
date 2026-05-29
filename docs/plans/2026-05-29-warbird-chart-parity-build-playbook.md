# Warbird Chart Parity Plan-Build Brief

**Status:** Devin planning brief only. This is not the final implementation plan and not authorization to write runtime code.

**Purpose:** Prepare Devin to write the final multiphase artifacted chart parity plan from the local PR #14 authority, with PR #11 retained as source inventory only.

## Boundary

Codex is not writing the final plan in this file. Devin's next run must read the local authority and produce the final plan artifact.

The final plan must be written by Devin after reading:

- `AGENTS.md`
- `.devin/rules/01-project-overview.md`
- `.devin/rules/08-chart-parity-authority.md`
- `.devin/rules/09-review-sonic-feedback.md`
- `.devin/rules/10-session-insights.md`
- `.devin/knowledge-blueprint.md`
- `docs/handoffs/2026-05-29-devin-session-13c8-retrospective.md`
- `agents/skills/chart-parity-authority/SKILL.md`
- `docs/packet_plan_v2.4.1_correction_proposal.md`

`agents/skills/chart-parity-authority/SKILL.md` must be read top-to-bottom before Devin writes plan content. The closeout must state this explicitly.

## Current Authority State

- PR #11 is closed and retained as source inventory only. Do not merge it.
- PR #14 is closed as partially imported/superseded.
- Accepted PR #14 authority is local:
  - `agents/skills/chart-parity-authority/SKILL.md`
  - `docs/packet_plan_v2.4.1_correction_proposal.md`
- The broader PR #14 agent-platform purge is not accepted. Do not delete `.github/agents`, `.github/skills`, `.github/copilot-instructions.md`, `.github/workflows/copilot-review.yml`, or `.copilot-tracking/`.
- Legacy runtime cleanup is complete in local WIP. Do not reintroduce its script, aliases, process signatures, or documentation references.
- Vercel is not demoted until local replacement proof exists.
- Pine is not touched without explicit current-session approval.

## Devin Deliverable

Devin must create the final multiphase artifacted plan as a new or updated plan artifact under `docs/plans/`.

The plan must include:

- authority map: exact files read, PR #14 SHA, PR #11 SHA, and source-of-truth order
- coverage map: every section/ruling from `agents/skills/chart-parity-authority/SKILL.md` mapped to a phase, artifact, or explicit deferral
- PR #11 keep/discard map: what can be inspected, what is discarded, and what requires approval before reuse
- phase sequence: each phase has entry criteria, allowed files, forbidden files, expected artifacts, verification commands, Codex QA gate, stop condition, and approval needed
- artifact contract: exact paths or naming pattern for closeout packets, screenshots/browser proof, test logs, Sonic/Sonar findings, schema inventories, and rollback notes
- Session Insights section: category, actionable feedback, misleading Knowledge, repeated issues, and proposed rule/playbook/Knowledge updates
- next-run recommendation: the first implementation slice after Kirk/Codex QA accepts the plan

The plan must not include code changes as proof. It should identify future implementation work and the evidence each future phase must produce.

## Hard Stops For Devin

Stop and ask Kirk before:

- implementing dashboard/runtime code during the plan-build run
- merging all of PR #14
- deleting non-Devin agent surfaces
- touching Pine or anything under `indicators/`
- connecting Supabase
- enabling write automations
- demoting Vercel
- pushing

## Codex QA Gate For The Plan

Codex should verify after Devin returns the plan:

- the stated authority files exist locally
- PR #14 remains closed / partial-import only
- PR #11 remains closed / source-inventory only
- no dashboard/runtime/Pine implementation diff was introduced during the plan-build run unless Kirk explicitly expanded scope
- the plan coverage map accounts for the full `agents/skills/chart-parity-authority/SKILL.md`
- `.devin/wiki.json` parses if touched
- `.devin/environment-blueprint.yaml` parses if touched
- `git diff --check`
