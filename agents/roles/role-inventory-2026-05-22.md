# Role Inventory (2026-05-22)

## Source Surface Reviewed

- `.github/agents/*.agent.md` (snapshot before phase-1 pruning)

## Decisions

Kept active now:

1. `Quant Analyst.agent.md` -> canonicalized as `agents/roles/quant-analyst.agent.md`

Pending Phase 2 hardening (not active; pruned from `.github/agents` and must
be rebuilt in `agents/roles/` before any reintroduction):

1. `agent-governance-reviewer.agent.md`
2. `startup-reviewer.agent.md`
3. `se-system-architecture-reviewer.agent.md`
4. `se-security-reviewer.agent.md`
5. `principal-software-engineer.agent.md`
6. `expert-nextjs-developer.agent.md`
7. `postgresql-dba.agent.md`
8. `se-responsible-ai-code.agent.md`
9. `janitor.agent.md`
10. `debug.agent.md`
11. `critical-thinking.agent.md`
12. `devils-advocate.agent.md`
13. `demonstrate-understanding.agent.md`

## Gate for Phase 2 Promotion

A pending role cannot be promoted to active keep set until:

1. it is rewritten under `agents/roles/`
2. stale architecture claims are removed
3. tool scope is minimal and intentional
4. it passes review against current V9/Core contracts
