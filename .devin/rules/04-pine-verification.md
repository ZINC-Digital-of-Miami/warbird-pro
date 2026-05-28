# Pine Verification

If ANY `.pine` file is touched, ALL of these must pass:

1. pine-facade compile check
2. `./scripts/guards/pine-lint.sh <file>`
3. `./scripts/guards/check-fib-scanner-guardrails.sh`
4. `./scripts/guards/check-contamination.sh`
5. `./scripts/guards/check-no-tv-force.sh`
6. `npm run build`

Do NOT run indicator/strategy parity unless explicitly approved. No active strategy Pine file exists.

Before ANY TradingView CDP/MCP operation, run:

```bash
python3 scripts/ag/tv_connection_doctor.py --json
```

Only proceed if `ready: true`.
