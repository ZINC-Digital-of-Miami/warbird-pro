#!/usr/bin/env python3
"""Warbird Hermes context/config doctor.

Read-only guard for the Hermes-first Warbird setup. It checks project context,
model routing, disabled messaging surfaces, MCP shape, launchd gateway state,
and common overlap hazards. It does not mutate repo, config, processes, or
network state.
"""
from __future__ import annotations

import json
import os
import plistlib
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path("/Volumes/Satechi Hub/warbird-pro")
CONFIG = Path("/Users/zincdigital/.hermes/config.yaml")
HERMES_HOME = Path("/Volumes/Satechi Hub/warbird-pro-state/hermes-home")
LOCAL_LOG_DIR = Path("/Users/zincdigital/Library/Logs/HermesAgent")
PROJECT_SKILLS = REPO / ".hermes/skills"
REQUIRED_CONTEXT_DOCS = [
    "AGENTS.md",
    "docs/INDEX.md",
    "docs/MASTER_PLAN.md",
    "docs/contracts/README.md",
    "docs/runbooks/startup_repo_review.md",
    "docs/cloud_scope.md",
    "WARBIRD_MODEL_SPEC.md",
    "CLAUDE.md",
    "docs/agent-safety-gates.md",
    ".hermes/rules/hermes-quality-policy.md",
    ".hermes/rules/validation-matrix.md",
]
EXPECTED_MCPS = {
    "warbird-status",
    "warbird-fetch",
    "warbird-filesystem",
    "warbird-github",
    "warbird-supabase-ro",
}
MUST_DISABLE_TOOLSETS = {
    "messaging",
    "discord",
    "discord_admin",
    "tts",
    "todo",
    "computer_use",
    "homeassistant",
    "spotify",
    "yuanbao",
    "feishu_doc",
    "feishu_drive",
}


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 30) -> tuple[int, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        return p.returncode, p.stdout.strip()
    except Exception as exc:  # pragma: no cover - defensive CLI reporting
        return 99, f"{type(exc).__name__}: {exc}"


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.ok: list[str] = []

    def check(self, condition: bool, ok: str, fail: str, warning: bool = False) -> None:
        if condition:
            self.ok.append(ok)
        elif warning:
            self.warnings.append(fail)
        else:
            self.failures.append(fail)

    def emit(self) -> int:
        print("WARBIRD_HERMES_CONTEXT_DOCTOR")
        print(f"repo={REPO}")
        print(f"config={CONFIG}")
        print(f"hermes_home={HERMES_HOME}")
        print()
        for item in self.ok:
            print(f"PASS: {item}")
        for item in self.warnings:
            print(f"WARN: {item}")
        for item in self.failures:
            print(f"FAIL: {item}")
        print()
        print(f"summary: pass={len(self.ok)} warn={len(self.warnings)} fail={len(self.failures)}")
        return 1 if self.failures else 0


def load_config(report: Report) -> dict[str, Any]:
    if not CONFIG.exists():
        report.check(False, "", f"missing Hermes config: {CONFIG}")
        return {}
    try:
        cfg = yaml.safe_load(CONFIG.read_text()) or {}
        report.ok.append("Hermes config parses as YAML")
        return cfg
    except Exception as exc:
        report.check(False, "", f"Hermes config failed to parse: {exc}")
        return {}


def main() -> int:
    report = Report()
    cfg = load_config(report)

    report.check(REPO.exists() and (REPO / ".git").exists(), "Warbird repo mount and .git exist", "Warbird repo mount/.git missing")
    missing_docs = [p for p in REQUIRED_CONTEXT_DOCS if not (REPO / p).exists()]
    report.check(not missing_docs, "required Warbird context docs are present", f"missing context docs: {missing_docs}")

    code, branch = run(["git", "branch", "--show-current"], REPO)
    report.check(code == 0 and branch == "main", "git branch is main", f"git branch is {branch!r}, expected main")
    code, upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], REPO)
    report.check(code == 0 and upstream == "origin/main", "git upstream is origin/main", f"git upstream is {upstream!r}, expected origin/main")

    model = cfg.get("model") or {}
    report.check(model.get("provider") == "openai-codex", "primary provider is openai-codex", f"primary provider is {model.get('provider')!r}")
    report.check(model.get("default") == "gpt-5.5", "primary model is gpt-5.5", f"primary model is {model.get('default')!r}")
    report.check(model.get("api_mode") == "codex_responses", "OpenAI Codex API mode is codex_responses", f"api_mode is {model.get('api_mode')!r}")

    fallbacks = cfg.get("fallback_providers") or []
    copilot_bad = [f for f in fallbacks if f.get("provider") == "copilot" and any(tok in str(f.get("model", "")).lower() for tok in ("claude", "opus", "sonnet"))]
    report.check(not copilot_bad, "Copilot fallback list has no Claude Opus/Sonnet models", f"forbidden Copilot Claude fallback entries: {copilot_bad}")
    report.check(any(f.get("provider") == "copilot" for f in fallbacks), "Copilot fallback lane exists", "Copilot fallback lane missing")
    report.check(any(f.get("provider") == "openrouter" for f in fallbacks), "OpenRouter fallback lane exists", "OpenRouter fallback lane missing")

    aux_vision = ((cfg.get("auxiliary") or {}).get("vision") or {})
    report.check(aux_vision.get("provider") == "openrouter" and aux_vision.get("model") == "google/gemini-2.5-flash", "vision auxiliary pinned to OpenRouter Gemini 2.5 Flash", f"vision auxiliary mismatch: {aux_vision}")
    aux = cfg.get("auxiliary") or {}
    nonvision_aux = ["compression", "web_extract", "skills_hub", "title_generation", "triage_specifier", "profile_describer"]
    bad_aux = {k: aux.get(k) for k in nonvision_aux if ((aux.get(k) or {}).get("provider") != "copilot" or (aux.get(k) or {}).get("model") != "gpt-5.4-mini")}
    report.check(not bad_aux, "non-vision auxiliary helpers use non-Claude Copilot gpt-5.4-mini", f"non-vision auxiliary route mismatch: {bad_aux}")
    comp = cfg.get("compression") or {}
    report.check(float(comp.get("threshold", 1.0)) <= 0.25, "compression threshold is <= 0.25 for helper context compatibility", f"compression threshold is {comp.get('threshold')!r}, expected <= 0.25")

    disabled = set(((cfg.get("agent") or {}).get("disabled_toolsets") or []))
    missing_disabled = sorted(MUST_DISABLE_TOOLSETS - disabled)
    report.check(not missing_disabled, "messaging/overlap-prone toolsets disabled", f"toolsets should be disabled but are enabled/missing: {missing_disabled}")

    skills = cfg.get("skills") or {}
    external = [str(x) for x in (skills.get("external_dirs") or [])]
    report.check(str(PROJECT_SKILLS) in external, "project-owned .hermes/skills is configured", f"project skill path missing from skills.external_dirs: {external}")
    report.check(not any(".kilo" in x or ".kilocode" in x for x in external), "no Kilo/Kilocode skill directory configured", f"Kilo/Kilocode skill path still configured: {external}")

    mcps = cfg.get("mcp_servers") or {}
    missing_mcps = sorted(EXPECTED_MCPS - set(mcps))
    report.check(not missing_mcps, "expected Warbird MCP servers configured", f"missing Warbird MCP servers: {missing_mcps}")
    extra_urls = [name for name, spec in mcps.items() if isinstance(spec, dict) and spec.get("url")]
    report.check(not extra_urls, "MCP servers are stdio/command based, no URL ghost servers", f"MCP servers with URL transports: {extra_urls}")
    bad_mcp_cmds = [name for name, spec in mcps.items() if isinstance(spec, dict) and spec.get("command") and not Path(str(spec.get("command"))).exists()]
    report.check(not bad_mcp_cmds, "MCP command paths exist", f"missing MCP command paths: {bad_mcp_cmds}")
    bad_sampling = [name for name, spec in mcps.items() if isinstance(spec, dict) and ((spec.get("sampling") or {}).get("enabled") is not False)]
    report.check(not bad_sampling, "MCP sampling disabled", f"MCP sampling not explicitly disabled: {bad_sampling}")

    plist = Path("/Users/zincdigital/Library/LaunchAgents/ai.hermes.gateway.plist")
    if plist.exists():
        with plist.open("rb") as fh:
            data = plistlib.load(fh)
        report.check(data.get("WorkingDirectory") == "/Users/zincdigital", "gateway launchd WorkingDirectory is local user home", f"gateway WorkingDirectory is {data.get('WorkingDirectory')!r}")
        report.check(str(data.get("StandardOutPath", "")).startswith(str(LOCAL_LOG_DIR)), "gateway stdout log path is local", f"gateway stdout path not local: {data.get('StandardOutPath')!r}")
        report.check(str(data.get("StandardErrorPath", "")).startswith(str(LOCAL_LOG_DIR)), "gateway stderr log path is local", f"gateway stderr path not local: {data.get('StandardErrorPath')!r}")
        env = data.get("EnvironmentVariables") or {}
        report.check(env.get("HERMES_HOME") == str(HERMES_HOME), "gateway preserves durable Warbird HERMES_HOME", f"gateway HERMES_HOME mismatch: {env.get('HERMES_HOME')!r}")
    else:
        report.check(False, "", f"gateway LaunchAgent plist missing: {plist}")

    code, launch = run(["launchctl", "print", f"gui/{os.getuid()}/ai.hermes.gateway"], timeout=20)
    report.check(code == 0 and "state = running" in launch, "gateway launchd service is running", "gateway launchd service is not running")

    code, crontab = run(["crontab", "-l"], timeout=20)
    report.check("warbird-hermes-gateway-ensure" not in crontab, "no overlapping crontab gateway watchdog is installed", "overlapping crontab gateway watchdog is installed", warning=True)
    report.check("com.warbird.hermes.cron-tick" not in launch, "legacy cron-tick LaunchAgent not loaded", "legacy cron-tick LaunchAgent appears loaded", warning=True)

    return report.emit()


if __name__ == "__main__":
    raise SystemExit(main())
