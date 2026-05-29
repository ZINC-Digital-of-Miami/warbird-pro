#!/usr/bin/env bash
# Hard enforcement gate: encodes Warbird Knowledge notes as executable rules.
#
# This script is the enforcement engine that Knowledge notes cannot be on their
# own. Knowledge notes are context injection — this script is exit 1.
#
# Runs as part of pre-commit and pre-push via warbird-agent-precheck.sh.
# Also callable standalone: ./scripts/guards/warbird-knowledge-enforcement.sh --mode manual
#
# Every check maps to a specific Knowledge note ID for traceability.
# See enforcement-manifest.json for the full mapping.
#
# Exit codes:
#   0 = all checks passed
#   1 = violation detected (hard block)
#   2 = usage error

set -euo pipefail

MODE="manual"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="${2:-manual}"; shift 2 ;;
    *) shift ;;
  esac
done

case "$MODE" in
  pre-commit|pre-push|manual) ;;
  *)
    echo "Usage: warbird-knowledge-enforcement.sh --mode pre-commit|pre-push|manual"
    exit 2
    ;;
esac

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

VIOLATIONS=()

add_violation() {
  local note_name="$1"
  local note_id="$2"
  local detail="$3"
  VIOLATIONS+=("[${note_name}] (${note_id}): ${detail}")
}

report_and_exit() {
  if [[ ${#VIOLATIONS[@]} -eq 0 ]]; then
    return 0
  fi

  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  WARBIRD KNOWLEDGE ENFORCEMENT ENGINE — HARD BLOCK          ║"
  echo "╠══════════════════════════════════════════════════════════════╣"
  echo "║                                                              ║"
  echo "║  One or more Knowledge notes were violated.                  ║"
  echo "║  These are not advisory. These are hard gates.               ║"
  echo "║                                                              ║"
  echo "║  Fix the violations or get explicit Kirk approval.           ║"
  echo "║                                                              ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "VIOLATIONS (${#VIOLATIONS[@]}):"
  for v in "${VIOLATIONS[@]}"; do
    echo "  ✘ $v"
  done
  echo ""
  exit 1
}

# ─── Collect changed files based on mode ───

collect_changed_files() {
  CHANGED_FILES=()
  case "$MODE" in
    pre-commit)
      while IFS= read -r f; do
        [[ -n "$f" ]] && CHANGED_FILES+=("$f")
      done < <(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null)
      ;;
    pre-push)
      local upstream_ref
      upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo 'origin/main')"
      while IFS= read -r f; do
        [[ -n "$f" ]] && CHANGED_FILES+=("$f")
      done < <(git diff --name-only --diff-filter=ACMR "$upstream_ref"...HEAD 2>/dev/null)
      ;;
    manual)
      while IFS= read -r f; do
        [[ -n "$f" ]] && CHANGED_FILES+=("$f")
      done < <(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null)
      if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
        while IFS= read -r f; do
          [[ -n "$f" ]] && CHANGED_FILES+=("$f")
        done < <(git diff --name-only --diff-filter=ACMR 2>/dev/null)
      fi
      ;;
  esac
}

# ═══════════════════════════════════════════════════════════════════════
# KNOWLEDGE NOTE ENFORCEMENT CHECKS
# Each function maps to one or more Knowledge notes.
# ═══════════════════════════════════════════════════════════════════════

# ─── Knowledge: "Main Only And Push Approval" ───
# note-07165b17942b47838287f90ac94ee165
# Rule: Never force push or use --no-verify

check_no_force_push_in_changes() {
  for f in "${CHANGED_FILES[@]}"; do
    [[ -f "$f" ]] || continue
    case "$f" in
      *.sh|*.bash|*.yml|*.yaml|Makefile|*.mk)
        # Skip self-references
        case "$f" in
          scripts/guards/warbird-knowledge-enforcement.sh) continue ;;
          scripts/guards/warbird-file-protection.sh) continue ;;
          scripts/guards/enforcement-manifest.json) continue ;;
        esac
        if grep -qE 'git\s+push\s+.*--force(?!-with-lease)' "$f" 2>/dev/null; then
          add_violation "Main Only And Push Approval" "note-07165b17" \
            "Forbidden 'git push --force' found in $f"
        fi
        if grep -qE '--no-verify' "$f" 2>/dev/null; then
          add_violation "Main Only And Push Approval" "note-07165b17" \
            "Forbidden '--no-verify' found in $f"
        fi
        ;;
    esac
  done
}

