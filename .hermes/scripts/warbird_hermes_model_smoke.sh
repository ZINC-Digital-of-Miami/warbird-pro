#!/usr/bin/env bash
set -euo pipefail

# Warbird Hermes model-routing smoke tests. Exact-response tests only.
# Does not mutate repo/config and bypasses project hooks to keep this a provider test.

export HERMES_NO_AGENT_HOOKS=1
REPO="/Volumes/Satechi Hub/warbird-pro"
cd "$REPO"

run_smoke() {
  local label="$1" provider="$2" model="$3" expected="$4"
  printf '== %s (%s / %s) ==\n' "$label" "$provider" "$model"
  local output
  if ! output=$(hermes chat -Q --provider "$provider" -m "$model" --ignore-rules -q "Reply exactly: ${expected}" 2>&1); then
    printf '%s\n' "$output"
    printf 'FAIL: %s command failed\n' "$label" >&2
    return 1
  fi
  printf '%s\n' "$output"
  if ! printf '%s\n' "$output" | grep -qx "$expected"; then
    printf 'FAIL: %s did not return exact marker %s\n' "$label" "$expected" >&2
    return 1
  fi
  printf 'PASS: %s\n\n' "$label"
}

run_smoke "primary-codex" "openai-codex" "gpt-5.5" "OPENAI_CODEX_CONNECTED"
run_smoke "copilot-non-claude" "copilot" "gpt-5.4-mini" "COPILOT_CONNECTED"
run_smoke "openrouter-free-fast" "openrouter" "google/gemini-2.5-flash-lite" "OPENROUTER_CONNECTED"

python3 - <<'PY'
import yaml
from pathlib import Path
cfg=yaml.safe_load(Path('/Users/zincdigital/.hermes/config.yaml').read_text())
fb=cfg.get('fallback_providers') or []
bad=[f for f in fb if f.get('provider')=='copilot' and any(tok in str(f.get('model','')).lower() for tok in ('claude','opus','sonnet'))]
vision=(cfg.get('auxiliary') or {}).get('vision') or {}
assert not bad, bad
assert vision.get('provider') == 'openrouter', vision
assert vision.get('model') == 'google/gemini-2.5-flash', vision
print('PASS: fallback assertions and vision auxiliary route')
PY
