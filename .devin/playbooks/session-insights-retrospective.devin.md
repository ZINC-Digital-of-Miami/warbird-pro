# Session Insights Retrospective Workflow

Suggested macro in Devin: `!warbird-session-insights`

Use this playbook after each meaningful Devin session before treating the next run as improved.

## Procedure

1. Open the completed Devin session.
2. Generate or regenerate Session Insights.
3. Record ACU usage, user message count, session size, and category.
4. Compare the shown category to the intended Warbird category from `.devin/rules/10-session-insights.md`.
5. Review Issue Timeline for high/medium impact issues and repeated issue labels.
6. Review Actionable Feedback and classify each item as prompt, machine setup, repo config, Knowledge, playbook, or out-of-scope.
7. Review Knowledge Usage and list useful and misleading Knowledge items.
8. For every misleading Knowledge item, decide whether to edit trigger, edit content, narrow repo pinning, disable/delete, or replace it.
9. For repeated issues, update the relevant `.devin/rules/`, `.devin/playbooks/`, `.devin/knowledge-blueprint.md`, or `.devin/environment-blueprint.yaml`.
10. Return a closeout section named `Session Insights Review`.

## Specifications

- Every L/XL session is treated as too broad until proven otherwise; split future work into smaller bounded runs.
- Wrong task category means the launch prompt or playbook needs clarification before the next similar run.
- Misleading Knowledge must be fixed, narrowed, disabled, or explicitly escalated.
- Repeated issues must create a durable process or environment change unless the issue is a one-off external outage.
- Actionable Feedback is advisory; repo changes still need local verification.

## Advice

- Use improved prompts as source material for launch packets and `.devin.md` playbooks.
- Keep Knowledge notes short and trigger-specific when fixing misleading retrieval.
- Prefer machine setup fixes for recurring dependency/tool/version problems.
- Do not add permanent Knowledge for one-off implementation bugs.

## Forbidden Actions

- Do not ignore misleading Knowledge.
- Do not call a repeated issue "resolved" without a durable change or explicit escalation.
- Do not enable write automations from Session Insights alone.
- Do not treat Session Insights as QA proof of code correctness.

## Required From User

- Approval before deleting broad team Knowledge, changing repo-wide automation policy, installing connectors, or enabling any write automation.
