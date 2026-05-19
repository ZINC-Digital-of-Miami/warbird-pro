# Warbird Fib Visual Semantics Gate (Regression Reference)

## Why this exists
A regression occurred when non-active fib visuals were removed/restyled into TP-like labels. This made the chart look like an active trade while engine state was inactive.

## Failure signature
- Table shows `WAITING`
- Entry line is missing
- TP-like ladder still visible

This is consistent with `tradeActive == false` while waiting-state fib ladder is visually mislabeled.

## Hard invariants
1. `positionText == "WAITING"` iff `tradeActive == false`.
2. `lineEntry` visibility is gated by `tradeActive` only.
3. Non-active fib ladder uses fib-level semantics (`0/.236/.382/.5/.618/.786/1.0/...`), not `TP*` semantics.
4. Active-trade ladder uses `ENTRY/SL/TP*` semantics and only draws when `tradeActive == true`.

## Mandatory check sequence for fib/table/entry edits
1. Read-only audit and user approval.
2. Diff review of fib draw block + table state block + tradeActive gates.
3. Run validators:
   - `scripts/guards/compile-pine.sh indicators/warbird-pro-v9.pine`
   - `scripts/guards/pine-lint.sh indicators/warbird-pro-v9.pine`
   - `scripts/guards/check-fib-scanner-guardrails.sh`
   - `scripts/guards/check-contamination.sh`
   - `scripts/guards/check-no-tv-force.sh`
   - `npm run build`
4. Require user chart review before any training/modeling request is honored.

## Scope note
Warbird Pine work is Pine Script v6 only.
