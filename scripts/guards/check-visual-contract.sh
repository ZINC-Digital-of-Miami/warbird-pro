#!/usr/bin/env bash
# check-visual-contract.sh — mechanical enforcement of the visual contract.
#
# Architect's chart styling/labels/colors/widths/fib drawing was rebuilt many times
# after AI agents wrecked them while "promising not to touch fibs." Verbal
# commitments don't count anymore — this script does.
#
# Usage:
#   scripts/guards/check-visual-contract.sh [--snapshot path] [--source path]
#
# Defaults:
#   snapshot: .references/visual_contract_frozen_2026-04-29.txt
#   source:   indicators/v7-warbird-institutional-backtest-strategy.pine
#
# Exit codes:
#   0  All visual-contract regions match the frozen snapshot byte-for-byte.
#   1  At least one region has changed. Diffs printed.
#   2  Configuration error (file not found, marker not found, etc.).
#
# Marker design: each region's start/end markers use variable names or unique
# structural prefixes — NOT values. That way a deliberate value change shows up
# as a region-content diff (exit 1) rather than a marker-lookup failure (exit 2).
#
# Add this script to your pre-commit pipeline alongside pine-lint,
# check-fib-scanner-guardrails, and check-contamination.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

SNAPSHOT="${SNAPSHOT:-$ROOT_DIR/.references/visual_contract_frozen_2026-04-29.txt}"
SOURCE="${SOURCE:-$ROOT_DIR/indicators/v7-warbird-institutional-backtest-strategy.pine}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --snapshot) SNAPSHOT="$2"; shift 2 ;;
    --source)   SOURCE="$2"; shift 2 ;;
    --help|-h)
      sed -n '2,25p' "$0"
      exit 0
      ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

[[ -f "$SNAPSHOT" ]] || { echo "FAIL: snapshot not found: $SNAPSHOT" >&2; exit 2; }
[[ -f "$SOURCE" ]]   || { echo "FAIL: source not found: $SOURCE"   >&2; exit 2; }

CURRENT="$(mktemp)"
trap 'rm -f "$CURRENT"' EXIT

python3 - "$SOURCE" "$CURRENT" <<'PYEOF'
import sys

src_path, out_path = sys.argv[1], sys.argv[2]

with open(src_path, "r") as f:
    lines = f.readlines()

def starts_with(s):
    return lambda line: line.startswith(s)
def equals(s):
    return lambda line: line.rstrip("\n") == s
def contains(s):
    return lambda line: s in line

# Markers identify start/end by variable name or structural prefix — not by value.
# Value changes show up as content diff, not marker miss.
regions = [
    ("R01 — Color constants",
     starts_with("color COLOR_ANCHOR "),
     starts_with("color COLOR_ENTRY_LABEL")),
    ("R02 — Width constants",
     starts_with("int WIDTH_ANCHOR "),
     starts_with("int WIDTH_TARGET ")),
    ("R03 — groupViz visual inputs",
     starts_with("string groupViz ="),
     starts_with("int zoneFillTransparencyInput")),
    ("R04 — groupBrand watermark inputs",
     starts_with("string groupBrand ="),
     starts_with("color webWatermarkProColorInput")),
    ("R05 — Drawing helpers (f_line_style, f_label_size)",
     starts_with("f_line_style(string styleName)"),
     contains("size.tiny")),
    ("R06 — Drawing primitive declarations",
     starts_with("var line lineZero"),
     starts_with("var table webWatermarkTable")),
    ("R07 — drawAnchoredLine function",
     starts_with("drawAnchoredLine(line id, bool visible"),
     equals("        line.set_color(id, color(na))")),
    ("R08 — setFibLevelLabel function",
     starts_with("setFibLevelLabel(label idIn"),
     equals("    id")),
    ("R09 — drawAnchoredLine call block",
     starts_with("drawAnchoredLine(lineZero,"),
     starts_with("drawAnchoredLine(lineT5,")),
    ("R10 — setFibLevelLabel call block",
     equals("if barstate.islastconfirmedhistory"),
     contains("setFibLevelLabel(_fibLblT5")),
    ("R11 — Trade label drawing block",
     starts_with("if barstate.islast and showTradeLevels and not na(_lblEntry)"),
     equals("    label.set_color(_lblT5, color(na))")),
    ("R12 — Zone box drawing block",
     starts_with("if not na(zoneFillUpper) and not na(zoneFillLower)"),
     equals("    box.set_border_color(zoneBox, color(na))")),
    ("R13 — Watermark table cells render",
     equals("if barstate.islast"),
     contains("table.cell(webWatermarkTable, 1, 0, showWebWatermarkInput")),
    ("R14 — EMA/VWAP plot calls",
     starts_with("plot(showEma9Input ? ema9 : na"),
     starts_with("plot(showVwapInput ? vwapVal : na")),
]

def find_idx(predicate, lines, start_from=0):
    for i in range(start_from, len(lines)):
        if predicate(lines[i]):
            return i
    return -1

output = []
errors = []
for label, start_match, end_match in regions:
    output.append(f"===== {label} =====\n")
    si = find_idx(start_match, lines)
    if si < 0:
        errors.append(f"START marker not found for {label}")
        output.append("!!! START MARKER NOT FOUND\n\n")
        continue
    ei = find_idx(end_match, lines, si)
    if ei < 0:
        errors.append(f"END marker not found for {label} (start at line {si+1})")
        output.append("!!! END MARKER NOT FOUND\n\n")
        continue
    output.extend(lines[si:ei+1])
    output.append("\n")

with open(out_path, "w") as f:
    f.writelines(output)

if errors:
    print("Marker errors during extraction:", file=sys.stderr)
    for e in errors:
        print(f"  {e}", file=sys.stderr)
    print("This indicates a structural change to the visual contract — likely a", file=sys.stderr)
    print("rename or removal of a protected symbol. Treat as a violation.", file=sys.stderr)
    sys.exit(2)
PYEOF

if diff -u "$SNAPSHOT" "$CURRENT" > /tmp/visual_contract_diff.txt 2>&1; then
  echo "PASS: visual contract intact."
  echo "  snapshot: $SNAPSHOT"
  echo "  source:   $SOURCE"
  exit 0
else
  echo "FAIL: visual contract VIOLATED — see diff below."
  echo "  snapshot: $SNAPSHOT"
  echo "  source:   $SOURCE"
  echo
  echo "==== unified diff (expected | actual) ===="
  cat /tmp/visual_contract_diff.txt
  echo "==== end diff ===="
  echo
  echo "Per memory feedback_visual_contract_sacred.md and"
  echo "docs/contracts/visual_contract_line_ranges.md:"
  echo "  - Either revert the changed lines back to the frozen state, OR"
  echo "  - Get explicit Architect approval and use the manifest's update"
  echo "    procedure to regenerate the snapshot in an atomic commit."
  exit 1
fi
