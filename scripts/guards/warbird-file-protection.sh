#!/usr/bin/env bash
# Hard enforcement gate: blocks file deletions and .gitignore additions
# for protected paths. Runs as part of pre-commit and pre-push hooks.
#
# This is NOT advisory. This is exit 1. No override except Kirk in the
# current session.
#
# Enforces:
#   - Knowledge: "Main Only And Push Approval" (no-delete, no-gitignore)
#   - Knowledge: "Repo Authority And Source Of Truth" (plan docs are permanent)
#   - Knowledge: "Exact Rulings No Interpretation" (literal rule application)
#   - .devin/rules/02-hard-rules.md "File Deletion / Removal"
#   - .devin/rules/03-git-protocol.md (no delete tracked files)
#   - .devin/rules/07-common-mistakes.md (2026-05-29 incident)
#   - AGENTS.md Process section (no-delete planning artifacts)
#
# Usage:
#   warbird-file-protection.sh --mode pre-commit|pre-push|manual
#
# Exit codes:
#   0 = all checks passed
#   1 = violation detected (hard block)
#   2 = usage error

set -euo pipefail

MODE="${1:-manual}"
case "$MODE" in
  --mode) MODE="${2:-manual}" ;;
esac
# Strip leading --mode if passed as first arg
case "$MODE" in
  pre-commit|pre-push|manual) ;;
  *)
    echo "Usage: warbird-file-protection.sh --mode pre-commit|pre-push|manual"
    exit 2
    ;;
esac

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

MANIFEST="$ROOT_DIR/scripts/guards/enforcement-manifest.json"
VIOLATIONS=()

# ─── Protected path lists (from enforcement-manifest.json, hardcoded as backup) ───

NEVER_DELETE_PATHS=(
  "docs/plans/"
  "docs/handoffs/"
  "agents/skills/"
  "docs/contracts/"
  "docs/runbooks/"
  ".devin/rules/"
  ".devin/playbooks/"
)

NEVER_GITIGNORE_PATHS=(
  "docs/"
  "agents/"
  ".devin/"
)

# ─── Helpers ───

add_violation() {
  VIOLATIONS+=("$1")
}

report_and_exit() {
  if [[ ${#VIOLATIONS[@]} -eq 0 ]]; then
    return 0
  fi

  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  WARBIRD FILE PROTECTION — HARD BLOCK                      ║"
  echo "╠══════════════════════════════════════════════════════════════╣"
  echo "║                                                              ║"
  echo "║  Planning artifacts are PERMANENT project history.           ║"
  echo "║  They are not disposable scaffolding.                        ║"
  echo "║                                                              ║"
  echo "║  To proceed: get explicit Kirk approval in current session.  ║"
  echo "║                                                              ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "VIOLATIONS:"
  for v in "${VIOLATIONS[@]}"; do
    echo "  ✘ $v"
  done
  echo ""
  echo "Knowledge notes enforced:"
  echo "  - Main Only And Push Approval"
  echo "  - Repo Authority And Source Of Truth"
  echo "  - Exact Rulings No Interpretation"
  echo ""
  exit 1
}

# ─── Check 1: Detect deleted files in protected paths ───

check_deleted_files() {
  local deleted_files=()

  case "$MODE" in
    pre-commit)
      while IFS= read -r f; do
        [[ -n "$f" ]] && deleted_files+=("$f")
      done < <(git diff --cached --name-only --diff-filter=D 2>/dev/null)
      ;;
    pre-push)
      local upstream_ref
      upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo 'origin/main')"
      while IFS= read -r f; do
        [[ -n "$f" ]] && deleted_files+=("$f")
      done < <(git diff --name-only --diff-filter=D "$upstream_ref"...HEAD 2>/dev/null)
      ;;
    manual)
      while IFS= read -r f; do
        [[ -n "$f" ]] && deleted_files+=("$f")
      done < <(git diff --cached --name-only --diff-filter=D 2>/dev/null)
      while IFS= read -r f; do
        [[ -n "$f" ]] && deleted_files+=("$f")
      done < <(git diff --name-only --diff-filter=D 2>/dev/null)
      ;;
  esac

  for f in "${deleted_files[@]}"; do
    for protected in "${NEVER_DELETE_PATHS[@]}"; do
      if [[ "$f" == "$protected"* ]]; then
        add_violation "DELETED protected file: $f (protected path: $protected)"
      fi
    done
  done
}

