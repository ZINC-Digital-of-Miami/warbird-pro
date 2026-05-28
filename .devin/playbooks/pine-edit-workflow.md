# Pine Edit Workflow

Step-by-step for any Pine indicator edit.

1. **Confirm approval** — Do not proceed without explicit approval for the specific Pine edit in the current session
2. **Check state** — Run `git status --short` to understand current working tree
3. **Read governing docs** — Read the governing docs for the touched Pine surface (see `06-reference-docs.md`)
4. **Check output budget** — Only 10 output slots remain on V9 before the 64-call hard cap. Price any new plot or alertcondition before editing.
5. **Make the minimal edit** — Touch the smallest viable write-set. Do not refactor unrelated areas.
6. **Run ALL 6 Pine verification gates:**
   1. pine-facade compile check
   2. `./scripts/guards/pine-lint.sh <file>`
   3. `./scripts/guards/check-fib-scanner-guardrails.sh`
   4. `./scripts/guards/check-contamination.sh`
   5. `./scripts/guards/check-no-tv-force.sh`
   6. `npm run build`
7. **Run precheck** — `./scripts/guards/warbird-agent-precheck.sh --mode manual`
8. **Report results** — Do NOT claim complete if any gate failed
