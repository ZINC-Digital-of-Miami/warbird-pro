# Review, Sonic, And Self-Heal Workflow

Suggested macro in Devin: `!warbird-review-self-heal`

Use this playbook when Devin Review, Sonic/SonarQube, GitHub review comments, lint, build, or Codex QA produces feedback.

## Procedure

1. Collect the feedback source: Devin Review URL, Sonic/SonarQube issue, GitHub comment, command failure, or Codex QA finding.
2. Build a defect map before fixing: path, issue class, severity, owning surface, likely root cause, and verification step.
3. Separate advisory findings from blocking repo gates.
4. Ask for approval before applying broad Sonic suggested fixes or changing architecture.
5. Implement only the approved, bounded remediation.
6. Run the narrow verification command that disproves the defect.
7. If the failure is reusable process knowledge, update the relevant `.devin/rules/` or `.devin/playbooks/` file in the same change.
8. If platform Knowledge should change, propose the exact Knowledge note in the closeout for Kirk to approve.
9. Return before/after evidence and whether the gate is passed, blocked, or passed with registered ambiguity.

## Specifications

- Every actionable finding has a path, severity, root cause, and verification step.
- Broad review/Sonic suggestions are not applied without approved scope.
- Repeated review feedback becomes a `.devin/rules/`, `.devin/playbooks/`, or Knowledge update.
- Codex QA remains allowed to block even if Sonic and Devin Review are green.

## Advice

- First decide whether a finding is a code bug, process gap, stale documentation, or false positive.
- Fix one root cause at a time and rerun the narrowest proof command.
- Keep process updates short; one-off bugs do not need new permanent Knowledge.

## Forbidden Actions

- Do not auto-apply Sonic fixes.
- Do not treat Devin Review green as proof of completion.
- Do not hide failed local checks behind remote green checks.
- Do not say Devin "learned" unless a rule, playbook, Knowledge proposal, or automation update exists.

## Required From User

- Approval before broad automated fixes, architecture changes, pushing, or dismissing a blocking gate as accepted risk.
