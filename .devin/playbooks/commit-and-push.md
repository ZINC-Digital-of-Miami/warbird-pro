# Commit and Push Workflow

Step-by-step for committing and pushing work.

## Pre-Flight (BEFORE any file edits)

0. **Diff against main first** — For ANY file in `docs/plans/`, `docs/handoffs/`, or governance files, run `git show origin/main:<path> | wc -l` to check if a newer version exists. Do NOT blindly restore from git history.

## Commit Sequence

1. **Run precheck** — `./scripts/guards/warbird-agent-precheck.sh --mode manual`. This runs the Knowledge Enforcement Engine and File Protection Engine first. If they fail, STOP — do not work around the failure.
2. **Run lint and build** — `npm run lint` and `npm run build`
3. **Verify branch** — `git branch --show-current` must return `main`
4. **Verify upstream** — `git rev-parse --abbrev-ref --symbolic-full-name @{u}` must resolve to `origin/main`
5. **Stage and commit** — Use a descriptive conventional commit message. NEVER use `--no-verify`.
6. **Ask for approval** — Request explicit user approval before pushing
7. **Push** — Only after approval: `git push origin main`
8. **If claiming PR is mergeable** — Also run `./scripts/guards/check-github-merge-readiness.sh`

## If Kirk Says STOP

- Kill all background shells immediately
- Do NOT push, commit, or "fix" anything
- Respond only after all processes are dead
- Wait for new instructions
