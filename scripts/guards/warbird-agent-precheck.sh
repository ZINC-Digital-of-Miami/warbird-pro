#!/usr/bin/env bash
# Codex-owned deterministic local precheck for commits, pushes, and manual review.

set -euo pipefail

MODE="manual"

usage() {
  cat <<'USAGE'
Usage: scripts/guards/warbird-agent-precheck.sh [--mode pre-commit|pre-push|manual]

pre-commit: fast checks on staged files only.
pre-push:   full local quality lane over @{upstream}...HEAD.
manual:     full local quality lane over staged files, or worktree files if nothing is staged.

This gate is local-only. It does not call Vercel, GitHub hosted checks, Claude,
or a nested Codex review.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "FAIL: unknown argument '$1'"
      usage
      exit 2
      ;;
  esac
done

case "$MODE" in
  pre-commit|pre-push|manual) ;;
  *)
    echo "FAIL: invalid mode '$MODE'"
    usage
    exit 2
    ;;
esac

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

LOG_DIR="$ROOT_DIR/.git/warbird-prechecks"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date -u +%Y%m%dT%H%M%SZ)-$MODE.log"
ln -sf "$(basename "$LOG_FILE")" "$LOG_DIR/latest.log"

exec > >(tee "$LOG_FILE") 2>&1

fail() {
  echo
  echo "FAIL: $*"
  echo "PRECHECK LOG: $LOG_FILE"
  exit 1
}

run_agents_process_reaper() {
  local reaper_script="$ROOT_DIR/agents/scripts/process_reaper.py"
  local python_cmd=""

  [[ -f "$reaper_script" ]] || return 0

  if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    python_cmd="$ROOT_DIR/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    python_cmd="$(command -v python3)"
  else
    echo "WARN: skipped agents process cleanup (python runtime not found)."
    return 0
  fi

  "$python_cmd" "$reaper_script" \
    --orphan-only \
    --max-age-seconds 1200 \
    --port-start 8090 \
    --port-end 8120 \
    --quiet >/dev/null 2>&1 || echo "WARN: agents process cleanup reported non-zero exit."
}

require_hooks_path() {
  local hooks_path
  hooks_path="$(git config --get core.hooksPath || true)"
  if [[ "$hooks_path" != ".githooks" ]]; then
    fail "core.hooksPath is '$hooks_path', expected '.githooks'. Run: git config core.hooksPath .githooks"
  fi
}

resolve_upstream_ref() {
  local upstream_ref
  upstream_ref="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)"
  [[ -n "$upstream_ref" ]] || fail "pre-push needs an upstream branch; set one with: git branch --set-upstream-to origin/$(git rev-parse --abbrev-ref HEAD)"
  echo "$upstream_ref"
}

cat <<EOF
============================================================
WARBIRD CODEX LOCAL PRECHECK
Mode: $MODE
Repo: $ROOT_DIR
Log:  $LOG_FILE
============================================================
EOF

require_hooks_path
run_agents_process_reaper

echo "INFO: branch $(git rev-parse --abbrev-ref HEAD)"
echo "INFO: head $(git rev-parse --short HEAD)"
echo "INFO: working tree status"
git status --short --branch

case "$MODE" in
  pre-commit)
    staged_count="$(git diff --cached --name-only --diff-filter=ACMR | sed '/^$/d' | wc -l | tr -d ' ')"
    [[ "$staged_count" -gt 0 ]] || fail "pre-commit saw no staged files."

    if ! git diff --quiet --exit-code; then
      echo "WARN: unstaged tracked changes exist; pre-commit checks staged files only."
    fi
    if [[ -n "$(git ls-files --others --exclude-standard)" ]]; then
      echo "WARN: untracked files exist; pre-commit checks staged files only."
    fi

    "$ROOT_DIR/scripts/guards/check-local-quality-lane.sh" --scope staged --fast
    ;;

  pre-push)
    if [[ -n "$(git status --porcelain)" ]]; then
      echo "WARN: working tree is dirty; pre-push checks committed range only."
    fi

    upstream_ref="$(resolve_upstream_ref)"
    if git diff --quiet "$upstream_ref"...HEAD; then
      echo "INFO: no commit-range diff against $upstream_ref; running baseline full lane."
    else
      echo "INFO: checking commit range $upstream_ref...HEAD"
    fi

    "$ROOT_DIR/scripts/guards/check-local-quality-lane.sh" --scope range --base-ref "$upstream_ref" --full
    ;;

  manual)
    "$ROOT_DIR/scripts/guards/check-local-quality-lane.sh" --scope auto --full
    ;;
esac

echo "PASS: Warbird local precheck complete"
echo "PRECHECK LOG: $LOG_FILE"
