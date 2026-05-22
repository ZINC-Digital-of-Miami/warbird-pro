#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PLIST_TEMPLATE="$ROOT_DIR/agents/launchd/com.warbird.agents.process-reaper.plist"
TARGET="$HOME/Library/LaunchAgents/com.warbird.agents.process-reaper.plist"
LOG_DIR="$HOME/Library/Logs/warbird-agents"

mkdir -p "$(dirname "$TARGET")"
mkdir -p "$LOG_DIR"

if [[ ! -f "$PLIST_TEMPLATE" ]]; then
  echo "FAIL: missing plist template: $PLIST_TEMPLATE" >&2
  exit 1
fi

sed "s|__REPO_ROOT__|$ROOT_DIR|g" "$PLIST_TEMPLATE" > "$TARGET"

launchctl unload "$TARGET" >/dev/null 2>&1 || true
launchctl load "$TARGET"

echo "PASS: installed launch agent at $TARGET"
echo "INFO: process reaper is now automatic (RunAtLoad + StartInterval)."
