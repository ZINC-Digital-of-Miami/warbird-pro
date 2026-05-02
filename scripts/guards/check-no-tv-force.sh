#!/usr/bin/env bash
# check-no-tv-force.sh
# Fail if repo automation surfaces attempt to force-launch or restart TradingView.

set -euo pipefail

ROOT_DIR="${1:-.}"
cd "$ROOT_DIR"

if ! command -v rg >/dev/null 2>&1; then
  echo "FAIL: rg is required for check-no-tv-force.sh"
  exit 1
fi

scan_roots=()
[[ -d scripts ]] && scan_roots+=("scripts")
[[ -d .claude ]] && scan_roots+=(".claude")

if [[ ${#scan_roots[@]} -eq 0 ]]; then
  echo "PASS: no automation surfaces found to scan."
  exit 0
fi

pattern='launch_tv_debug_mac\.sh|(^|[^[:alnum:]_])tv_launch([^[:alnum:]_]|$)|pkill[[:space:]]+-f[[:space:]]+TradingView|killall[[:space:]]+TradingView'

hits="$(
  rg -n -S \
    --glob '*.{sh,bash,zsh,py,js,mjs,ts,json,toml,yaml,yml}' \
    --glob '!scripts/guards/check-no-tv-force.sh' \
    "$pattern" "${scan_roots[@]}" || true
)"

if [[ -n "$hits" ]]; then
  echo "FAIL: forbidden forced-TradingView automation pattern(s) detected."
  echo "$hits"
  exit 1
fi

echo "PASS: no forbidden forced-TradingView automation patterns detected."
