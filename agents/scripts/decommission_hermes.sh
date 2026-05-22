#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REAPER_RUNNER="$ROOT_DIR/agents/scripts/run_process_reaper.sh"

PLISTS=(
  "$HOME/Library/LaunchAgents/ai.hermes.gateway.plist"
  "$HOME/Library/LaunchAgents/com.warbird.hermes.cron-tick.plist"
)

echo "INFO: starting Hermes decommission (safe mode)"

for plist in "${PLISTS[@]}"; do
  if [[ -f "$plist" ]]; then
    launchctl unload "$plist" >/dev/null 2>&1 || true
    rm -f "$plist"
    echo "PASS: removed $plist"
  else
    echo "INFO: not present $plist"
  fi
done

# Stop known Hermes runtime process signatures.
pkill -f "hermes-agent" >/dev/null 2>&1 || true
pkill -f "warbird_hermes_" >/dev/null 2>&1 || true
pkill -f "/\.hermes/mcp/" >/dev/null 2>&1 || true

if [[ -x "$REAPER_RUNNER" ]]; then
  "$REAPER_RUNNER" >/dev/null 2>&1 || true
fi

echo "PASS: Hermes runtime decommissioned."
echo "INFO: next step is migrating kept assets under agents/ and pruning legacy mirrors."
