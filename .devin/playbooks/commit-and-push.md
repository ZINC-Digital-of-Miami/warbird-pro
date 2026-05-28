# Commit and Push Workflow

Step-by-step for committing and pushing work.

1. **Run precheck** — `./scripts/guards/warbird-agent-precheck.sh --mode manual`
2. **Run lint and build** — `npm run lint` and `npm run build`
3. **Verify branch** — `git branch --show-current` must return `main`
4. **Verify upstream** — `git rev-parse --abbrev-ref --symbolic-full-name @{u}` must resolve to `origin/main`
5. **Stage and commit** — Use a descriptive conventional commit message
6. **Ask for approval** — Request explicit user approval before pushing
7. **Push** — Only after approval: `git push origin main`
8. **If claiming PR is mergeable** — Also run `./scripts/guards/check-github-merge-readiness.sh`
