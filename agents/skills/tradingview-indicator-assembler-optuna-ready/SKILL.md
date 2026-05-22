---
name: tradingview-indicator-assembler-optuna-ready
description: |
  Assemble one clean, compile-ready TradingView Pine Script indicator from one or more existing source indicators, with no-repaint behavior and an Optuna-tunable input surface. Use this skill when the user wants to **build, merge, refactor, port, audit, or harden** a Pine indicator — particularly when combining the best parts of multiple existing indicators, hardening a script for no-repaint, preparing an indicator's input surface for Optuna sweeps, or auditing an indicator for repaint risk, resource budget, or Optuna-readiness. Triggers on substantive requests like "combine the best parts of A and B", "merge these indicators into one", "rewrite this Pine to be no-repaint", "make this Optuna-ready", "consolidate these scripts", "turn these into one final indicator", "audit my indicator for repaint and tunability", or "this Pine script is a mess — clean it up and make it sweepable". Do NOT use this skill for casual Pine syntax questions, single-line bug fixes, "how does X work in Pine" lookups, or quick conversational chatter — those are better handled directly. Use this skill when the work is substantial enough to justify the structured deliverable: source ownership map, design contract, Optuna tuning contract, no-repaint proof, and a Pine-specific validation report (compile-pine, pine-lint, repo guards). The skill refuses to claim "VERIFIED" without real Pine/TradingView validation evidence, so it's the right tool when the user wants the result to actually be trustworthy, not just plausible.
owner: agents
last_reviewed: 2026-05-22
---

# TradingView Indicator Assembler (Optuna-Ready)

Top-line philosophy: **Research first. Validate second. Prove third. Then build.**

You are acting as a senior Pine Script architect. The user has given you one or more source indicators and a goal. Your job is to produce one clean Pine v6 indicator that preserves the intended edge from each source, behaves the same on every reload (no repaint), stays inside TradingView's resource budget, and exposes a clean input surface that Optuna can sweep without breaking signal logic.

You must assume the merged indicator is wrong until source parity, no-repaint behavior, real Pine/TradingView validation, and Optuna-readiness have been independently verified. A compile-clean script is not a behavior-correct script. Passing repo-wide JS/Python/build tests proves nothing about Pine behavior.

## When to use this skill

Trigger when the user asks to build, merge, refactor, debug, port, or assemble a TradingView Pine indicator from one or more source indicators — especially when "best parts of A + B + C" framing is present. Trigger even if the user does not name Optuna; the Optuna-readiness contract is part of the deliverable unless they explicitly opt out.

Do not use this skill when the user only wants a strategy backtest harness, a non-Pine analytical model, or pure documentation work.

## Core workflow

Work through these phases in order. Skipping ahead to code is the most common failure mode and produces the kind of "looks right, behaves wrong" merge this skill exists to prevent.

### Phase 1 — Research the goal

Read the user request and look past the surface ask. The literal request is "merge A + B + C", but the real question is always: what trading behavior do they want the final indicator to exhibit?

Decide and write down:

- Output type: indicator (`indicator()`), strategy, alert helper, or library. If the user said "indicator" but the script will need to fire orders, surface that conflict before coding.
- Symbol and timeframe assumptions (e.g., MES 5m vs 15m vs 1h). Behavior often depends on this.
- Overlay vs separate pane.
- Repaint policy. Default is **no repaint** unless the user explicitly approves intrabar/realtime preview behavior.
- Bar-close vs intrabar confirmation policy.
- For each named source (A, B, C, …) write one sentence describing exactly what that source contributes — fib anchor logic, MA stack, label style, alert engine, etc.

Always assume your first interpretation may be incomplete. If the goal as you understand it would force a bad design choice (e.g., a no-repaint signal that depends on a future bar), surface that contradiction back to the user before continuing.

### Phase 2 — Source inventory

Before merging anything, build a per-source inventory. Use `references/source-inventory-template.md`. For each indicator file the user provided, document:

- Pine version declaration (`//@version=5`, `//@version=6`).
- Script type (`indicator`, `strategy`, `library`).
- All `input.*()` calls — name, type, default, group, tooltip if any.
- All `plot()`, `plotshape()`, `plotchar()`, `plotarrow()`, `plotbar()`, `plotcandle()`, `bgcolor()`, `fill()`, `hline()`, and `alertcondition()` calls. Hidden plots (`display=display.none`) still count against TradingView's 64-output cap.
- All `request.security()` and `request.footprint()` calls — symbol, timeframe, expression, lookahead.
- All `var` / `varip` declarations and what they persist.
- All helper functions, with the global names they reference.
- Core logic blocks (signal generation, fib anchoring, MA computation, alert routing, label rendering, debug/export).
- Inter-block dependencies: what does block X read that block Y produces?
- Any code that cannot be safely lifted in isolation (forward references, `var` state with bar-1 init, helper functions that close over globals, etc.).

If the source is large, build the inventory by section rather than by line. The point is to know what you have before you start cutting.

### Phase 3 — Component ownership map

Decide which source owns which component of the final indicator. Write it down explicitly — this is the audit trail you will need in the proof packet. Example:

- Indicator A: fib anchor logic, anchor helper functions, fib inputs, fib `var` state.
- Indicator B: moving averages, trend filter, MA visuals.
- Indicator C: label style system, colors, line widths, watermark.
- Indicator D: alert conditions, exported `ml_*` plots.

Every major block in the final script must be traceable back to one source (or marked "new — added because the merge required it, with rationale").

### Phase 4 — Clarify only after inventory

Now is the time for clarifying questions, not before. Ask sharp, source-grounded questions:

- "Indicator A's fib anchor sets `tradeEntry`, `tradeStop`, `tradeT1..T5`. Should those drive the final indicator's trade levels, or only draw structure?"
- "Indicator B's MA stack gates a `trendOk` boolean used in entry logic. Should the merged script keep that gate, or treat the MAs as visual only?"
- "Indicator C's labels read `entryPrice`, `stopPrice`, etc. Do you want exact text and placement preserved, or only the visual style?"
- "Indicator D fires `alertcondition()` 6 times. Are all six required, or can we collapse to one alert with a payload?"

Vague questions ("what do you want this to do?") indicate you skipped Phase 2.

### Phase 5 — Design the combined indicator contract

Before writing Pine code, fill in `references/merge-contract-template.md`. The contract must specify:

- Final indicator name and `//@version=6` (default v6 unless a source forces otherwise — and if it does, justify it).
- `indicator()` call: title, shorttitle, overlay, max_lines_count, max_labels_count, max_boxes_count, max_bars_back.
- Final input groups, in this order: Fib Structure, Moving Averages, Signal Logic, Visual Style, Labels, Alerts, Optuna/Debug, Advanced.
- Source ownership map (carried over from Phase 3).
- Naming convention for merged variables. When two sources both used `len`, you rename to `fibLen` and `maLen` — never let collisions resolve silently.
- Which original plots survive, which are dropped, and why.
- Repaint and confirmation policy, including any deliberate exceptions and how they will be communicated in plots/labels.
- Alert conditions: name, when they fire, what payload they include.
- Resource budget — count plot/plotshape/plotchar/plotarrow/plotbar/plotcandle + bgcolor + fill + hline + alertcondition. TradingView's hard cap is 64 outputs per script. Warbird Pro currently runs 56/64 — leave headroom.
- `request.security()` and `request.footprint()` budget. Pine's per-script `request.security()` cap is 40; the warbird-pro repo treats >30 as a warning. `request.footprint()` is heavy and must be cached per bar.

### Phase 6 — Optuna-tunable by design

Fill in `references/optuna-tuning-contract-template.md` before writing code, not after. Optuna readiness is a structural property of the script, not something you add afterward.

Required structure:

- All tunable knobs are `input.int()`, `input.float()`, `input.bool()`, or `input.string()` with `options=[...]`. No `input.timeframe()` or `input.session()` in the tunable surface — those break categorical sweeps.
- Group inputs cleanly: a sweep should target one group at a time without dragging unrelated visuals along.
- No magic constants in signal logic. If a number affects a signal, it is an input — even if its sensible range is narrow.
- No two inputs control the same behavior. Deduplicate ruthlessly.
- Stable, named output plots/signals that an external runner can read. For Warbird, this typically means `ml_*` or `nexus_fp_*` hidden plots with documented semantics.
- Explicit trigger booleans for each lifecycle state the user cares about: `setupLong`, `setupShort`, `entryLong`, `entryShort`, `exitLong`, `exitShort`, `stopHit`, `targetHit`, etc., as relevant. Each must use confirmed-bar logic.
- Clear separation between (a) frozen structural code, (b) tunable signal logic, (c) visuals, (d) labels, (e) alerts, (f) debug/export outputs. A sweep should never need to touch (a), (c), or (d) to test (b).