# ─── Knowledge: "DuckDB And Specialized Models Only" ───
# note-a429f39c81174484a424646173251551
# Rule: Do not invoke training-full-zoo or legacy ag_training

check_no_legacy_training() {
  for f in "${CHANGED_FILES[@]}"; do
    [[ -f "$f" ]] || continue
    case "$f" in
      *.py)
        if grep -qE '(training.full.zoo|train_ag_baseline|train_hard_gate|ag_training)' "$f" 2>/dev/null; then
          add_violation "DuckDB And Specialized Models Only" "note-a429f39c" \
            "Legacy/full-zoo training reference found in $f — use train_v9_locked.py"
        fi
        ;;
    esac
  done
}

# ─── Knowledge: "Nexus And Standard Volume Adapter Gap" ───
# note-96ef65ec546145338408dc298235f718
# Rule: No fake footprint/win rate data presented as real

check_no_fake_data_labels() {
  for f in "${CHANGED_FILES[@]}"; do
    [[ -f "$f" ]] || continue
    case "$f" in
      *.py|*.ts|*.tsx|*.js|*.jsx)
        if grep -qiE '(fake.?footprint|mock.?footprint|fake.?win.?rate|simulated.?footprint)' "$f" 2>/dev/null; then
          add_violation "Nexus And Standard Volume Adapter Gap" "note-96ef65ec" \
            "Fake/mock footprint data detected in $f — label adapter gaps honestly"
        fi
        ;;
    esac
  done
}

# ─── Knowledge: "Proof Before Vercel Demotion" ───
# note-86b6ce3eac4646eb87b2f83bef46dfbf
# Rule: No Vercel demotion without proven replacement

