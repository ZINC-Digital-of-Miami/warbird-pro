---
name: verify-tv-slot
description: Use before any mcp__tradingview__pine_save, pine_smart_compile, pine_set_source, or pine_new call when working with Pine Script on TradingView. Prevents silent overwrites of the currently-open Pine Editor slot.
owner: agents
last_reviewed: 2026-05-22
---

# Verify TV Slot

## Core Rule

`pine_new` does not create a new script slot. It clears the editor buffer, but
save/compile operations still target whichever script is open in the editor
header.

Treat every save/compile/source write as potentially destructive until slot
identity is verified.

## Required Flow

Run this before every `pine_save`, `pine_smart_compile`, `pine_set_source`, or
`pine_new` call.

1. List scripts with `mcp__tradingview__pine_list_scripts`.
2. Read the current editor header using `mcp__tradingview__pine_get_source`
   (first lines only).
3. State the intended slot name explicitly before write.
4. If intended target is not the open slot, stop and switch slot manually in
   TradingView before any write call.
5. Execute write call only after steps 1-4 pass.

## Production-Locked Slots

Never overwrite these without explicit session approval and verified target
header:

- `Warbird Pro V9` (`indicators/warbird-pro-v9.pine`)
- `Warbird Nexus Machine Learning RSI` (`indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`)

## Red Flags (Hard Stop)

- "I already verified earlier in this session."
- "The buffer shows my new code so save is safe."
- "I will run pine_new then save-as through MCP."

If any red flag appears, restart the Required Flow from step 1.

## CDP Safety Link

If TradingView CDP is unresponsive, follow the hard-stop rule from
`agents/skills/cdp-down-recovery/SKILL.md`. Do not attempt recovery automation.
