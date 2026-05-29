# Vercel Demotion After Local Proof

Suggested macro in Devin: `!warbird-vercel-demotion`

Use this playbook only after the local dashboard/runtime replacement has passed implementation and QA gates.

## Procedure

1. Confirm Kirk explicitly approved Vercel demotion in the current session.
2. Read `AGENTS.md`, `.devin/rules/08-chart-parity-authority.md`, and the latest local dashboard closeout packet.
3. Produce a dependency map for Vercel/Next.js routes, components, API routes, environment variables, webhooks, and DNS/routing.
4. Prove the local replacement covers the required runtime functions.
5. Produce a rollback plan before deleting or disabling anything.
6. Run `npm run lint`, `npm run build`, and any route/runtime checks required by the touched files.
7. Return a demotion packet with deleted/retained surfaces, verification evidence, rollback steps, and remaining external actions.

## Specifications

- Vercel demotion is a later phase, not part of chart packet implementation.
- Demotion must be reversible until Kirk accepts the local runtime as replacement.
- DNS/routing implications are documented before any change.
- Every removed runtime surface has replacement proof or is explicitly approved for removal.

## Advice

- Treat Vercel as still live until the demotion proof packet is accepted.
- Preserve rollback paths before deleting code, config, or project settings.
- Separate repo removal, Vercel project settings, and DNS/routing into separate approval gates.

## Forbidden Actions

- Do not disable Vercel before local replacement proof exists.
- Do not delete active routes/components without replacement coverage.
- Do not change DNS/routing without explicit current-session approval.
- Do not push without approval.

## Required From User

- Explicit current-session approval to start demotion, modify DNS/routing, disable/delete project settings, or push removal commits.
