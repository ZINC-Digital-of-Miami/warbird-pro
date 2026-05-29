# Phase 2: Role Hardening

Status: planned (separate phase from umbrella bootstrap).

## Objective

Rebuild retained custom roles so each one is intentional, robust, and aligned
to the active V9/Core workflow.

## Sequence

1. Inventory all legacy role files across mirror directories.
2. Mark each role keep/drop with reason and owner.
3. Rewrite kept roles under `agents/roles/` using current contracts:
   - local-first V9 Core
   - real data only
   - no unauthorized Pine edits
   - no push/deploy without explicit approval
4. Add a dated audit note for each rewritten role.
5. Retire legacy role files after parity review.

## Definition of Done

- no kept role contains placeholders or stale architecture claims
- no duplicate role ownership across multiple directories
- every kept role includes model, tool scope, and fail-closed safety behavior
