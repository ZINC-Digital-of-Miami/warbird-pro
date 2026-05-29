# Git Protocol

- ALL commits land directly on `main`. No feature branches.
- If Devin auto-creates a branch: merge to main, push main, close PR, delete branch before ending session.
- Push only with explicit Kirk approval. Use `git push origin main` explicitly.
- Run `./scripts/guards/warbird-agent-precheck.sh --mode manual` before commit/push.
- If rollback needed, create a revert commit — never force push.
- NEVER delete tracked files or add existing tracked files to `.gitignore` without explicit Kirk approval.
