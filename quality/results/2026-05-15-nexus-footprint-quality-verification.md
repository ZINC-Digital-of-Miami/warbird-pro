# Nexus Footprint-Quality Verification Checkpoint — 2026-05-15

## Scope

Nexus-only verification for `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine` after the footprint-quality repair and alert-surface removal.

No V9 Pine, V9 trainer, V9 export, V9 SHAP, V9 Monte Carlo, Supabase, or live TradingView surfaces are part of this checkpoint.

## Changes Under Verification

- `fpQualityOk` added as the fail-closed footprint-history/availability gate.
- Data-window/export-only export `nexus_fp_quality_ok` added to the TradingView CSV/evidence contract.
- `deltaDir`, gas-out, fatigue, Tier 1, Tier 2, and divergence confirmation now depend on footprint-quality proof.
- Generic cross dots are UI-only context and default OFF.
- Alert group, alert inputs, `alertcondition()`, and imperative `alert()` block removed.
- Nexus quality workbook/static tests expanded to cover the new fail-closed contract.

## Triple-Check Plan

Each verification area must pass three independent checks:

1. **Compiler / platform check:** Pine facade compile and `pine-lint.sh` budget accounting.
2. **Static contract check:** quality workbook tests plus targeted source inspection for footprint APIs, gates, data-window/export-only exports, no alerts, and no V9 contamination.
3. **Repo integration check:** guard scripts, Nexus footprint contract tests, and `npm run build`.

## Expected Evidence

- Pine facade returns `success: true`.
- `pine-lint.sh` reports one `request.footprint()` path, zero `request.security()`, zero alerts, and output calls below 64.
- `quality/test_functional.py -k nexus -q` passes all Nexus tests.
- `tests/duckdb_local/test_nexus_footprint_contract.py -q` passes.
- `check-contamination.sh` and `check-no-tv-force.sh` pass.
- `npm run build` completes successfully.

## Known Manual-Limit Note

This repository verification cannot visually inspect TradingView chart rendering or CSV-export the new data-window/export-only plot without an approved live TradingView operation. The code-level and compiler-level proof validates that the export plots exist, compile, and are set to `display.data_window`; chart-level CSV validation remains a manual or separately approved live-TV step.


## Observed Triple Verification Results

Recorded during this session on 2026-05-15 after all Nexus quality workbook updates were in place.

| Area | Pass 1 | Pass 2 | Pass 3 |
| --- | --- | --- | --- |
| Pine facade compiler | `success=True`, 258 variables, 3 functions | `success=True`, 258 variables, 3 functions | `success=True`, 258 variables, 3 functions |
| Static contract inspection | required tokens missing `[]`; exports missing `[]`; banned alert tokens `[]`; executable `request.footprint=1`; `request.security=0`; no V9 changed paths | same | same |
| Line proof | request line 283; delta line 285; rows line 288; row total line 294; `fpQualityOk` line 306; signal tier line 577 | same | same |
| Pine lint/budget | rc 0; output calls 35/64; plot 27; fill 8; alert 0; errors 0; warnings 0 | same | same |
| Nexus quality workbook tests | rc 0; 9 passed, 42 deselected | rc 0; 9 passed, 42 deselected | rc 0; 9 passed, 42 deselected |
| Nexus footprint contract tests | rc 0; 4 passed | rc 0; 4 passed | rc 0; 4 passed |
| Repo static banned-pattern guard | rc 0; no `fibHtfSnapshot()` definitions found | same | same |
| Contamination guard | rc 0; no cross-project contamination detected | same | same |
| No forced TradingView guard | rc 0; no forbidden forced-TradingView automation patterns detected | same | same |
| Next.js build | rc 0; compiled successfully; TypeScript finished; 27/27 static pages generated | same | same |

## Verification Harness Note

A first draft of the static checker counted the tooltip mention of `request.footprint()` plus the executable call. The final triple-pass checker corrected this by counting executable assignment lines only, and `pine-lint.sh` independently confirmed the request budget.


## 2026-05-15 Exportability Correction

Kirk confirmed that all TradingView Style/Visibility boxes were checked, but the downloaded CSV still omitted `nexus_*` columns. Screenshots showed only visible plots in the Style tab and no hidden export checkboxes. The root cause is that the evidence plots were still `display = display.none`; TradingView does not expose those as exportable series. The Nexus evidence plots are now intended to remain chart-clean but exportable via `display = display.data_window`.
