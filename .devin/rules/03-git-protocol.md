# Git Protocol

- ALL commits land directly on `main`. No feature branches.
- If Devin auto-creates a branch: merge to main, push main, close PR, delete branch before ending session.
- Push only with explicit Kirk approval. Use `git push origin main` explicitly.
- Run `./scripts/guards/warbird-agent-precheck.sh --mode manual` before commit/push.
- If rollback needed, create a revert commit — never force push.
- **NEVER** use `--no-verify`. This flag is itself a violation.
- **NEVER** use `git push --force` or `git push -f`.
- Before touching any file in `docs/plans/` or `docs/handoffs/`, diff against `origin/main` first. If the file already exists and is newer/larger on `main`, do not overwrite.

## Pre-Commit Enforcement

The pre-commit hook (`warbird-agent-precheck.sh`) now runs two enforcement engines before quality-lane checks:

1. **Knowledge Enforcement Engine** (`warbird-knowledge-enforcement.sh`): Blocks commits that violate Knowledge notes — legacy training, fake data, force push, retired surfaces, unauthorized automation.
2. **File Protection Engine** (`warbird-file-protection.sh`): Blocks deletions of protected paths, .gitignore additions for governance dirs, plan file overwrites with shorter content, retired surface modifications.

Both produce `exit 1` on violation. They cannot be bypassed.
