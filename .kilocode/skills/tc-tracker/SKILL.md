---
name: tc-tracker
description: >
  TradingCode task-context tracker for Pine work. Routes Pine/TradingView work
  through curated tc-* skills and enforces tc_validator before completion.
---

# tc-tracker

## Purpose

Use this skill as the entrypoint for TradingCode (`tc-*`) Pine knowledge in the
Warbird workspace. It provides deterministic routing to the right `tc-*` skill
and blocks completion claims unless `tc_validator` passes.

## Required Flow

1. Classify the request and pick matching `tc-*` modules:
   - strategy/backtest mechanics -> `tc-strategies-backtesting`
   - strategy archetypes -> `tc-example-strategies`
   - control flow/logic -> `tc-advanced-pine`, `tc-operators`
   - alerts/webhooks -> `tc-alerts`
   - plot budget/rendering -> `tc-plots`, `tc-visual-output`, `tc-bar-coloring`
   - indicators/inputs/TA primitives -> `tc-indicators-basics`, `tc-technical-analysis`, `tc-math`
2. Pull exact patterns from the selected `tc-*` skills under `.kilocode/skills/tc-*`.
3. Apply Warbird boundaries from `AGENTS.md` + `.kilo/rules/*.md` before coding.
4. Before claiming completion, run:
   - `tc_validator --fast` for docs/config-only edits
   - `tc_validator` (full) for code, Pine, trainer, ETL, or contract edits
5. If `tc_validator` fails, do not claim completion. Fix and rerun.

## Source Map

- Compiled skill index: `.kilocode/skills/tc-README.md`
- Raw lessons lineage: `.claude/skills/_tc_raw/` (source-only reference)

## Non-Negotiable

- No completion claim without passing `tc_validator`.
- No fake "validated" status from exit-code assumptions or partial checks.
