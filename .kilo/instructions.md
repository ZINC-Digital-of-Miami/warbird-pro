# Warbird-Pro Kilo Guardrail Overlay

This overlay is additive to `AGENTS.md`, `CLAUDE.md`, and the active docs listed in
`AGENTS.md`. It does not replace those files. When this overlay conflicts with
Warbird authority docs, follow the higher-precedence Warbird authority stack in
`AGENTS.md`.

## Load Order For Warbird Work

1. Read `AGENTS.md` first.
2. Read the active docs listed in `AGENTS.md` for the touched surface.
3. Read these Kilo guardrail files before planning edits:
   - `.kilo/rules/warbird-absolute-boundaries.md`
   - `.kilo/rules/validation-matrix.md`
   - `.kilo/rules/hermes-quality-policy.md`

## Operating Rule

If a task touches Pine, training, local DuckDB, Supabase, Optuna, Databento,
TradingView, quality archives, Kilo config, or Hermes config, stop and
route through the matching guardrail before editing. Do not infer from memory.

## Fixed Lane Summary

- Warbird Pro V9 is the only active main chart indicator lane.
- Nexus is a retained support/research indicator lane only.
- Local DuckDB/Pandera/AutoGluon file pipeline is the active V9 modeling layer.
- Cloud Supabase is serving/runtime/support only, never a raw training warehouse.
- Legacy local `ag_training` and old warehouse modeling are reference-only.
- Optuna is a backup/specialist path only and must not be used unless Kirk
  explicitly requests it in the current session.

## Validator Rule

Every completed task needs a validator matched to the work type. If a named
validator such as `tc_validator` is unavailable, do not pretend it ran. Install
it with `./scripts/setup/install_tc_tracker.sh`, then rerun validation. Follow
`.kilo/rules/validation-matrix.md` and fail closed on any unvalidated surface.

## Critical Workspace Constraints

- NO NODE NATIVE MODULES in Supabase Functions. Use Deno-compatible imports only.
- NO PACKAGE INSTALLS without explicit chat approval.
- PINE SCRIPT MUST BE V5. Do not introduce v4 syntax.
- SEPARATE SQL DIALECTS: DuckDB (OLAP) for Python, Postgres (OLTP) for Supabase.
- NEVER assume a visual UI is complete just because code compiled; use validator evidence.
