#!/bin/bash
# PostToolUse hook: block new code that references retired V7/V8/deprecated surfaces.
#
# Motivation: agents keep dragging stale context forward. Example failure 2026-05-13:
# updated hook-pre-plan-contract.sh and left WARBIRD_V8_PLAN.md as "fallback" even
# though V8 is retired. The mistake was caught by Kirk, not by infra. This guard
# blocks the class of mistake mechanically.
#
# Scans the edited file for retired-surface tokens. Carved-out paths still allowed
# to reference them (CLAUDE.md / AGENTS.md / audit history / archive trees).
#
# Input: JSON on stdin (PostToolUse contract). Output: decision:block on hit, else nothing.

set -uo pipefail

fp=$(jq -r '.tool_input.file_path // .tool_response.filePath // ""' 2>/dev/null || true)
[ -z "$fp" ] && exit 0
[ ! -f "$fp" ] && exit 0

# File-type scope: only scan files where NEW retired references are clearly a mistake.
# History/audit/archive files are explicitly excluded; they legitimately describe
# what was retired.
case "$fp" in
  # Active code surfaces where retired refs are forbidden
  */indicators/*.pine) ;;
  */scripts/ag/*.py) ;;
  */scripts/duckdb_local/*.py) ;;
  */scripts/guards/*.sh) ;;
  */.claude/agents/*.md) ;;
  */.claude/skills/*/SKILL.md) ;;
  */.claude/skills/*/*.md) ;;
  */.claude/commands/*.md) ;;
  */.claude/hooks/*.sh) ;;
  *) exit 0 ;;
esac

# Carve-out paths — these legitimately reference retired surfaces (history, audit, archive)
case "$fp" in
  */archive/*|*/.archive/*) exit 0 ;;
  */docs/audits/*) exit 0 ;;
  */docs/changelog*) exit 0 ;;
  # The guard itself can name what it bans
  */scripts/guards/check-retired-surfaces.sh) exit 0 ;;
  # Backfill/migration scripts may name retired tables for history
  */scripts/ag/backfill_*.py) exit 0 ;;
esac

# Retired-surface tokens (V7 Pine, V8 plan/Pine, deprecated V9 cards, retired inputs)
# When this list changes, update CLAUDE.md "Retired/removed Pine variants" too.
RETIRED_PATTERNS=(
  # V7 Pine indicators / strategies (all retired per CLAUDE.md)
  'warbird-pro-indicator\.pine'
  'Warbird_Pro_v7\.pine'
  'v7-warbird-institutional'
  'v7-warbird-strategy'
  'v7-warbird-institutional-backtest-strategy'
  'fibs-only\.pine'
  # V8 plan + Pine files (retired era)
  'WARBIRD_V8_PLAN\.md'
  'v8-warbird-live\.pine'
  'v8-warbird-prescreen\.pine'
  'v8-warbird-institutional'
  # Deprecated V9 4-card system (per CLAUDE.md 2026-05-09: "deprecated. Path went 4 cards → 2 cards → single Core card")
  'warbird_pro_v9_exit_cpcv'
  'warbird_pro_v9_entry_filter_cpcv'
  'warbird_pro_v9_ag_meta_cpcv'
  'warbird_pro_v9_joint_challenger'
  # Retired Pine inputs / gates (per CLAUDE.md MA-rewrite + Phase B changes)
  'znGateDirection'
  'useMaGate'
  # Retired feature (DXY removed from V9 Core 2026-05-11)
  'ml_xa_dxy_code'
  'ml_xa_dxy_diverge'
)

hits=""
for pat in "${RETIRED_PATTERNS[@]}"; do
  # -n for line numbers, -E for extended regex, fixed boundaries via the pattern itself
  match=$(grep -nE "$pat" "$fp" 2>/dev/null || true)
  if [ -n "$match" ]; then
    hits+="  retired token /${pat}/ in ${fp}:"$'\n'
    while IFS= read -r line; do
      hits+="    ${line}"$'\n'
    done <<< "$match"
  fi
done

if [ -n "$hits" ]; then
  msg=$(printf 'check-retired-surfaces FAILED for %s. New code must not reference V7/V8/deprecated surfaces. Per CLAUDE.md, these are retired. If this is a genuine history reference, move it to docs/audits/, docs/changelog*, or an archive/ tree. Otherwise update the code to the V9 equivalent.\n\nHits:\n%s' "$fp" "$hits")
  jq -cn --arg fp "$fp" --arg out "$msg" \
    '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$out}, decision:"block", reason:"check-retired-surfaces failed — see additionalContext"}'
fi

exit 0