check_no_vercel_demotion() {
  for f in "${CHANGED_FILES[@]}"; do
    case "$f" in
      vercel.json|.vercel/*|next.config.*|app/layout.tsx)
        # Check if file is being deleted or gutted
        if ! git diff --cached --name-only --diff-filter=D 2>/dev/null | grep -q "^${f}$"; then
          continue
        fi
        add_violation "Proof Before Vercel Demotion" "note-86b6ce3e" \
          "Vercel infrastructure file deleted: $f — requires proven local replacement first"
        ;;
    esac
  done
}

# ─── Knowledge: "Sonic Is Advisory" ───
# note-d6a7f0cef6ad457c9aec8d044a7b7a87
# Rule: No auto-apply of Sonic fixes (checked via commit message)

check_no_autofix_commit_messages() {
  # Only check on pre-commit — inspect the commit message being created
  [[ "$MODE" == "pre-commit" ]] || return 0

  local msg_file="$ROOT_DIR/.git/COMMIT_EDITMSG"
  [[ -f "$msg_file" ]] || return 0

  local msg
  msg="$(cat "$msg_file")"

  if echo "$msg" | grep -qiE '(auto.?fix|autofix).*(sonic|sonar)'; then
    add_violation "Sonic Is Advisory" "note-d6a7f0ce" \
      "Commit message references Sonic auto-fix — Sonic fixes require defect map + Kirk approval"
  fi
}

# ─── Knowledge: "Manual First Automations Later" ───
# note-445c5846b0aa450b9fdfa1a70f81f70e
# Rule: No auto-push/auto-merge/auto-fix automation without approval

check_no_unauthorized_automation() {
  for f in "${CHANGED_FILES[@]}"; do
    [[ -f "$f" ]] || continue
    case "$f" in
      .github/workflows/*|.devin/playbooks/*|cron/*|scripts/automation/*)
        # Check for auto-push/auto-merge patterns in new workflow files
        if git diff --cached -- "$f" 2>/dev/null | grep -qiE '(auto.?push|auto.?merge|auto.?fix|auto.?deploy)'; then
          add_violation "Manual First Automations Later" "note-445c5846" \
            "Write automation detected in $f — manual-first: run playbook manually once first"
        fi
        ;;
    esac
  done
}

# ─── Knowledge: "Repo Authority And Source Of Truth" + "Exact Rulings" ───
# note-082ff726ae7c432b9b99cebb825f00b7
# note-42b98a630a3f43fab3f6888628089262
# Rule: AGENTS.md is the instruction surface — changes need care

check_governance_file_changes() {
  for f in "${CHANGED_FILES[@]}"; do
    case "$f" in
      AGENTS.md|CLAUDE.md|WARBIRD_MODEL_SPEC.md)
        # These are governance files — flag large changes
        local main_lines current_lines
        main_lines="$(git show origin/main:"$f" 2>/dev/null | wc -l | tr -d ' ' || echo 0)"
        if [[ "$MODE" == "pre-commit" ]]; then
          current_lines="$(git show :"$f" 2>/dev/null | wc -l | tr -d ' ' || echo 0)"
        else
          current_lines="$(wc -l < "$f" 2>/dev/null | tr -d ' ' || echo 0)"
        fi

        if [[ "$main_lines" -gt 0 && "$current_lines" -gt 0 ]]; then
          local change_pct
          if [[ "$current_lines" -lt "$main_lines" ]]; then
            change_pct=$(( (main_lines - current_lines) * 100 / main_lines ))
          else
            change_pct=$(( (current_lines - main_lines) * 100 / main_lines ))
          fi
          if [[ "$change_pct" -gt 20 ]]; then
            add_violation "Repo Authority And Source Of Truth" "note-082ff726" \
              "Governance file $f changed by ${change_pct}% — verify this is intentional and Kirk-approved"
          fi
        fi
        ;;
    esac
  done
}

# ─── Knowledge: "Session 13c8 Failure Pattern" ───
# note-db63edb0358840a88d3068c0b11e9bf7
# Rule: Watch for V7/V8 references in new code

check_no_v7_v8_references() {
  for f in "${CHANGED_FILES[@]}"; do
    [[ -f "$f" ]] || continue
    case "$f" in
      *.py|*.ts|*.tsx|*.js|*.jsx|*.pine)
        # Skip retired files themselves and docs
        case "$f" in
          indicators/v7-*|indicators/v8-*|indicators/Warbird_Pro_v7*|docs/*) continue ;;
        esac
        # Check for imports/references to retired V7/V8 surfaces
        if grep -qE '(v7.warbird|v8.warbird|Warbird_Pro_v7|warbird-pro-indicator)' "$f" 2>/dev/null; then
          add_violation "Session 13c8 Failure Pattern" "note-db63edb0" \
            "V7/V8 retired surface reference found in $f — only V9 is active"
        fi
        ;;
    esac
  done
}

# ─── Knowledge: Pine protection (from AGENTS.md Hard Rules) ───
# Enforces: never edit Pine without approval
# (This is defense-in-depth alongside hook-pre-plan-contract.sh)

check_pine_edit_protection() {
  for f in "${CHANGED_FILES[@]}"; do
    case "$f" in
      indicators/warbird-pro-v9.pine|indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine)
        # Pine edits in a Devin session need extra scrutiny
        # We can't block outright (Kirk might have approved), but we add a loud warning
        echo "⚠ WARNING: Protected Pine file modified: $f"
        echo "  → Requires explicit Kirk approval in the current session"
        echo "  → Run all 6 Pine verification gates before pushing"
        ;;
    esac
  done
}

# ═══════════════════════════════════════════════════════════════════════
# RUN ALL CHECKS
# ═══════════════════════════════════════════════════════════════════════

echo "ENFORCEMENT: knowledge note checks ($MODE)"

collect_changed_files

if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
  echo "INFO: no changed files in scope; knowledge enforcement checks pass."
  exit 0
fi

echo "INFO: checking ${#CHANGED_FILES[@]} files against Knowledge enforcement rules"

check_no_force_push_in_changes
check_no_legacy_training
check_no_fake_data_labels
check_no_vercel_demotion
check_no_autofix_commit_messages
check_no_unauthorized_automation
check_governance_file_changes
check_no_v7_v8_references
check_pine_edit_protection

report_and_exit

echo "PASS: knowledge enforcement checks clean"
