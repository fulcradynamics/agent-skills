# Deploy through Fulcra

Fulcra creates the app's Vercel project and issues short-lived project-scoped tokens. The owner does not need a separate hosting account. Use the same project on every redeploy, including a namespace already parked in their account.

## First deployment and every redeploy

Use Node24 and an authenticated `uvx fulcra-api` CLI. From the generated app root, copy [the standalone helper](../scripts/deploy-fulcra.mjs) to `scripts/deploy-fulcra.mjs` if the template does not include it. Add `.private/` to `.gitignore` **before running** it. Keep `.env` ignored; use the template's public Auth0 client configuration. Never copy another instance's `.env` or `.private` directory.

```sh
node scripts/deploy-fulcra.mjs your-name sveltekit your-name.my.fulcra.ai
# React template: use nextjs instead of sveltekit.
```

Supply the owner-authorized DNS label and exact expected domain. This updates the selected project's production alias; retain its current deployment ID for rollback when replacing an existing app. A new clone must supply its own name. The helper:

1. Lists the signed-in owner's projects with `GET /user/v1/deploy/project`. Reuses the exact named project, or creates it with `POST` and `{name, framework}`. It checks saved metadata against current ownership. It does not treat an owned parked namespace as a reason to rename.
2. Saves returned ID/domain to ignored `.private/fulcra-deployment.json` before further mutation. Record those identifiers (not credentials) in the workspace's `progress.md` Deployment section too.
3. Gets credentials with `POST /user/v1/deploy/project/{id}/token`. Keeps `token`, `platform_team_id` and `platform_project_id` in memory, exposing them to the CLI as `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.
4. Reads the project via Vercel `GET /v9/projects/{platform_project_id}?teamId={platform_team_id}`. Saves its current production deployment ID and selected settings for rollback before making changes, then sets and reads back framework, `buildCommand: "npm run build"`, `outputDirectory: null`, Node24, Fluid compute and automatic system environment exposure. A parked static project can have `framework: null`, an empty build command and output `"."`; deployment can otherwise succeed without building the app and produce a404. These defaults suit the official starters; adapt the helper explicitly for a custom build layout.
5. Runs `npx --yes --engine-strict=false vercel deploy --prod --yes` with scoped credentials. Only `PUBLIC_*` / `NEXT_PUBLIC_*` values go to `--build-env`; all `.env` values go to `--env` for runtime. Secrets must be read server-side at runtime. Do not use `DEPLOYMENT_ID` or `VERCEL_*` for application-owned variables; use an app prefix.

The helper sets Node24/Fluid/system env exposure as the tested baseline; generated Workflow functions need the platform deployment identity. Check the generated output as well as project settings. Svelte starters also carry this portable `vercel.json` so parked project defaults cannot silently select static output:

```json
{"$schema":"https://openapi.vercel.sh/vercel.json","framework":"sveltekit","buildCommand":"npm run build","outputDirectory":null}
```

A token/settings403 is an access/configuration blocker for that operation, not evidence that the owner needs another account. The helper stops on failed configuration/readback. Keep the project and rollback deployment; do not create a second project, reset instance identity or switch hosting silently. On a create409, list owned projects again to distinguish an owned namespace/race from a name belonging to someone else. Ask for another name only in the latter case. Invalid names422 require a valid owner-chosen name. Record exact failures and the prerequisite to unblock them.

## Persistence and scheduled work

Fulcra v1 data types and folders store application content. Apps that also need durable timers, serialized cursor/job state or encrypted background grants can use native Vercel Workflow through this same scoped hosting flow. Read [native-state-and-scheduling.md](native-state-and-scheduling.md) **before proposing a separate database or cron service**. A static/local SQLite, PGlite or JSON file in a Function is not durable production backing. A relational database remains an explicit alternative when its capabilities are actually required.

The generic deploy helper configures hosting; it does **not** implement app-specific job state, grant enrollment or bootstrap. The connector template includes those parts and automates its own first-deploy initialization. Preserve that script when cloning the connector app rather than replacing it with this generic helper.

## Evaluate the actual domain

Use `https://<domain>` returned by Fulcra, not the incidental `*.vercel.app` URL. Check live HTML/app routes, owner login, private API denial, real Fulcra write/readback, and populated harness events. For Workflow apps also prove a queued continuation after the initiating request closes, duplicate-start handling, retained state after redeploy, and unauthorized queue/start rejection. A build or deployment receipt alone does not complete a milestone.

Open sign-in in the owner's normal system browser as described in the skill. Preserve its public landing if requested and keep personal controls behind verified owner authentication. CLI/session access used for evaluation is not permission to save the assistant's token as the app's unattended grant.

## Rollback

The helper retains `previousProductionDeploymentId` and `beforeDeploySettings` in private metadata before replacing production. It also preserves the first `baselineProductionDeploymentId`/`baselineProjectSettings` across a two-deploy bootstrap. Choose the appropriate known-good checkpoint; do not assume the immediately preceding bootstrap build is the original landing. With a fresh scoped token/team/project in the environment (the same token endpoint above), run `npx --yes --engine-strict=false vercel rollback <previousProductionDeploymentId> --yes`. Verify the Fulcra domain afterward. If rollback access fails, preserve that exact deployment ID and report the failed operation; do not erase or rebuild the prior source/state. Workflow state is independent of the alias: coordinate recovery or compatible code before rolling back an initialized controller.

## Other hosting

Use another hosting account only when the user chooses it or a recorded platform blocker makes it necessary and they approve the change. A hosted clone should inherit a supported deployment path, not a request to provision infrastructure already included by Fulcra.
