#!/bin/bash
# PreToolUse hook: enforce CDP-down HARD STOP rule (CLAUDE.md Locked Rules, 2026-05-05).
# Banned TradingView ops cannot run from the agent — full stop, no parameters
# that make them OK.
#
# Matched against the tool name via PreToolUse matcher in settings.json.
# This script is the *final* enforcement layer — even if the user permissions
# allow these tools, this hook blocks them.

set -uo pipefail

tool=$(jq -r '.tool_name // ""' 2>/dev/null || true)

reason="CDP-down HARD STOP rule (CLAUDE.md Locked Rules): \`${tool}\` is banned from the agent. No parameters make this OK. If CDP is unresponsive, STOP and report 'CDP is not responding. I'm stopped. Waiting for instructions.' — wait for human direction. Do NOT call tv_launch, tv_health_check as recovery, launch_tv_debug_mac.sh, pkill TradingView, killall TradingView, or computer-use request_access on TradingView."

case "$tool" in
  mcp__tradingview__tv_launch)
    jq -cn --arg r "$reason" \
      '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
    ;;
  *)
    exit 0
    ;;
esac

exit 0
