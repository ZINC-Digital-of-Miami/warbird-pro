# Supabase / Cloud Work

Cloud Supabase is runtime/support ONLY. It is NOT a training database.

## Allowed cloud roles

- Frontend/dashboard runtime
- Auth and admin runtime
- Live chart data already used by the app
- Pine alert/webhook support (if explicitly approved)
- Operational health logging

## Explicitly prohibited in cloud

- Raw TradingView exports
- Raw Databento training rows
- Raw Strategy Tester trade lists
- Raw tuning/training trial tables
- Raw AutoGluon/SHAP artifacts
- Full research datasets
- Training labels
- Legacy `ag_training` tables
- FRED/macro/cross-asset warehouses

## Before adding any cloud object

Answer these three questions:
1. Does it serve live runtime/support rather than training?
2. Can the indicator-only modeling program run without it?
3. Does it avoid storing raw trials, labels, or research artifacts?

If any answer is no, the object does not belong in cloud.

## Technical rules

- No Prisma, Drizzle, or ORM
- Cloud DDL belongs in `supabase/migrations/`
- If touching `supabase/`, `app/api/cron/`, or ingestion libraries: run `npm run build` and path-specific validation
