#!/usr/bin/env bash
# Installs tc-tracker skills into .kilocode/skills and installs tc_validator into ~/bin.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC_DIR="$ROOT_DIR/.claude/skills"
DEST_DIR="$ROOT_DIR/.kilocode/skills"
VALIDATOR_SRC="$ROOT_DIR/scripts/validators/tc_validator.sh"
VALIDATOR_DEST="$HOME/bin/tc_validator"

die() {
  echo "FAIL: $*" >&2
  exit 1
}

ensure_symlink() {
  local src="$1"
  local dest="$2"

  [[ -e "$src" || -L "$src" ]] || die "source missing: $src"

  if [[ -L "$dest" ]]; then
    local target
    target="$(readlink "$dest")"
    if [[ "$target" == "$src" ]]; then
      echo "OK: $dest already linked"
      return 0
    fi
    die "existing symlink points elsewhere: $dest -> $target"
  fi

  if [[ -e "$dest" ]]; then
    die "destination exists and is not a symlink: $dest"
  fi

  ln -s "$src" "$dest"
  echo "LINK: $dest -> $src"
}

echo "Installing tc-tracker into: $ROOT_DIR"
mkdir -p "$DEST_DIR"

tc_skills=(
  tc-strategies-backtesting
  tc-example-strategies
  tc-advanced-pine
  tc-alerts
  tc-plots
  tc-bar-coloring
  tc-visual-output
  tc-technical-analysis
  tc-math
  tc-operators
  tc-indicators-basics
)

for skill in "${tc_skills[@]}"; do
  ensure_symlink "$SRC_DIR/$skill" "$DEST_DIR/$skill"
done

ensure_symlink "$SRC_DIR/tc-README.md" "$DEST_DIR/tc-README.md"

[[ -x "$VALIDATOR_SRC" ]] || chmod +x "$VALIDATOR_SRC"
mkdir -p "$HOME/bin"

if [[ -e "$VALIDATOR_DEST" && ! -L "$VALIDATOR_DEST" ]]; then
  die "cannot install tc_validator: $VALIDATOR_DEST exists and is not a symlink"
fi

if [[ -L "$VALIDATOR_DEST" ]]; then
  target="$(readlink "$VALIDATOR_DEST")"
  if [[ "$target" != "$VALIDATOR_SRC" ]]; then
    rm -f "$VALIDATOR_DEST"
    ln -s "$VALIDATOR_SRC" "$VALIDATOR_DEST"
    echo "RELINK: $VALIDATOR_DEST -> $VALIDATOR_SRC"
  else
    echo "OK: tc_validator already linked at $VALIDATOR_DEST"
  fi
else
  ln -s "$VALIDATOR_SRC" "$VALIDATOR_DEST"
  echo "LINK: $VALIDATOR_DEST -> $VALIDATOR_SRC"
fi

echo
echo "tc-tracker install complete."
echo "Next checks:"
echo "  1) hermes skills list | rg 'tc-|tc-tracker'"
echo "  2) tc_validator --fast"