# ─── Check 2: Detect protected paths added to .gitignore ───

check_gitignore_additions() {
  local gitignore="$ROOT_DIR/.gitignore"
  [[ -f "$gitignore" ]] || return 0

  # Check staged .gitignore changes
  local gitignore_diff=""
  case "$MODE" in
    pre-commit)
      gitignore_diff="$(git diff --cached -- .gitignore 2>/dev/null || true)"
      ;;
    pre-push)
      local upstream_ref
      upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo 'origin/main')"
      gitignore_diff="$(git diff "$upstream_ref"...HEAD -- .gitignore 2>/dev/null || true)"
      ;;
    manual)
      gitignore_diff="$(git diff --cached -- .gitignore 2>/dev/null || true)"
      if [[ -z "$gitignore_diff" ]]; then
        gitignore_diff="$(git diff -- .gitignore 2>/dev/null || true)"
      fi
      ;;
  esac

  [[ -n "$gitignore_diff" ]] || return 0

  # Extract added lines (lines starting with +, excluding +++ header)
  local added_lines
  added_lines="$(echo "$gitignore_diff" | grep '^+[^+]' | sed 's/^+//' || true)"
  [[ -n "$added_lines" ]] || return 0

  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    # Strip leading/trailing whitespace and comments
    line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -n "$line" && "$line" != "#"* ]] || continue

    for protected in "${NEVER_GITIGNORE_PATHS[@]}"; do
      if [[ "$line" == *"$protected"* || "$line" == "$protected"* ]]; then
        add_violation "GITIGNORED protected path: '$line' matches protected: $protected"
      fi
    done
  done <<< "$added_lines"
}

# ─── Check 3: Detect overwrites of plan/handoff files with older content ───

