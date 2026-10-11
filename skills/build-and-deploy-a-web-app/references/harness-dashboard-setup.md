# Harness Dashboard Setup

M1 implementation and evaluation checklist for the owner-only dashboard.
Execute inside the first harness run, not before starting the harness.
Referenced from step 9 of [`../SKILL.md`](../SKILL.md). See
[`harness-control-flow.md`](harness-control-flow.md) for the run flow and how
events are recorded, and [`workspace.md`](workspace.md) for the workspace files.

## Reuse the harness data type

Read the full `MomentAnnotation/<UUID>` ID from `progress.md`, created by the
Nurse in step 5. Confirm it already contains M1's `RUN_START`, `FIND_MILESTONE`,
and `GENERATE` started records. If absent, return to
[harness setup](harness-control-flow.md#setup) before implementing the dashboard;
do not fabricate retrospective records or create a second empty data type.
Use the same ID as `PUBLIC_HARNESS_ANNOTATION_ID` below.

## Add environment variables to `.env`

Obtain the owner's Fulcra User ID by running `uvx fulcra-api user-info` in the CLI and extracting the `"userid"` field from the JSON response. Do not attempt to use `curl` or decode session tokens to find this ID.

```
# Server-only — NO PUBLIC_/NEXT_PUBLIC_ prefix. This must never reach the
# browser; the backend compares it against the authenticated user's Fulcra id.
OWNER_USER_ID=<your-fulcra-user-id>

# Client-readable (Svelte PUBLIC_*, React NEXT_PUBLIC_*).
PUBLIC_HARNESS_ANNOTATION_ID=<annotation-id-from-above>
PUBLIC_WORKSPACE_PATH=workspace/<project-name>
```

(For React, use the `NEXT_PUBLIC_*` prefix for the two client-readable vars;
keep `OWNER_USER_ID` server-only with no prefix.)

## Create server endpoints

The dashboard must fetch data through backend API endpoints (not directly from
Fulcra API) to avoid CORS issues. The Fulcra API must be called only from the
backend — never from the browser. Ownership is also enforced on the backend: the
owner's id (`OWNER_USER_ID`) stays server-only, and each route reads the caller's
id from the `fulcradynamics.com/userid` claim already carried in their Fulcra
access token (the JWT in the session cookie) and compares them — no extra network
call, so the identity provider is only hit once, at login. See
[`svelte/harness-api-server.js`](svelte/harness-api-server.js) and
[`svelte/harness-owner.js`](svelte/harness-owner.js) for the complete
implementation, which uses endpoints documented at
https://docs.fulcradynamics.com/rest-api/.

The `issues` and `overview` routes read markdown files from the workspace.
Fulcra's file API is two-step: list the folder
(`GET /input/v1/file?path=/<workspace-path>`, absolute path with a leading
slash) to resolve a file's input id, then download by id
(`GET /input/v1/file/{input_id}/download`, which returns raw text). The reference
`fetchWorkspaceFileText()` helper does both.

- For Svelte: Create:
  - `src/lib/server/harness-owner.js` (copy [`svelte/harness-owner.js`](svelte/harness-owner.js) — the shared `isOwner()` check)
  - `src/routes/api/harness/runs/+server.js` (export the GET_runs function as GET — 403s non-owners)
  - `src/routes/api/harness/issues/+server.js` (export the GET_issues function as GET — 403s non-owners; serves `outstanding-issues.md`)
  - `src/routes/api/harness/overview/+server.js` (export the GET_overview function as GET — 403s non-owners; serves the nurse-authored `overview.md`)
  - `src/routes/api/harness/owner/+server.js` (export the GET_owner function as GET — returns `{ isOwner }` so the dashboard/nav can gate visibility without seeing the id)
- For React (Next.js app router): the same four routes live in their own
  `route.ts` files. See [`react/harness-api-server.ts`](react/harness-api-server.ts)
  for all four handlers (named `GET_*` there only so they fit one file — rename
  each to `GET` in its own route file) and
  [`react/harness-owner.ts`](react/harness-owner.ts) for the shared `isOwner()`
  check. Create:
  - `lib/server/harness-owner.ts` (copy [`react/harness-owner.ts`](react/harness-owner.ts))
  - `app/api/harness/runs/route.ts` (export the GET_runs body as GET — 403s non-owners)
  - `app/api/harness/issues/route.ts` (export the GET_issues body as GET — 403s non-owners; serves `outstanding-issues.md`)
  - `app/api/harness/overview/route.ts` (export the GET_overview body as GET — 403s non-owners; serves the nurse-authored `overview.md`)
  - `app/api/harness/owner/route.ts` (export the GET_owner body as GET — returns `{ isOwner }` so the dashboard/nav can gate visibility without seeing the id)

  Copy the shared `fetchWorkspaceFileText()` helper into a small module (e.g.
  `lib/server/harness-files.ts`) or inline it in each route. Client-readable env
  vars use the `NEXT_PUBLIC_*` prefix; `OWNER_USER_ID` stays server-only.

## Integrate dashboard components

- For Svelte:
  - Install the markdown renderer used for the overview and issues panels: `npm install marked dompurify`. The dashboard runs `marked` to turn the nurse-authored markdown into HTML and `DOMPurify` to sanitize it before injecting with `{@html}`.
  - Copy [`svelte/HarnessDashboard.svelte`](svelte/HarnessDashboard.svelte) to `src/lib/components/HarnessDashboard.svelte`
  - Copy [`svelte/OwnerNav.svelte`](svelte/OwnerNav.svelte) to `src/lib/components/OwnerNav.svelte`
  - Create `src/routes/harness/+page.svelte` (see [`svelte/harness-page.svelte`](svelte/harness-page.svelte))
  - Add `<OwnerNav />` to `src/routes/+layout.svelte` before the main content

- For React:
  - Install the markdown renderer used for the overview and issues panels: `npm install marked dompurify`. The dashboard runs `marked` to turn the nurse-authored markdown into HTML and `DOMPurify` to sanitize it before injecting with `dangerouslySetInnerHTML`.
  - Copy [`react/HarnessDashboard.tsx`](react/HarnessDashboard.tsx) to your `components/` directory
  - Copy [`react/OwnerNav.tsx`](react/OwnerNav.tsx) to your `components/` directory
  - Create the harness dashboard page route (e.g. `app/harness/page.tsx`) rendering `<HarnessDashboard />`
  - Add `<OwnerNav />` inside `<UserProvider>` in `app/layout.tsx`, before the main content

The navigation bar will only appear when logged in as the owner and provides
quick access to the home page and harness dashboard. The dashboard will refresh
every 5 seconds to show live harness progress.

## Deploy dashboard update

Redeploy with the [deploy command](deploy.md#deploy), which passes the added
harness variables from `.env` to the deployment. Keep `OWNER_USER_ID` server-only.

## Evaluate M1 before handoff

The Evaluator records `REVIEW` started, then checks the deployed application
against the spec with real tools and retains the evidence:

- The baseline starts, the sign-in page renders and starts a device flow, and an
  authenticated owner can use the app and reach `/harness` from the global
  Harness navigation. Sign the browser in with the CLI token as the
  `fulcra_access_token` cookie, and ask the user to try the real sign-in once
  through `outstanding-issues.md` (non-blocking; see the
  [control-flow rules](harness-control-flow.md#rules)).
- The runs endpoint returns the actual M1 run ID and its recorded steps; the
  dashboard renders them, not an empty state or hardcoded demonstration data.
- Verify record writing during this first harness run: write a real REVIEW
  progress event, read it back with `fulcra-api get-records`, and check its run ID,
  step, status, and JSON string note. Confirm the same event appears through the
  runs endpoint and in the dashboard after refresh. Use this run's annotation,
  not a separate command-test log. The overview and issues panels load their
  workspace files without API errors.
- Unauthenticated and non-owner requests cannot read runs, overview, or issues;
  owner controls are hidden for a non-owner. Verify backend denial, not only
  conditional UI rendering. No second account is needed: send the owner's token
  with its `fulcradynamics.com/userid` claim changed. `isOwner()` reads the claim
  without verifying the signature, so this tests the backend's owner check,
  while the Fulcra API still rejects the altered token. Expect `401` without a
  cookie, `403` with the altered token, and `{"isOwner": false}` from the owner
  route.
- Build/check commands and relevant baseline regression checks pass. Record
  the commands, results, tested deployment URL, and UI/API evidence in workspace
  history so the result can be inspected later.

Include the commands/UI actions, tested deployment URL, and observed results in
the REVIEW event's required `evidence` string, with workspace paths for longer
tool output. Confirm evidence appears below the detail in the dashboard cells.

Only after these checks pass may the Evaluator record `REVIEW` completed with
evidence of the successful evaluations actually performed. Missing or blocked
checks are not passes; record the blocker and keep the milestone incomplete.
The Coordinator then records `MARK_COMPLETE`, saves M1 completion and evidence,
and records `RUN_COMPLETE`. Refresh the overview and read back the terminal
events; confirm the dashboard displays the real review and completed M1 run
before sharing it as the finished baseline. If verification fails, keep M1
incomplete and follow the retry/escalation rules in the control-flow reference.

**Do not present an empty dashboard as complete.** A URL may be shared earlier
only as an explicitly in-progress preview. This gate applies to both Svelte and
React; lack of testing is not a harness exemption.
