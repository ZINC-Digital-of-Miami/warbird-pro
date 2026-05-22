# Phase 2 Batch 4 Audit: Domain And Legacy Skill Retirement

Date: 2026-05-22
Status: complete

## Scope

Phase-2 batch-4 review for the remaining domain-specific or legacy-only
`.claude/skills/` source surfaces:

1. `_tc_raw`
2. flat TradingCode Pine snippet files in `.claude/skills/*.md`
3. `quality-playbook`
4. `supabase-ml-ops`

## Decisions

1. Retire `_tc_raw` and flat TradingCode Pine snippet material.
   - These files are raw reference snippets, not complete Warbird skills.
   - They do not carry owner, last-reviewed, Warbird V9, or current Pine v6
     safety metadata.
   - Current Pine work is covered by `pine-script-ai-coding-agent`,
     `tradingview-indicator-assembler-optuna-ready`, `tv-preflight`, and the
     active repo Pine rules.
2. Retire `quality-playbook`.
   - Active Warbird quality execution is repo-native:
     `warbird-agent-precheck`, `tc_validator`, and `agents/` automation.
   - `AGENTS.md`, `CLAUDE.md`, and `docs/MASTER_PLAN.md` already state that
     quality workbook runtime/artifact surfaces are retired and must not be
     used for active execution.
   - Prior evidence showed quality-playbook could falsely appear complete when
     its artifact contract drifted, so reintroducing it as an active skill
     would weaken the fail-closed lane.
3. Retire `supabase-ml-ops`.
   - It is a broad monolith that mixes Supabase, ML, Pine, fib, market data,
     and feature engineering guidance.
   - Its content includes stale assumptions that conflict with current V9/Core:
     v7 active Pine files, MES-centric training wording, macro/FRED/cloud
     feature stacking, and `-.236` mechanical stop guidance.
   - Valid surviving behavior is already covered by focused canonical skills
     plus current repo authority docs:
     - `v9-core-training-governance`
     - `v9-postfit-shap-monte-carlo-gates`
     - `warbird-tuning-router`
     - `pine-script-ai-coding-agent`
     - `docs/cloud_scope.md`
     - `docs/contracts/pine_indicator_ag_contract.md`
     - `AGENTS.md`

## Actions

1. Added no new active canonical skill for batch-4.
2. Updated canonical registries and phase tracking:
   - `agents/README.md`
   - `agents/manifest.yaml`
   - `agents/skills/README.md`
   - `agents/skills/phase-2-custom-skill-migration.md`
   - `MEMORY.md`
3. Marked `.claude/skills/**` retired in the canonical manifest.
4. Left ignored local `.claude/skills/` files untouched as migration evidence
   only. They are not tracked and are not active registry surfaces.
5. Did not delete or edit active AG/Optuna code, study databases, workspaces,
   model artifacts, Pine files, or training scripts.

## Rationale

Batch-4 is a retirement batch because migrating these surfaces verbatim would
reintroduce stale or unsafe guidance. The safe current state is one canonical
skill registry under `agents/skills/`, with legacy mirrors treated as ignored
local evidence rather than execution authority.

## Verification

Completed checks after batch actions:

1. PASS: `./scripts/guards/warbird-agent-precheck.sh --mode manual`
   - local quality lane passed
   - `npm run lint` passed
   - `npm run build` passed
   - V9 contract tests passed: `6 passed`
   - tuner jsonl safety tests passed: `2 passed, 63 deselected`
2. PASS: `tc_validator --fast`
   - fast local quality lane passed
   - agents umbrella, manifest, skills, roles, Quant role, and process-reaper
     surface checks passed
3. PASS: active canonical skill names do not duplicate legacy
   `.claude/skills` names: 10 active checked.
4. PASS: `git diff --check`
5. PASS: `git diff --name-status` showed no tracked deletions.

## Risk Notes

- The ignored local `.claude/skills/` directory still exists on disk for
  forensic comparison, but it is no longer an active registry surface.
- Future skill additions must start under `agents/skills/`.
- Any future Supabase, Pine, or V9/Core ML work must use focused canonical
  skills and current repo authority docs, not the retired monolith.
