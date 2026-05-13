#!/bin/bash
# UserPromptSubmit hook: inject sr-quant-engineer discipline + current V9 context.
#
# Motivation: recurring failure modes —
#  - skimming docs instead of reading sequentially
#  - dragging stale V7/V8 references into V9 work
#  - rationalizing past the CDP-down HARD STOP rule
#  - claiming verification done without running gates
#  - jumping to a fix without superpowers:systematic-debugging
#
# This hook adds one short reminder block to every user prompt so the discipline
# stays visible. Output goes into the agent's context, not the user's view.

set -uo pipefail

cat <<'EOF'
<warbird-discipline>
V9 is the only active model surface. Active Pine = indicators/warbird-pro-v9.pine
(Nexus ML RSI is research-only). All V7 and V8 surfaces are retired — never
reference them in new code; if you see one, treat it as a bug.

Before claiming work is done: run the Pine Verification Pipeline (lint, guards,
npm build) for .pine; run preflight-training + training-hard-gate flow for any
model artifact promotion. Verification-before-completion is a floor, not a
nice-to-have.

Before any TradingView CDP/MCP call: run `python3 scripts/ag/tv_connection_doctor.py --json`.
If `ready` is false, STOP and report it. Never call tv_launch, tv_health_check
as recovery, launch_tv_debug_mac.sh, pkill TradingView, killall TradingView,
or computer-use request_access on TradingView. CDP-down → human direction only.

Sequential stepped work — read files in full before editing, run the actual
verification commands before reporting them as run, cite file:line when making
claims. No skimming, no guessing, no high-school-rock-band improvisation.
</warbird-discipline>
EOF

exit 0
