#!/usr/bin/env bash
set -euo pipefail

TARGET="$HOME/Library/LaunchAgents/com.warbird.agents.process-reaper.plist"

if [[ -f "$TARGET" ]]; then
  launchctl unload "$TARGET" >/dev/null 2>&1 || true
  rm -f "$TARGET"
  echo "PASS: removed $TARGET"
else
  echo "INFO: launch agent not installed at $TARGET"
fi