For each tunable input, record in the contract:

- Parameter name (matches the Pine `input.*()` call).
- Type: int, float, bool, categorical (string options).
- Safe min/max/options. Be explicit about why this range is safe — wider isn't better if it produces nonsense behavior.
- Default value.
- Reason it is tunable (what behavior it controls).
- Freeze warning if applicable (e.g., "do not sweep this with the fib anchor inputs simultaneously — they interact").

### Phase 7 — No repainting

No repaint is a hard requirement unless the user has explicitly approved otherwise in this session. Document the policy in the proof packet either way.

Required patterns:

- Use `barstate.isconfirmed` to gate any signal that matters for trading.
- Use `request.security(..., lookahead=barmerge.lookahead_off)` for higher-timeframe series. `barmerge.lookahead_on` is a future-look bug unless the surrounding code is built around it (rare; document if so).
- Never read `close[0]` or `high[0]` as if it were the closed bar. On the live bar it is intrabar.
- Never use `ta.pivothigh()` / `ta.pivotlow()` results without offsetting by the right-side window — pivots only confirm `rightBars` later.
- If the user wants both a live preview and a confirmed signal, render them as two distinct visual layers. Never let the preview backfill into the confirmed signal stream.
- If any logic is unavoidably realtime (e.g., a watermark that updates every tick), document it explicitly.

### Phase 8 — Simplicity first

The final indicator should be as simple as possible while preserving the requested edge.

- Prefer fewer gates over more gates. Each filter should have a documented reason it is in the script.
- Prefer direct, readable logic over clever abstractions.
- Remove dead code, unused inputs, unused plots, redundant calculations.
- Do not turn a clean indicator into a giant framework. If you find yourself adding a `mode` enum that switches between four behaviors, you are designing four indicators — say so and ask which one to keep.
- When two implementations are possible, recommend the simpler one and explain why.

### Phase 9 — Integration rules

- Preserve the exact source logic for any component the user identified as "best." Do not rewrite a working fib anchor from memory. Copy the proven internals; rename only what collides.
- Rename merged variables intentionally. Document the renames in the contract so the user can map back to the originals.
- Deduplicate inputs across sources. If A has `useEma` and B has `enableEma`, pick one and document.
- Group inputs as specified in Phase 5.
- Keep labels plain and readable. Avoid emoji-heavy labels unless the user's existing style uses them.
- Track resource limits as you add visuals. Hidden plots and alert conditions count.
- Do not claim the script is error-free unless real Pine/TradingView validation has actually passed (Phase 10).

### Phase 10 — Validate multiple ways

See `references/pine-validation-checklist.md` for the complete list. Generic tests do not count. Do not present results from `npm run lint`, `npm test`, Python unit tests, or repo-wide CI as proof that the Pine indicator is correct — they are not Pine validation.

What does count:

- Real TradingView pine-facade compile (`scripts/guards/compile-pine.sh <file>` in this repo).
- Pine-specific lint (`scripts/guards/pine-lint.sh <file>` in this repo) — checks ternary `ta.*`, alertcondition scope, output count, request.security budget, barstate.isconfirmed gates, etc.
- Pine-specific repo guards that validate Pine behavior, syntax, limits, or TradingView compatibility (see Phase 10 reference for the full list).
- TradingView chart/runtime inspection when the user can perform it.
- Static review specifically for repaint risk, security() lookahead, plot/label/line/box/table budget, and Optuna search-space compatibility.

You must always re-check, after the script is assembled:

- Compile status.
- Repaint risk (every signal-bearing branch).
- `request.security()` and `request.footprint()` lookahead and call count.
- TradingView output budget (plots + bgcolor + fill + hline + alertcondition ≤ 64).
- `max_lines_count`, `max_labels_count`, `max_boxes_count` are sufficient for the rendering load.
- Input names match the Optuna contract exactly. Names that drift between Pine and the runner break sweeps silently.
- Each component traces back to its source (Phase 3 audit).

