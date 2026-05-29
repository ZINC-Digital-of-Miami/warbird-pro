# Chart Parity Authority Packet v2 -> v2.1 (Gate-Clear Patch)

This patch applies only the three QA-required fixes:
1. Scope/contract alignment
2. Git protocol alignment
3. Reproducible evidence for Section 10

---

## PATCH 1 — Scope/Contract Alignment

### Replace front-matter block

```diff
-**Status:** DRAFT v2 — Kirk's rulings applied; awaiting final approval before implementation
-**Scope:** Pixel-for-pixel parity between the live Vercel dashboard and the new local Lightweight Charts dashboard
-**No Pine edits. No chart redesign. No approximation.**
+**Status:** DRAFT v2.1 — Kirk's rulings applied; awaiting final approval before implementation
+**Scope:** Chart-surface parity with explicit approved UI deltas. Pixel parity applies to retained chart surfaces; approved layout deltas are enumerated below.
+**No Pine edits. No unsanctioned redesign. No approximation on retained chart surfaces.**
+
+**Approved UI deltas from live Vercel surface (contracted exceptions):**
+- Replace bottom `DataTablesPanel` layout with PR #11 right-side cards.
+- Remove standalone volume histogram; retain pressure bar + volume-intelligence card.
+- Keep top correlations row, but adapt symbol set via Section 10 once approved.
+All other chart rendering surfaces remain parity-targeted against live Vercel authority.
```

### Replace this line in Section 2G

```diff
-### 2G. Right-Side Cards (PR #11 layout — Kirk's ruling)
+### 2G. Right-Side Cards (Approved UI Delta — Contracted Exception)
```

### Replace this line in Section 6

```diff
-**DO NOT merge PR #11 as-is.**
+**DO NOT merge PR #11 as-is.** This remains a parity implementation with approved UI deltas, not an open redesign lane.
```

---

## PATCH 2 — Git Protocol Alignment

### Replace Section 6 "Merge/Rebuild Recommendation (Updated)" with the block below

```markdown
## 6. Merge/Rebuild Recommendation (Updated)

**Cherry-pick content only** — do NOT merge PR #11.

Execution must follow repo git protocol in `AGENTS.md`:
- work on `main`
- no feature-branch implementation lane
- push only with explicit approval

Implementation steps:
1. Confirm branch is `main` and working tree ownership is known.
2. Pull only required surfaces from PR #11 into `main` working tree:
   - `dashboard/`
   - `engine/`
   using targeted restore/checkout from `origin/devin/1779988864-warbird-command-center`.
3. Do **not** carry PR #11 governance/config deletions.
4. Apply Section 3B fixes in bounded commits.
5. Run required verification after each phase.
6. Request approval before any push.
```

### Replace this line in Phase 1

```diff
-- Cherry-pick `dashboard/` + `engine/` from PR #11 into clean branch
+- Pull `dashboard/` + `engine/` from PR #11 onto `main` as targeted content import (no feature-branch lane)
```

---

## PATCH 3 — Section 10 Reproducibility / Evidence Trail

### Insert this immediately below `## 10. Correlations Row — 4 Databento Futures Symbol Research`

```markdown
**Evidence status:** PROVISIONAL until reproducibility packet is attached.

The symbol conclusions below are hypothesis-grade until the following evidence is produced and archived:
- exact query windows (UTC)
- exact symbols and mapping outputs
- exact aggregation method (1m -> 15m)
- exact correlation windows and formulas
- raw outputs + computed tables committed as artifacts
```

### Append this new subsection at the end of Section 10

```markdown
### 10.6 Reproducibility Appendix (Required Before Implementation)

Runbook-grade evidence must be generated before Section 10 is treated as settled:

1. Capture instrument mapping and symbol validity (GLBX.MDP3)
- verify continuous symbols used in the plan
- archive mapping output with timestamp

2. Build synchronized 15m panels for MES, NQ, 6E, CL, ZN
- source: Databento GLBX.MDP3
- base schema: `ohlcv-1m`
- aggregation: exact 15m bar close alignment in UTC

3. Compute rolling and full-window statistics
- Pearson correlation to MES returns
- rolling stability windows (e.g., 5d, 20d, 60d)
- sign-consistency checks for positive/negative designations

4. Archive evidence artifacts in repo
- recommended path: `artifacts/research/correlations/2026-05-29/`
- include:
  - `inputs_manifest.json`
  - `symbol_map.json`
  - `corr_table.csv`
  - `methodology.md`
  - `summary.md`

5. Promotion rule
- Section 10 remains provisional until artifacts exist and QA confirms reproducibility.
```

### Replace this line in Section 9 Open Items

```diff
-4. **Correlations symbols** -> **RESEARCHED:** See Section 10 — needs Kirk's approval
+4. **Correlations symbols** -> **PROVISIONAL:** See Section 10; requires reproducibility appendix + Kirk approval
```

---

## Optional One-Line Status Update for v2.1 Header

```diff
-**Status:** DRAFT v2 — Kirk's rulings applied; awaiting final approval before implementation
+**Status:** DRAFT v2.1 — Kirk's rulings applied; three QA-gate fixes integrated; awaiting final approval before implementation
```
