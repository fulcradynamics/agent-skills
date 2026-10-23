# Native state and background scheduling

Read when a Fulcra-hosted app needs cursors, serialized jobs, durable timers or unattended sync. Fulcra v1 data types and folders remain the content store. Managed Workflow persistence/queues can supply the app's operational state through the existing scoped Vercel deployment. This path was exercised on two independent Fulcra projects under one owner; different-owner clone acceptance is a separate check.

## Integrate with the starter

The tested SvelteKit integration used `workflow@5.2.3` (commit the dependency lock). Add `workflowPlugin()` from `workflow/sveltekit` alongside `sveltekit()` in `vite.config.js`. See the [official SvelteKit integration](https://workflow-sdk.dev/docs/getting-started/sveltekit) for the current API. For Next.js use its corresponding official integration; do not assume the Vite plugin applies there.

Keep orchestration in exported functions marked `"use workflow"`; put network/Node operations in stable `"use step"` functions. Start via `start` from `workflow/api` in an owner-authorized server handler. Durable `sleep` from `workflow` resumes through the managed queue after the initial HTTP request closes; it is not an in-process timer or cron. Never ship the unauthenticated demonstration start route as a personal production endpoint.

Use the [deploy helper](deploy.md) to check Node24, Fluid and automatic system environment exposure. Do not set a fake `VERCEL_DEPLOYMENT_ID`. For the tested SDK, inspect `.vercel/output/functions/.well-known/workflow/v1/flow.func/.vc-config.json`: the managed queue trigger should be present. Permit only the required generated handler through app hooks. Do not exempt every `/.well-known/*` route.

The [Vercel World](https://workflow-sdk.dev/worlds/vercel) manages the backing storage/queues. A403 from storage-store or Neon Marketplace provisioning does not block Workflow or justify requesting a database URL. Do not promise arbitrary SQL transactions from Fulcra file/record APIs or treat Workflow as a general relational database. Bound the state and retention requirements; choose another backend only if the app needs capabilities this pattern cannot supply.

## A repeatable operational contract

For a personal sync app, serialize state transitions in one durable controller per owner/instance. Give each request a stable command ID and cache its final result: queue acceptance is not successful application. Use an atomic singleton mechanism (the tested version used hook-token conflict resolution), rather than read-then-write initialization. Serialize provider selection, pause/disconnect and cursor changes through that controller. Keep content in Fulcra; encrypt grants and staged source content with a fresh server-only per-instance key.

Persist bounded phases separately: source read, pending output, delivery intent, destination allocation/submission, verification, then cursor checkpoint. A single retried step around the whole poll cycle hides partial external side effects. Verify destination content before advancing its cursor; reconcile ambiguous uploads using stable identities. Rotating credential refresh needs a persisted intent and a bounded one-attempt exchange: uncertain success must require reauthorization rather than blindly retry a consumed refresh token.

A durable timer does not grant service access. Browser sign-in and the app's offline Fulcra grant are separate enrollments. Obtain app-owned provider credentials in its protected UI, select limited sources, preview, and enable explicitly. Existing agent MCP/CLI credentials are not reusable unattended app grants.

## First initialization, redeploy and recovery

Make this part of the clone's deployment command, not an undocumented manual task:

1. Generate fresh owner/instance identity, encryption key and bootstrap secret in ignored private configuration. Keep public-template mode an explicit choice; personal deployments get minimal login and verified-owner controls.
2. Deploy once with a narrowly scoped first-deploy initializer enabled. Require verified owner identity, same-origin mutation checks and a separate bootstrap secret. Ordinary setup/readiness must never silently create empty state.
3. Start the singleton, persist an owner/instance-bound marker in Fulcra files, and read it back. Atomically save the controller root run ID and recovery metadata locally **before** continuing. Initialization is not complete on a start receipt alone.
4. Deploy again with the root pinned and first-time bootstrap disabled. Subsequent deployments reuse it. On interruption, recover from the retained marker/config; never clear the root, regenerate identity or drop unresolved intents to make setup appear ready.
5. Plan bounded controller epochs with exact-state handoff to the latest deployment. Retry command IDs through the handoff gap; do not duplicate mutations or leave an old deployment running indefinitely. Preserve pending inbox iteration when racing timers.

The controller's operational lifetime and the platform's retained history are different. State a bounded retention/size budget and a restoration procedure. Preserve the instance key, marker, root and retained encrypted snapshot together. A missing or failed initialized controller must fail closed until recovery, not bootstrap a blank replacement. See [platform retention](https://vercel.com/docs/workflows/retention) when choosing recovery guarantees.

## Security and acceptance

The tested Vercel edge rejected ordinary/spoofed CloudEvent POSTs to the public queue path. The SDK callback alone did not verify a forged signature; direct self-hosting needs equivalent queue authentication/isolation. Recheck this on the target host. Never expose a queue/start route merely to make a timer test pass.

Before claiming native backing works, evaluate the real owner/domain: command result after202, timer after request closure, duplicate start/command exactly once, pause fencing, independent instance identities, retained root through redeploy, failed-state recovery, private API denial and forged queue rejection. Report credential refresh and each live provider journey separately.

## Full connector reference

The [Fulcra Connectors guide](https://connectors.my.fulcra.ai/guides/hosting-and-storage.md) explains the packaged deployment. [Setup](https://connectors.my.fulcra.ai/guides/setup.md) is the user/agent procedure, and the source is [ashfulcra/connectors-webapp](https://github.com/ashfulcra/connectors-webapp/tree/feat/connector-template) (private preview; repository access required). The public guides are readable without repository access; do not imply its source is publicly clonable before release.

Reusable source locations in that app: `scripts/init-env.mjs`, `scripts/deploy.mjs`, `workflows/native-controller.js`, `workflows/native-steps.js`, `src/lib/server/native/`, and `src/lib/client/connector-api.js`. These implement encrypted state, singleton/commands, durable work phases, result polling, two-deploy bootstrap and recovery markers. Do not copy any owner's `.env`, `.private`, controller IDs, keys or enrolled grants. The generic starter does not contain this entire connector-specific state engine; add the capabilities the new app actually needs and evaluate them through its harness.
