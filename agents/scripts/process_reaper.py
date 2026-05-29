#!/usr/bin/env python3
"""Lightweight orphan/stale process cleanup for the Warbird workspace.

This script intentionally targets only known workspace signatures and defaults
to orphan-only cleanup so active sessions are not disrupted.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]

# Process signatures known to drift after IDE/terminal disconnects.
SIGNATURES = (
    "warbird_optuna_hub.py",
    "tv_bridge_worker.mjs",
    "next dev",
    "next-server",
)

# Never touch these even if they match broad patterns.
PROTECTED_MARKERS = (
    "TradingView",
    "tv_connection_doctor.py",
    "process_reaper.py",
)


@dataclass
class ProcRow:
    pid: int
    ppid: int
    etimes: int
    command: str


def _run(cmd: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except Exception:
        return 99, ""
    return result.returncode, result.stdout


def list_processes() -> list[ProcRow]:
    code, out = _run(["ps", "-axo", "pid=,ppid=,etimes=,command="])
    if code != 0:
        return []
    rows: list[ProcRow] = []
    for raw in out.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split(maxsplit=3)
        if len(parts) < 4:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
            etimes = int(parts[2])
        except ValueError:
            continue
        rows.append(ProcRow(pid=pid, ppid=ppid, etimes=etimes, command=parts[3]))
    return rows


def proc_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def kill_pid(pid: int, grace_seconds: float = 2.5) -> str:
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        return "already-exited"

    deadline = time.time() + grace_seconds
    while time.time() < deadline:
        if not proc_exists(pid):
            return "terminated"
        time.sleep(0.1)

    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        return "already-exited"
    return "killed"


def _matches_signature(cmd: str, signatures: Iterable[str]) -> bool:
    return any(sig in cmd for sig in signatures)


def _is_protected(cmd: str) -> bool:
    return any(marker in cmd for marker in PROTECTED_MARKERS)


def _is_workspace_related(cmd: str) -> bool:
    repo = str(REPO_ROOT)
    return repo in cmd or _matches_signature(cmd, SIGNATURES)


def _candidate(
    row: ProcRow,
    known_pids: set[int],
    orphan_only: bool,
    max_age_seconds: int,
    signatures: Iterable[str],
) -> bool:
    if row.pid == os.getpid():
        return False
    if _is_protected(row.command):
        return False
    if not _is_workspace_related(row.command):
        return False
    if not _matches_signature(row.command, signatures):
        return False

    parent_missing = row.ppid == 1 or row.ppid not in known_pids
    stale = row.etimes >= max_age_seconds

    if orphan_only:
        return parent_missing and stale
    return stale


def _pid_for_ports(ports: Iterable[int]) -> set[int]:
    pids: set[int] = set()
    for port in ports:
        code, out = _run(["lsof", "-nP", "-iTCP:" + str(port), "-sTCP:LISTEN", "-t"])
        if code != 0:
            continue
        for line in out.splitlines():
            raw = line.strip()
            if not raw:
                continue
            try:
                pids.add(int(raw))
            except ValueError:
                continue
    return pids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Warbird orphan process reaper")
    parser.add_argument("--dry-run", action="store_true", help="report only")
    parser.add_argument(
        "--orphan-only",
        action="store_true",
        default=True,
        help="kill only orphaned processes",
    )
    parser.add_argument(
        "--include-non-orphans",
        action="store_true",
        help="also kill stale non-orphan processes that match known signatures",
    )
    parser.add_argument(
        "--max-age-seconds",
        type=int,
        default=1200,
        help="minimum process age before cleanup",
    )
    parser.add_argument("--port-start", type=int, default=8090)
    parser.add_argument("--port-end", type=int, default=8120)
    parser.add_argument("--extra-port", action="append", type=int, default=[])
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--json-report", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    orphan_only = not args.include_non_orphans
    max_age = max(1, args.max_age_seconds)

    all_rows = list_processes()
    known_pids = {r.pid for r in all_rows}

    ports = list(range(min(args.port_start, args.port_end), max(args.port_start, args.port_end) + 1))
    ports.extend(args.extra_port)
    port_owner_pids = _pid_for_ports(ports)

    victims: list[ProcRow] = []
    for row in all_rows:
        is_candidate = _candidate(
            row,
            known_pids=known_pids,
            orphan_only=orphan_only,
            max_age_seconds=max_age,
            signatures=SIGNATURES,
        )
        if not is_candidate:
            continue
        # If process owns watched ports, always include. Otherwise keep orphan stale rule.
        if row.pid in port_owner_pids or row.ppid == 1 or row.ppid not in known_pids:
            victims.append(row)

    actions: list[dict[str, str | int]] = []
    for row in victims:
        outcome = "dry-run"
        if not args.dry_run:
            outcome = kill_pid(row.pid)
        actions.append(
            {
                "pid": row.pid,
                "ppid": row.ppid,
                "age_seconds": row.etimes,
                "outcome": outcome,
                "command": row.command,
            }
        )

    report = {
        "repo_root": str(REPO_ROOT),
        "dry_run": args.dry_run,
        "orphan_only": orphan_only,
        "max_age_seconds": max_age,
        "victim_count": len(actions),
        "actions": actions,
    }

    if args.json_report:
        Path(args.json_report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if not args.quiet:
        print(json.dumps(report, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
