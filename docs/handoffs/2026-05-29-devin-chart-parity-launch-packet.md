# Devin Chart Parity Launch Packet

**Date:** 2026-05-29
**Repo:** `/Volumes/Satechi Hub/warbird-pro`
**Purpose:** Next bounded Devin planning run after PR #11 closure, PR #14 partial import, and legacy runtime cleanup. This prepares Devin to write the final multiphase artifacted plan; it is not an implementation launch.

## Current State

- PR #11 is closed and retained as source inventory only. Do not merge it.
- PR #14 is closed as partially imported/superseded.
- The accepted PR #14 artifacts are local:
  - `agents/skills/chart-parity-authority/SKILL.md`
  - `docs/packet_plan_v2.4.1_correction_proposal.md`
- The chart authority skill is registered in `agents/manifest.yaml` and
  `agents/skills/README.md`.
- The legacy runtime cleanup is complete in local WIP; do not reintroduce its
  script, aliases, process signatures, or documentation references.
- The broader PR #14 agent-platform purge remains deferred; do not delete
  `.github/agents`, `.github/skills`, `.github/copilot-instructions.md`,
  `.github/workflows/copilot-review.yml`, or `.copilot-tracking/`.

## Paste To Devin

Use this exact scope. Do not expand it.

```text
We are starting the Warbird Pro chart parity plan-build lane.

Read these first:
- AGENTS.md
- docs/plans/2026-05-29-warbird-chart-parity-build-playbook.md
- .devin/rules/01-project-overview.md
- .devin/rules/08-chart-parity-authority.md
- .devin/rules/09-review-sonic-feedback.md
- .devin/rules/10-session-insights.md
- .devin/knowledge-blueprint.md
- docs/handoffs/2026-05-29-devin-session-13c8-retrospective.md
- agents/skills/chart-parity-authority/SKILL.md
- docs/packet_plan_v2.4.1_correction_proposal.md

Mission for this run:
Write the final multiphase artifacted chart parity plan from the local PR #14 authority. Before writing any plan content, read `agents/skills/chart-parity-authority/SKILL.md` top-to-bottom and read `docs/packet_plan_v2.4.1_correction_proposal.md`. Do not summarize from memory or prior Devin output.

Scope:
- Treat PR #14 authority as already imported locally.
- Treat PR #11 dashboard frontend as discarded. Use it only as source inventory when explicitly cited by the packet.
- Start from `components/charts/LiveMesChart.tsx` for retained Lightweight Charts behavior.
- Produce a plan artifact only. Do not implement dashboard/runtime changes in this run.
- Convert the full PR #14 authority into a sequenced plan with phases, deliverables, acceptance evidence, stop conditions, and artifact paths.
- Keep engine integration, Databento trades-side aggregation, Nexus adapter work, Supabase audit, and Vercel demotion as planned phases only. Do not execute them.
- Include a Session Insights section for the planning run: expected category, what feedback to collect, and how misleading Knowledge/repeated issues will be routed.

Forbidden:
- Do not merge PR #11 as-is.
- Do not reopen PR #14 or accept its broader agent-platform purge.
- Do not implement code in this run unless Kirk explicitly changes the scope after reviewing the plan.
- Do not run training/modeling.
- Do not edit Pine.
- Do not touch `indicators/`.
- Do not migrate Supabase.
- Do not demote Vercel.
- Do not push without explicit approval.
- Do not auto-apply Sonic fixes.

Return a closeout packet with:
- files changed
- exact authority files read
- explicit confirmation that `agents/skills/chart-parity-authority/SKILL.md` was read top-to-bottom before plan writing
- PR #14 SHA and PR #11 SHA
- confirmation that PR #14 remains partial-import only
- confirmation that PR #11 remains source inventory only
- validation commands and outcomes
- path to the final multiphase artifacted plan Devin wrote
- plan coverage map showing every PR #14 section/ruling is either represented in the plan or explicitly deferred with reason and owner
- dashboard baseline keep/discard map as a planning artifact, not an implementation diff
- proposed Knowledge notes for approval if the run surfaces a new reusable rule
- Session Insights Review: category, actionable feedback, misleading Knowledge, repeated issues, and any rule/playbook/Knowledge/blueprint updates needed
- next task recommendation after Kirk/Codex QA reviews the plan
```

## Codex QA Acceptance Gate

Codex should verify:

- `git status --short --branch --untracked-files=all`
- `test -f agents/skills/chart-parity-authority/SKILL.md`
- `test -f docs/packet_plan_v2.4.1_correction_proposal.md`
- `.devin/wiki.json` parses if present
- `.devin/environment-blueprint.yaml` parses if present
- `git diff --check`

If Devin modifies dashboard/runtime code, Codex QA must also run `npm run lint`
and `npm run build`, plus browser smoke if a local runtime is started.

## Stop Conditions

Stop and ask Kirk before:

- merging all of PR #14
- deleting non-Devin agent surfaces
- touching dashboard implementation during the plan-build run
- touching Pine
- connecting Supabase
- enabling write automations
- pushing
