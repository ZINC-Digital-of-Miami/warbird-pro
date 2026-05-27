---
description: Warbird-safe Codacy Guardrails behavior for AI agents
applyTo: "**"
---

# Codacy Guardrails

Codacy is a review and investigation surface for this repository. It may flag
issues, summarize risk, and provide evidence. It is not approval to edit.

## Repository Identity

When Codacy tools ask for repository metadata, use:

- `provider`: `gh`
- `organization`: `zincdigitalofmiami`
- `repository`: `warbird-pro`

## Required Behavior

- Run Codacy analysis after editing files when Codacy MCP tools are available.
- If Codacy MCP is unavailable but the local Codacy CLI works, say that clearly
  and use the CLI for read-only analysis.
- If Codacy reports issues, return a defect map first: path, issue class,
  severity, owning surface, likely root cause, and verification step.
- Apply fixes only after Kirk explicitly approves the exact remediation scope.
- Do not use Codacy suggested fixes as an automatic write path.
- Do not run Codacy complexity or coverage checks unless the task explicitly
  asks for them.

## Dependency And Security Checks

After adding or changing dependencies, run a Trivy/Codacy security analysis
before claiming completion. If vulnerabilities are found, stop and report the
issue before continuing with unrelated work.

## MCP Troubleshooting

If Codacy MCP tools are missing:

- Check that the Codacy VS Code extension is installed and authenticated.
- Run `Codacy: Configure Codacy MCP Server` from the VS Code command palette.
- Check VS Code Copilot MCP settings if Copilot is expected to consume MCP
  tools.
- Do not invent MCP wiring or claim MCP is connected from generated files alone.
