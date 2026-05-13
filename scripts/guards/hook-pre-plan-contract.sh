#!/bin/bash
# PreToolUse hook: surface V9 Locked Rules before edits on governed surfaces.
#
# Motivation: verbal requests have contradicted Locked Rules before
# (CDP-down HARD STOP rule violated twice before being escalated to absolute;
# tv_launch called as "recovery" after CDP failure). This hook injects the
# Locked Rules into additionalContext before any edit on governed surfaces,
# so the rules are visible in real time — not post-mortem.
#
# V9 authority order (first that exists wins):
#   1. CLAUDE.md "Locked Rules" section (canonical)
#   2. docs/MASTER_PLAN.md "Hard Constraints" section (active plan)
#
# Non-blocking: just adds context. Kirk's verbal overrides still rule;
# this ensures the contradiction is SEEN before, not after.

set -uo pipefail

fp=$(jq -r '.tool_input.file_path // ""' 2>/dev/null || true)

# Governed surfaces where Locked Rules apply (V9 surface set)
case "$fp" in
  */indicators/warbird-pro-v9.pine) ;;
  */indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine) ;;
  */scripts/ag/*.py) ;;
  */scripts/duckdb_local/*.py) ;;
  */scripts/duckdb_local/workspaces/warbird_pro_core/*) ;;
  */CLAUDE.md|*/AGENTS.md|*/WARBIRD_MODEL_SPEC.md) ;;
  *) exit 0 ;;
esac

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/Volumes/Satechi Hub/warbird-pro}"

constraints=""
source_file=""

# Prefer CLAUDE.md Locked Rules (canonical)
if [ -f "$PROJECT_DIR/CLAUDE.md" ]; then
  candidate=$(awk '/^## Locked Rules/{flag=1;next} /^## /{flag=0} flag' "$PROJECT_DIR/CLAUDE.md" | head -80)
  if [ -n "$candidate" ]; then
    constraints="$candidate"
    source_file="CLAUDE.md → Locked Rules"
  fi
fi

# Fall back to MASTER_PLAN Hard Constraints
if [ -z "$constraints" ] && [ -f "$PROJECT_DIR/docs/MASTER_PLAN.md" ]; then
  candidate=$(awk '/^## Hard Constraints/{flag=1;next} /^## /{flag=0} flag' "$PROJECT_DIR/docs/MASTER_PLAN.md" | head -60)
  if [ -n "$candidate" ]; then
    constraints="$candidate"
    source_file="docs/MASTER_PLAN.md → Hard Constraints"
  fi
fi

if [ -z "$constraints" ]; then
  exit 0
fi

jq -cn --arg fp "$fp" --arg c "$constraints" --arg src "$source_file" \
  '{hookSpecificOutput:{hookEventName:"PreToolUse",additionalContext:("V9 LOCKED RULES (" + $src + ") — edit to " + $fp + " must respect these. If a verbal request conflicts with a rule below, STOP and confirm before proceeding:\n\n" + $c)}}'

exit 0