### Phase 11 — Hard stop condition

If you cannot independently prove all of the following, return `NOT VERIFIED` and explain exactly what is missing. Do not present the indicator as done.

- Pine compile status (errors and warnings, with file path and command used).
- Real Pine/TradingView validation (which guards ran, which passed, which failed, exit codes).
- Source parity (each major component traces back to the source it claims to come from).
- No-repaint behavior (every signal-bearing branch reviewed against the patterns in Phase 7).
- Optuna-readiness (every tunable input listed in the contract is wired to real signal logic; no magic numbers remain).
- Resource budget safety (output count, request.security count, max_*_count headroom).

This is non-negotiable. "I think it should work" is not proof. "It compiled in my head" is not proof. Compile-clean is not behavior-correct.

### Phase 12 — Always make suggestions

After the analysis and validation, add a Suggestions section to the proof packet. Cover:

- Better structural choices (rearranging input groups, splitting visual from signal).
- Safer no-repaint patterns the current implementation could adopt.
- Cleaner Optuna tuning surface (inputs to add, inputs to remove, ranges to tighten).
- Inputs that should be frozen in early sweeps and unlocked later.
- Inputs that should be tunable but currently are hardcoded.
- Visuals that should be simplified to free output budget.
- Alerts or hidden export plots that would improve external validation.
- Risky logic that should be removed or isolated behind a debug flag.

Suggestions are not optional. Even on a successful merge, write them.

## Required proof packet

Use `references/proof-packet-template.md`. Every assembly run returns:

1. Final Pine script (or exact patch).
2. Source component map (Phase 3).
3. Final indicator contract (Phase 5).
4. Optuna tuning contract (Phase 6).
5. No-repaint proof (Phase 7).
6. Pine/TradingView validation report (Phase 10) — commands run, exit codes, error/warning counts, with paths.
7. Resource budget report — output count, `request.security` count, `request.footprint` count, `max_*_count` settings, current vs. cap.
8. Suggestions for improvement (Phase 12).
9. Known risks and unverified assumptions.
10. `VERIFIED` or `NOT VERIFIED` status with explicit justification.

## Reference files

Read these as needed during the workflow.

- `references/source-inventory-template.md` — per-source inventory format for Phase 2.
- `references/merge-contract-template.md` — combined indicator contract format for Phase 5.
- `references/optuna-tuning-contract-template.md` — Optuna parameter contract format for Phase 6.
- `references/pine-validation-checklist.md` — exhaustive Pine-only validation list for Phase 10, with this repo's guards named explicitly. **Read this before Phase 10.**
- `references/proof-packet-template.md` — final deliverable schema.

## What does not count as validation

Do not cite any of these as proof the Pine indicator is correct:

- Generic linters (eslint, prettier, ruff, black).
- Generic unit tests written in JS/TS/Python.
- `npm run build` succeeding (it builds the dashboard, not the Pine script).
- "I read the script and it looks right."
- "It compiled in my head."
- "It's similar to a script that worked."
- A previous version of the indicator passing — the merge changed the script.

If the only evidence available is generic, return `NOT VERIFIED` and ask the user to run the Pine-specific guards (or, if you have shell access in this session, run them yourself).

## Operating notes for this repo

This skill lives inside the warbird-pro repo. Several repo rules apply directly to any Pine work this skill does:

- Never edit `indicators/warbird-pro-v9.pine` or `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine` without explicit approval in the current session. The fib anchor, ladder math, and trade-state label semantics are protected scope.
- Never push Pine to TradingView Pine Editor from automation. Live TV operations are one explicit command at a time.
- Never reintroduce the banned `fibHtfSnapshot` pivot-window/`ta.barssince` variant — `scripts/guards/check-fib-scanner-guardrails.sh` enforces this.
- Do not rely on a stale static budget number. Always run `scripts/guards/pine-lint.sh <file>` and report current output/request headroom before approving new visuals or data calls.

If a request would conflict with these rules, surface the conflict before assembling. Doing the work and discovering the violation in Phase 10 wastes a session.
