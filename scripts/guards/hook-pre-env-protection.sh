#!/bin/bash
# PreToolUse hook: block edits to .env* secret files.
# Inputs: JSON on stdin with tool_input.file_path.
# On match: emit a deny PreToolUse decision and exit 0.

set -uo pipefail

fp=$(jq -r '.tool_input.file_path // ""' 2>/dev/null || true)
[ -z "$fp" ] && exit 0

case "$fp" in
  */.env|*/.env.*|*/.env.local|*/.env.production|*/.env.development|*/.env.test)
    jq -cn --arg fp "$fp" \
      '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:("Editing " + $fp + " is blocked. Secrets must be rotated/set via the user'\''s shell, not by the agent. If you genuinely need to inspect a key, ask the user to read the relevant line for you.")}}'
    ;;
  *)
    exit 0
    ;;
esac

exit 0
