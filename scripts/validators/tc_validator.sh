#!/usr/bin/env bash
# tc_validator: Warbird task-completion validator with agents-surface checks.

set -euo pipefail

SCOPE="auto"
BASE_REF=""
INTENSITY="full"
SKIP_QUALITY=0
SKIP_RUNTIME=0

usage() {
  cat <<'USAGE'
Usage: tc_validator [options]

Options:
  --scope staged|worktree|range|auto   Changed-file scope for quality lane (default: auto)
  --base-ref <ref>                     Required when --scope range
  --fast                               Run fast quality lane (skip npm lint/build + pytest lane)
  --full                               Run full quality lane (default)
  --skip-quality-lane                  Skip scripts/guards/check-local-quality-lane.sh
  --skip-runtime                       Skip agents runtime surface checks
  --skip-hermes                        Deprecated alias for --skip-runtime
  -h, --help                           Show this help
USAGE
}

die() {
  echo "FAIL: $*" >&2
  exit 1
}

run_step() {
  local label="$1"
  shift
  echo
  echo "==> $label"
  "$@"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --scope)
      SCOPE="${2:-}"
      shift 2
      ;;
    --base-ref)
      BASE_REF="${2:-}"
      shift 2
      ;;
    --fast)
      INTENSITY="fast"
      shift
      ;;
    --full)
      INTENSITY="full"
      shift
      ;;
    --skip-quality-lane)
      SKIP_QUALITY=1
      shift
      ;;
    --skip-runtime|--skip-hermes)
      SKIP_RUNTIME=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument '$1'"
      ;;
  esac
done

case "$SCOPE" in
  staged|worktree|range|auto) ;;
  *)
    die "invalid scope '$SCOPE' (expected staged|worktree|range|auto)"
    ;;
esac

if [[ "$SCOPE" == "range" && -z "$BASE_REF" ]]; then
  die "--scope range requires --base-ref"
fi

if [[ -n "$BASE_REF" ]]; then
  git rev-parse --verify "${BASE_REF}^{commit}" >/dev/null 2>&1 || die "base ref '$BASE_REF' is not a valid commit-ish"
fi

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ROOT_DIR" || ! -d "$ROOT_DIR" ]]; then
  die "not inside a git worktree"
fi
cd "$ROOT_DIR"

[[ -f "AGENTS.md" ]] || die "AGENTS.md missing at repo root ($ROOT_DIR)"

echo "============================================================"
echo "tc_validator"
echo "repo: $ROOT_DIR"
echo "scope: $SCOPE"
echo "intensity: $INTENSITY"
if [[ -n "$BASE_REF" ]]; then
  echo "base_ref: $BASE_REF"
fi
echo "============================================================"

run_step "Git status preflight" git status --short --branch

if [[ "$SKIP_QUALITY" -eq 0 ]]; then
  qlane_cmd=(./scripts/guards/check-local-quality-lane.sh --scope "$SCOPE")
  if [[ "$SCOPE" == "range" ]]; then
    qlane_cmd+=(--base-ref "$BASE_REF")
  fi
  if [[ "$INTENSITY" == "fast" ]]; then
    qlane_cmd+=(--fast)
  else
    qlane_cmd+=(--full)
  fi
  run_step "Warbird local quality lane" "${qlane_cmd[@]}"
else
  echo "INFO: skipping local quality lane (--skip-quality-lane)"
fi

if [[ "$SKIP_RUNTIME" -eq 0 ]]; then
  run_step "Agents umbrella surface check" test -f "agents/README.md"
  run_step "Agents manifest check" test -f "agents/manifest.yaml"
  run_step "Agents skills registry check" test -f "agents/skills/README.md"
  run_step "Agents roles registry check" test -f "agents/roles/README.md"
  run_step "Quant Analyst role check" test -f "agents/roles/quant-analyst.agent.md"
  run_step "Process reaper lane check" test -f "agents/scripts/process_reaper.py"
else
  echo "INFO: skipping runtime surface checks (--skip-runtime)"
fi

echo
echo "PASS: tc_validator completed successfully"
