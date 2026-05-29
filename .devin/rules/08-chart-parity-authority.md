# Chart Parity Authority

Use this rule whenever the task mentions chart parity, Packet v2.4/v2.4.1, PR #11, PR #14, local dashboard, `LiveMesChart.tsx`, fib rendering, pressure bar, Nexus, correlations, or Vercel demotion.

## Current Authority

- PR #14, branch `devin/1780027391-chart-parity-authority-skill`, is closed as partial-import archive evidence.
- Governing packet surface: `agents/skills/chart-parity-authority/SKILL.md`.
- Corrected proposal: `docs/packet_plan_v2.4.1_correction_proposal.md`.
- Older local v2.1 packet diffs are superseded.

## Non-Negotiables

- Do not merge PR #11 as-is.
- Do not reopen or merge PR #14; its accepted chart-authority subset is already local.
- Do not carry PR #11 dashboard frontend unless the packet explicitly says to use a surface.
- Use the exact `components/charts/LiveMesChart.tsx` chart behavior as the visual source for retained chart surfaces.
- Use `engine/fib_engine.py` only where the packet approves it. Do not invent a new fib engine.
- No Pine edits unless Kirk explicitly approves the exact Pine edit in the current session.
- No Vercel/Next.js demotion until local replacement proof exists.
- No fake footprint, fake win rate, fake Gemini screenshot analysis, or proxy values presented as equivalent to real data.

## Nexus And Volume

- Drop in the approved Nexus logic as-is minus TradingView-centric items.
- Use standard volume for now.
- If real `request.footprint()` or Databento `trades` side evidence is unavailable, document the adapter gap honestly.
- If unknown/low-quality volume evidence is used, force WAIT instead of GO when the packet requires a confidence gate.

## Required Closeout

Every Devin session touching this lane must return:

- files changed
- exact authority read
- what was kept from PR #11 / PR #14
- known adapter gaps
- verification commands run and their outcomes
- what remains blocked or waiting for Kirk
