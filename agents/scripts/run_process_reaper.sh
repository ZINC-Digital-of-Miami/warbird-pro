#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REAPER="$ROOT_DIR/agents/scripts/process_reaper.py"

if [[ ! -f "$REAPER" ]]; then
  exit 0
fi

PYTHON_CMD=""
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_CMD="$ROOT_DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="$(command -v python3)"
else
  exit 0
fi

exec "$PYTHON_CMD" "$REAPER" \
  --orphan-only \
  --max-age-seconds 1200 \
  --port-start 8090 \
  --port-end 8120 \
  --quiet
