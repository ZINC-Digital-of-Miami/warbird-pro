# Chart Parity Implementation Workflow

Suggested macro in Devin: `!warbird-chart-parity`

Use this playbook for Warbird local dashboard work based on the locally imported Packet v2.4.1 / PR #14 authority.

If the task is the 2026-05-29 plan-build run, do not implement from this playbook yet. First use `docs/plans/2026-05-29-warbird-chart-parity-build-playbook.md` to write the final multiphase artifacted plan after reading `agents/skills/chart-parity-authority/SKILL.md` top-to-bottom.

## Procedure

1. Read `AGENTS.md`, `.devin/rules/01-project-overview.md`, `.devin/rules/08-chart-parity-authority.md`, and `agents/skills/chart-parity-authority/SKILL.md` if present.
2. Confirm the task is packet-approved implementation, not packet redesign.
3. Inventory the current working tree with `git status --short --untracked-files=all`.
4. Identify which exact local packet surfaces are being used and whether any PR #11 source-inventory code is being inspected.
5. Use `components/charts/LiveMesChart.tsx` as the visual chart source for retained chart behavior.
6. Use approved `engine/` surfaces only where the packet allows them.
7. Preserve Nexus as approved: dropped-in logic minus TradingView-centric items, standard volume for now, adapter gaps documented honestly.
8. Make the smallest scoped change set.
9. Run `npm run lint` and `npm run build` for dashboard/runtime changes.
10. Run focused Python tests when `engine/` behavior changes.
11. Return a closeout packet with files changed, authority read, PR surfaces used, adapter gaps, verification evidence, and remaining blockers.

## Specifications

- Dashboard work remains traceable to Packet v2.4.1 / imported PR #14 authority.
- Retained chart behavior comes from `components/charts/LiveMesChart.tsx`.
- PR #11 dashboard frontend is not carried forward unless a packet step explicitly approves that surface.
- Any incomplete data equivalence is named as an adapter gap.
- Verification failures keep the gate blocked.

## Advice

- Treat green Devin Review and green Sonic as useful signal, not acceptance.
- Keep implementation slices small enough that Codex QA can verify them from local files and commands.
- Use exact command outputs in the closeout rather than narrative confidence.
- Prefer documenting an adapter gap over hiding it with a proxy.

## Forbidden Actions

- Do not merge PR #11 as-is.
- Do not edit Pine without explicit current-session approval.
- Do not claim Vercel is demoted before replacement proof exists.
- Do not represent standard volume, candle-body delta, or other proxy data as footprint-equivalent.
- Do not auto-push or auto-merge.

## Required From User

- Explicit approval before Pine edits, Vercel demotion, Supabase connection, pushing, or accepting deferred PR #14 agent-platform deletions.
- Clarification if Packet v2.4.1 conflicts with a newer Kirk ruling.
