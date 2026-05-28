# Git Protocol

- ALL commits land directly on `main`. No feature branches. Ever.
- If Devin auto-creates a branch, merge to main, push main, close PR, delete branch before ending session
- Push only with explicit user approval
- Use `git push origin main` explicitly (never bare `git push`)
- Before push, verify:
  - `git branch --show-current` returns `main`
  - `git rev-parse --abbrev-ref --symbolic-full-name @{u}` resolves to `origin/main`
- Never use `git push --force`, `git push -f`, or `git push --no-verify`
- Run `./scripts/guards/warbird-agent-precheck.sh --mode manual` before commit/push
- If rollback needed, create a revert commit — never force push