check_plan_overwrites() {
  local modified_files=()

  case "$MODE" in
    pre-commit)
      while IFS= read -r f; do
        [[ -n "$f" ]] && modified_files+=("$f")
      done < <(git diff --cached --name-only --diff-filter=M 2>/dev/null)
      ;;
    pre-push)
      local upstream_ref
      upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo 'origin/main')"
      while IFS= read -r f; do
        [[ -n "$f" ]] && modified_files+=("$f")
      done < <(git diff --name-only --diff-filter=M "$upstream_ref"...HEAD 2>/dev/null)
      ;;
    manual)
      while IFS= read -r f; do
        [[ -n "$f" ]] && modified_files+=("$f")
      done < <(git diff --cached --name-only --diff-filter=M 2>/dev/null)
      ;;
  esac

  for f in "${modified_files[@]}"; do
    # Only check docs/plans/ and docs/handoffs/
    case "$f" in
      docs/plans/*|docs/handoffs/*) ;;
      *) continue ;;
    esac

    # Compare line counts: if staged version is significantly shorter, warn
    local main_lines staged_lines
    main_lines="$(git show origin/main:"$f" 2>/dev/null | wc -l | tr -d ' ')" || main_lines=0
    if [[ "$MODE" == "pre-commit" ]]; then
      staged_lines="$(git show :"$f" 2>/dev/null | wc -l | tr -d ' ')" || staged_lines=0
    else
      staged_lines="$(wc -l < "$f" 2>/dev/null | tr -d ' ')" || staged_lines=0
    fi

    if [[ "$main_lines" -gt 0 && "$staged_lines" -gt 0 ]]; then
      local reduction_pct=$(( (main_lines - staged_lines) * 100 / main_lines ))
      if [[ "$reduction_pct" -gt 15 ]]; then
        add_violation "PLAN OVERWRITE: $f shrunk by ${reduction_pct}% (${main_lines} → ${staged_lines} lines). Verify this is intentional — do not overwrite with older/shorter versions."
      fi
    fi
  done
}

# ─── Check 4: Detect retired surface reactivation ───

check_retired_surfaces() {
  local changed_files=()

  case "$MODE" in
    pre-commit)
      while IFS= read -r f; do
        [[ -n "$f" ]] && changed_files+=("$f")
      done < <(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null)
      ;;
    pre-push)
      local upstream_ref
      upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo 'origin/main')"
      while IFS= read -r f; do
        [[ -n "$f" ]] && changed_files+=("$f")
      done < <(git diff --name-only --diff-filter=ACMR "$upstream_ref"...HEAD 2>/dev/null)
      ;;
    manual)
      while IFS= read -r f; do
        [[ -n "$f" ]] && changed_files+=("$f")
      done < <(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null)
      ;;
  esac

  local retired=(
    "indicators/v8-warbird-live.pine"
    "indicators/v8-warbird-prescreen.pine"
    "indicators/warbird-pro-indicator.pine"
    "indicators/Warbird_Pro_v7.pine"
    "indicators/v7-warbird-institutional.pine"
    "indicators/v7-warbird-strategy.pine"
    "indicators/v7-warbird-institutional-backtest-strategy.pine"
    "indicators/fibs-only.pine"
    "scripts/ag/train_ag_baseline.py"
    "scripts/ag/train_hard_gate.py"
  )

  for f in "${changed_files[@]}"; do
    for r in "${retired[@]}"; do
      if [[ "$f" == "$r" ]]; then
        add_violation "RETIRED SURFACE modified: $f — this surface is retired per AGENTS.md. Do not reactivate without explicit Kirk approval."
      fi
    done
  done
}

# ─── Check 5: Detect --force-push or --no-verify in recent git commands ───
# (This catches it in commit messages or scripts; the hooks themselves already
#  prevent --no-verify from working, but this catches attempts to encode it.)

check_force_push_markers() {
  local changed_files=()

  case "$MODE" in
    pre-commit)
      while IFS= read -r f; do
        [[ -n "$f" ]] && changed_files+=("$f")
      done < <(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null)
      ;;
    *)
      return 0
      ;;
  esac

  for f in "${changed_files[@]}"; do
    [[ -f "$f" ]] || continue
    case "$f" in
      *.sh|*.bash|*.py|*.md|*.yml|*.yaml)
        if grep -qE '(--force-with-lease|--force|--no-verify|force.push)' "$f" 2>/dev/null; then
          # Skip guard scripts, manifest, rules, and docs that document forbidden patterns
          case "$f" in
            scripts/guards/warbird-file-protection.sh) continue ;;
            scripts/guards/enforcement-manifest.json) continue ;;
            scripts/guards/warbird-knowledge-enforcement.sh) continue ;;
            scripts/guards/warbird-agent-precheck.sh) continue ;;
            .devin/rules/*) continue ;;
            .devin/playbooks/*) continue ;;
            .githooks/*) continue ;;
            AGENTS.md|CLAUDE.md) continue ;;
            docs/*) continue ;;
            *) add_violation "FORCE PUSH/NO-VERIFY reference in: $f — these operations are forbidden per Knowledge 'Main Only And Push Approval'" ;;
          esac
        fi
        ;;
    esac
  done
}

# ─── Run all checks ───

echo "ENFORCEMENT: file protection checks ($MODE)"

check_deleted_files
check_gitignore_additions
check_plan_overwrites
check_retired_surfaces
check_force_push_markers

report_and_exit

echo "PASS: file protection checks clean"
