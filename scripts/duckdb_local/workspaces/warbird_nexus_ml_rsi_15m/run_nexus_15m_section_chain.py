#!/usr/bin/env python3
"""Run Nexus 15m AG training one indicator section at a time.

The chain mirrors the old card-style discipline: train one section, inspect the
chronological OOS result, save/proceed if it clears gates, or optionally rerun
that same section with a larger budget before moving on. It never edits Pine and
never uses V9 artifacts.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
WORKSPACE = REPO_ROOT / "scripts" / "duckdb_local" / "workspaces" / "warbird_nexus_ml_rsi_15m"
TRAINER = WORKSPACE / "train_nexus_15m_heavy.py"
DEFAULT_MANIFEST = WORKSPACE / "exports" / "nexus_15m_dataset.manifest.json"
REPORTS_DIR = WORKSPACE / "reports"
SECTION_SEQUENCE = (
    "footprint_delta_flow",
    "volume_flow",
    "oscillator_regime",
    "divergence_exhaustion",
    "signal_tier_composite",
)


def _run(cmd: list[str]) -> None:
    print("$ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def _latest_summary() -> dict[str, Any]:
    path = REPORTS_DIR / "heavy_training_latest.json"
    if not path.exists():
        raise RuntimeError(f"Missing latest training summary: {path}")
    return json.loads(path.read_text())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--sections", nargs="+", default=list(SECTION_SEQUENCE))
    ap.add_argument("--start-at", choices=SECTION_SEQUENCE)
    ap.add_argument("--stop-after-one", action="store_true")
    ap.add_argument("--time-limit", type=int, default=14_400)
    ap.add_argument("--hpo-trials", type=int, default=80)
    ap.add_argument("--num-bag-folds", type=int, default=5)
    ap.add_argument("--num-bag-sets", type=int, default=2)
    ap.add_argument("--num-stack-levels", type=int, default=1)
    ap.add_argument("--dynamic-stacking", default="auto")
    ap.add_argument("--model-profile", default="neural_scout", choices=("full_zoo", "neural_scout"))
    ap.add_argument("--auto-rerun-on-fail", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    sections = list(args.sections)
    if args.start_at:
        sections = sections[sections.index(args.start_at):]
    if args.stop_after_one:
        sections = sections[:1]

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    chain_dir = REPORTS_DIR / f"section_chain_{run_id}"
    chain_dir.mkdir(parents=True, exist_ok=True)
    chain: dict[str, Any] = {
        "run_id": run_id,
        "sections": sections,
        "manifest": str(args.manifest),
        "settings": vars(args),
        "results": [],
        "scope_lock": "Nexus-only; no V9 Pine/trainer/export/model/fib surface used.",
    }
    (chain_dir / "chain_manifest.json").write_text(json.dumps(chain, indent=2, default=str))

    for section in sections:
        cmd = [
            sys.executable,
            str(TRAINER),
            "--manifest", str(args.manifest),
            "--section", section,
            "--time-limit", str(args.time_limit),
            "--hpo-trials", str(args.hpo_trials),
            "--num-bag-folds", str(args.num_bag_folds),
            "--num-bag-sets", str(args.num_bag_sets),
            "--num-stack-levels", str(args.num_stack_levels),
            "--dynamic-stacking", str(args.dynamic_stacking),
            "--model-profile", str(args.model_profile),
        ]
        if args.dry_run:
            print("$ " + " ".join(cmd), flush=True)
            continue
        _run(cmd)
        summary = _latest_summary()
        decision = summary.get("section_decision", {})
        chain["results"].append({
            "section": section,
            "decision": decision,
            "summary_path": str(summary.get("output_dir", "")),
            "test_metrics": summary.get("test_metrics", {}),
        })
        (chain_dir / "chain_manifest.json").write_text(json.dumps(chain, indent=2, default=str))
        (chain_dir / f"{section}_summary.json").write_text(json.dumps(summary, indent=2, default=str))
        if decision.get("decision") != "save_and_proceed":
            if not args.auto_rerun_on_fail:
                print(f"section {section} requires rerun/review; stopping chain", flush=True)
                return 2
            rerun_cmd = list(cmd)
            rerun_time_limit = str(max(args.time_limit * 2, args.time_limit + 3600))
            rerun_hpo_trials = str(max(args.hpo_trials * 2, args.hpo_trials + 40))
            rerun_cmd[rerun_cmd.index("--time-limit") + 1] = rerun_time_limit
            rerun_cmd[rerun_cmd.index("--hpo-trials") + 1] = rerun_hpo_trials
            _run(rerun_cmd)
            summary = _latest_summary()
            (chain_dir / f"{section}_rerun_summary.json").write_text(json.dumps(summary, indent=2, default=str))
            if summary.get("section_decision", {}).get("decision") != "save_and_proceed":
                print(f"section {section} still requires review after rerun; stopping chain", flush=True)
                return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
