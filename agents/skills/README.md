# Skills Registry

Canonical skill decisions live here.

## Policy

- New skills are authored under `agents/skills/`.
- Legacy skill trees are treated as migration sources only.
- Overlap is resolved by keep-one, retire-duplicates.

## 2026-05-22 Curation Snapshot

Keep (active, curated):

- project safety and governance guidance from `.github/instructions/`
- custom quant/trading safety skills migrated under `agents/skills/`:
  - `cdp-down-recovery`
  - `tv-preflight`
  - `senior-quant-mindset`
  - `v9-promote-champion`
  - `verify-tv-slot`
- Pine engineering skills migrated under `agents/skills/`:
  - `pine-script-ai-coding-agent`
  - `tradingview-indicator-assembler-optuna-ready`
- Training and model-governance skills rebuilt under `agents/skills/`:
  - `v9-core-training-governance`
  - `v9-postfit-shap-monte-carlo-gates`
  - `warbird-tuning-router`
- read-only MCP-oriented helpers that are not tied to Hermes runtime

Retired from legacy mirrors:

- `.hermes/skills/**` (removed in 2026-05-22 phase-1)
- duplicate Pine primer stacks mirrored in multiple locations
- duplicate generic utility skills mirrored in both `.github/skills` and
  `.claude/skills` (removed from `.claude/skills` in 2026-05-22 de-dup pass)
- empty `tc-*` placeholder directories in `.claude/skills` (retired in phase-2
  batch-2)
- legacy training/Optuna wrapper guidance that still routes active work through
  Postgres, `train_ag_baseline.py`, or stale `scripts/optuna` paths (not
  migrated verbatim; valid AG/Optuna implementations, runners, workspaces, and
  artifacts remain preserved)
- raw `_tc_raw` and flat TradingCode Pine snippets from `.claude/skills`
  (retired in phase-2 batch-4; canonical Pine work uses current Pine skills and
  active Warbird rules)
- `.claude/skills/quality-playbook` (retired in phase-2 batch-4; active quality
  execution is repo-native precheck, `tc_validator`, and `agents/` automation)
- `.claude/skills/supabase-ml-ops` (retired in phase-2 batch-4; active cloud,
  Pine, and V9/Core ML rules live in repo authority docs and focused canonical
  skills)

Audit record: `docs/audits/2026-05-22-skill-overlap-pruning.md`.
Phase-2 plan: `agents/skills/phase-2-custom-skill-migration.md`.
Batch-1 audit: `docs/audits/2026-05-22-phase2-batch1-tv-safety-skills.md`.
Batch-2 audit: `docs/audits/2026-05-22-phase2-batch2-pine-foundations-skills.md`.
Batch-3 audit: `docs/audits/2026-05-22-phase2-batch3-training-model-governance-skills.md`.
Batch-4 audit: `docs/audits/2026-05-22-phase2-batch4-domain-legacy-skills.md`.

## Required Audit Rules

- Every kept skill must have a clear owner, purpose, and last-reviewed date.
- Every retired skill must be listed in an audit note before removal.
- If two skills solve the same task, keep only one canonical copy.
