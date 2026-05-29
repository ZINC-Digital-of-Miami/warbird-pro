# Session Insights Retrospective

Use this rule after any meaningful Devin session, especially chart parity, PR review, environment setup, Supabase/DuckDB audit, Sonic remediation, or Vercel demotion planning.

Official basis: Devin Session Insights reports overview metrics, task category, issue timeline, actionable feedback, and Knowledge Usage. Warbird uses those outputs as a required improvement loop, not as passive analytics.

## Required Evaluation

For each completed Devin session, record:

- Session URL
- Task category shown by Session Insights
- Intended Warbird category
- ACU usage, user message count, and session size
- Whether size is L/XL and therefore too broad for one run
- Issue Timeline high/medium impact issues
- Actionable Feedback items
- Useful Knowledge items
- Misleading Knowledge items
- Repeated issue types
- Final action: prompt update, playbook update, Knowledge update, environment/blueprint update, repo fix, or no action

## Warbird Category Map

Use this map to catch wrong-category sessions:

- Devin control-plane setup: `CI/CD & DevOps` or `Code Review & Analysis`
- Packet/PR authority review: `Code Review & Analysis`
- Dashboard/runtime implementation: `Feature Development`
- Lint/build/Sonic remediation: `Code Quality & Security` or `Bug Fixing`
- Supabase-to-DuckDB audit: `Migrations & Upgrades` or `Data & Automation`
- Vercel demotion planning: `CI/CD & DevOps` or `Migrations & Upgrades`
- Knowledge/playbook cleanup: `Code Review & Analysis` or `Data & Automation`

If Session Insights classifies a run outside the expected map, treat it as a prompt-scope mismatch. Use the improved prompt as input for the next playbook or launch packet.

## Actionable Feedback Routing

- Prompt improvement -> update the next launch packet or relevant `.devin/playbooks/*.devin.md`.
- Machine setup -> update `.devin/environment-blueprint.yaml` or Devin Environment UI.
- Repo config -> create a scoped repo change, then verify it locally.
- Knowledge change -> update `.devin/knowledge-blueprint.md` and submit/approve the matching Devin Knowledge note.
- Broad architecture recommendation -> stop for Kirk approval before changing scope.

## Misleading Knowledge Policy

Misleading Knowledge is a blocking maintenance item. Do not keep using a Knowledge item that Session Insights flags as misleading.

For each misleading item:

1. Identify why it misled Devin: stale content, broad trigger, conflict, wrong repo scope, or missing stop condition.
2. Decide: edit trigger, edit content, narrow repo pinning, disable/delete, or replace with a new focused note.
3. Update `.devin/knowledge-blueprint.md` if the canonical Warbird Knowledge set changes.
4. Record the change in the session closeout.

## Repeated Issues Policy

If the Issue Timeline shows the same issue type more than once, do not only retry.

Route repeated issues as follows:

- Build/test retry loop -> fix repo script/config or split the task.
- Missing dependency/tool/version -> update environment blueprint.
- Permission/secret/access issue -> stop and request approved access path.
- Wrong approach or scope drift -> update playbook, Knowledge, or launch prompt.
- Same lint/type error after attempted fix -> narrow implementation and run the smallest failing command.

## Session 13c8 Standing Lesson

Session `13c8afb422cb4c3ea4cb582d90ab00e2` is the baseline failure pattern for this lane. It produced useful artifacts, but only after repeated correction. Watch for the same failures:

- exact instructions rewritten as interpretations
- false completion claims before evidence
- Knowledge updates delayed until another agent is already misaligned
- chart layout drift despite diagrams
- charting product/licensing confusion
- "no remaining drift" claims without disproof checks

If any of these recur, stop the run, update the prompt/playbook/Knowledge, and resume as a smaller session.

## Closeout Requirement

Every Devin closeout for a meaningful session must include a `Session Insights Review` section with:

```text
Session Insights generated: yes/no
Category shown:
Intended category:
Category aligned: yes/no
Size:
Actionable feedback applied:
Misleading Knowledge found:
Repeated issues found:
Rules/playbooks/Knowledge/blueprint changes made:
Remaining follow-up:
```
