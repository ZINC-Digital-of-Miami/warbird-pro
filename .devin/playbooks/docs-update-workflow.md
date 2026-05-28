# Documentation Update Workflow

When any architecture, contract, or operational truth changes, docs must be updated in the same commit as the code change.

## Which docs to update

| Change Type | Update These Docs |
|-------------|-------------------|
| Architecture change | `docs/MASTER_PLAN.md` |
| Model contract change | `WARBIRD_MODEL_SPEC.md`, `docs/contracts/pine_indicator_ag_contract.md` |
| Operational truth change | `CLAUDE.md` |
| Repo rules / hard constraints | `AGENTS.md` |
| Cloud scope change | `docs/cloud_scope.md` |
| Phase / contract lock | `MEMORY.md` |

## Quality gates for docs

Even docs-only changes need verification when they claim operational truth:

```bash
npm run lint
npm run build
```

## Rules

- Do not leave stale plans, runbooks, or agent-facing notes pointing at older triggers or training surfaces
- When evidence changes the contract, update active Markdown in the same change as code/settings/artifacts
- `AGENTS.md` and `CLAUDE.md` are derived operational views — they must not override hard safety rules or dated decision records
