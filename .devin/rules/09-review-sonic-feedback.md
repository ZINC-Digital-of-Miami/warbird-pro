# Reviews, Sonic, And Feedback Learning

Use this rule whenever a task mentions Devin Review, Session Insights, GitHub Review, Sonic, SonarQube, SonarCloud, quality gate, autofix, or review comments.

## Source Priority

- Repo-local gates and `AGENTS.md` remain authoritative.
- SonarQube/Sonic is the primary linter, review, audit, and reporting surface for quality remediation.
- SonarQube/Sonic findings drive the defect map, but fixes remain advisory until mapped to a repo file, rule, severity, root cause, and verification step.
- Devin Review is useful feedback, not proof of completion.
- Session Insights is useful feedback about prompt, Knowledge, environment, and category fit; it is not proof of code correctness.
- Codex QA can independently block Devin work even when Devin Review and Sonar pass.

## Sonic Workflow

When SonarQube/Sonic reports issues:

1. Return a defect map first: path, issue class, severity, owning surface, likely root cause, and disproof/verification step.
2. Do not apply suggested fixes automatically unless Kirk approved that exact remediation scope.
3. Run the relevant local verification after any approved fix.
4. If a finding is false positive or deferred, record why and where the decision lives.

## Self-Heal Loop

After every review, Session Insights report, or failed gate:

1. Identify whether the failure is a one-off implementation mistake or reusable process knowledge.
2. If reusable, update the relevant `.devin/rules/` or `.devin/playbooks/` file in the same change.
3. If platform Knowledge is needed, include a concise proposed Knowledge note in the closeout for Kirk to approve in Devin.
4. Do not claim the platform has learned unless the rule, playbook, Knowledge note, or automation change is actually present or submitted.

## Session Insights Routing

- Wrong category -> update launch prompt or playbook scope.
- Actionable Feedback -> classify as prompt, machine setup, repo config, Knowledge, playbook, or out-of-scope.
- Misleading Knowledge -> edit/narrow/disable/delete the Knowledge item before the next similar run.
- Repeated timeline issue -> update environment blueprint, playbook, Knowledge, or split the task.
- L/XL size -> split the next run into smaller phases.

## No Auto-Mutation Defaults

- No auto-merge.
- No auto-push.
- No auto-fix from Sonic without approved scope.
- No scheduled automation that writes code until the playbook has passed at least one manual run.
