# Deploy

Apps are deployed to a Fulcra domain through Fulcra's deploy projects: Fulcra
creates a Vercel project for the app and issues short-lived access tokens scoped
to it. The user doesn't need a Vercel account. Referenced from steps 8 and 9 of
[`../SKILL.md`](../SKILL.md); use the same [deploy command](#deploy) for every
later redeploy.

## Create the deploy project (once per app)

Before the first deploy, check `progress.md` for a saved **Deployment** section.
If it has a deploy project, reuse it; never create a second one for the same app.

Otherwise, create one. `name` becomes the app's address, `<name>.<Fulcra domain>`,
so use the project name as a lowercase DNS label (letters, digits, and inner
hyphens). `framework` is `sveltekit` for Svelte or `nextjs` for React.

```bash
curl -sS -X POST https://api.fulcradynamics.com/user/v1/deploy/project \
  -H "Authorization: Bearer $(uvx fulcra-api auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"name": "<name>", "framework": "<sveltekit|nextjs>"}' \
  -w '\n%{http_code}\n'
```

- `200`: save the response's `id` and `domain` to the **Deployment** section of
  `progress.md`. The app's URL is `https://<domain>`.
- `409`: the name is taken, possibly by another user. Ask the user for another name.
- `422`: the name is invalid or too long; the response says why. Fix it, confirming
  the new name with the user.
- Anything else, such as a `404` or a connection failure, means deploy projects
  are unavailable. Use [your own Vercel account](#fallback-your-own-vercel-account)
  instead, and record that choice in the **Deployment** section.

## Deploy

Run from the app's root directory. Each deploy gets a fresh token, valid for a day.
The subshell keeps the token out of your shell: never print it, or write it to a
file or the workspace. If getting the token fails, the subshell stops before
deploying.

The app's `.env` variables are passed both at build time (`--build-env`, which
React's `NEXT_PUBLIC_*` variables need) and at runtime (`--env`, which Svelte's
`$env/dynamic` variables need), since Vercel doesn't set them from `.env`.
`--engine-strict=false` lets `npx` install the Vercel CLI when the template's
`.npmrc` sets `engine-strict=true` and the local Node version is newer than one
of the CLI's dependencies supports.

```bash
(
  set -e
  DEPLOY_PROJECT_ID=<id from progress.md>
  DEPLOY_TOKEN=$(curl -sSf -X POST \
    "https://api.fulcradynamics.com/user/v1/deploy/project/$DEPLOY_PROJECT_ID/token" \
    -H "Authorization: Bearer $(uvx fulcra-api auth print-access-token)")
  export VERCEL_TOKEN=$(jq -r .token <<< "$DEPLOY_TOKEN")
  export VERCEL_ORG_ID=$(jq -r .platform_team_id <<< "$DEPLOY_TOKEN")
  export VERCEL_PROJECT_ID=$(jq -r .platform_project_id <<< "$DEPLOY_TOKEN")
  ENV_FLAGS=()
  while IFS='=' read -r key value; do
    value=${value%\"}; value=${value#\"}
    ENV_FLAGS+=(--build-env "$key=$value" --env "$key=$value")
  done < <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env)
  npx --engine-strict=false vercel deploy --prod --yes "${ENV_FLAGS[@]}"
)
```

The app is served at `https://<domain>` from `progress.md`, not at the
`*.vercel.app` URL the CLI prints. Evaluate the deployed app at `https://<domain>`.

## Fallback: your own Vercel account

Only use this when deploy projects are unavailable. Run `vercel whoami`. If the CLI
isn't logged in, ask the user to create a Vercel account (or log in) and run
`vercel login`; anonymous deployments expire after an hour and disrupt the harness
iteration cycle. Then deploy with the same environment variable flags as above,
without the `VERCEL_*` exports, and use the production URL the CLI prints.
