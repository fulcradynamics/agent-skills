# Testing this skill repository

## Account isolation for repository tests

Skill tests that authenticate to Fulcra MUST use the **agent-skills environment
credentials**. The expected tester is `leif+agent-skills-tester@fulcradynamics.com`.
Never use the Shell Beach account, a shared account, or ambient/default credentials.
This is contributor/acceptance-test guidance for this repository, not an account
requirement for ordinary users building their own apps with these skills.
Offline synthetic fixture tests need no Fulcra credentials and must remain offline.

Before any test write (including bootstrap, workspace creation, records, uploads,
deployment or cleanup):

1. Obtain the dedicated agent-skills environment's config path from the test
   operator. Set it explicitly; do not guess a path or copy credentials from a
   shared environment. Pass `--config-path "$AGENT_SKILLS_CONFIG_PATH"` on every
   `fulcra-api` invocation, including `user-info` and access-token retrieval.
2. Run `uvx fulcra-api --config-path "$AGENT_SKILLS_CONFIG_PATH" user-info`
   to obtain the Fulcra user ID. This command may not return an email: a successful
   response alone does not verify the tester account. Confirm the expected email
   through the authenticated identity-provider profile, or match the user ID to
   an independently verified tester mapping. Keep tokens in memory and out of logs.
   Record the verified identity and test scope, never credential contents.
   Derive owner IDs from this verified account, not an existing shared app.
3. Give every worker and independent evaluator the same explicit config path,
   expected identity and isolated target/resource IDs. Each context must verify
   identity before writes; child processes, API clients and browser sessions must
   use only credentials from that configuration. Do not inherit an unrelated
   browser login or ambient authentication.
4. Keep all test workspaces, harness records, data types, deploy projects and
   artifacts inside the isolated tester account and approved test scope. Never
   create test artifacts in Shell Beach or other shared workspaces. Retain IDs
   for scoped cleanup and verify cleanup using the same account.

Missing credentials, an unverified/mismatched identity, expired authorization or
an unavailable config is a blocker. Stop and ask the operator to fix the test
environment. There is **no credential fallback**, including retries, worker
handoffs and cleanup. Do not try a shared account to make a test pass.

## App-builder checks

Run offline regressions with `node --test tests/app_builder/*.test.mjs` (Node 22+).
See [app build acceptance](acceptance/build-and-deploy-a-web-app/end-to-end.md)
for the separately authorized live scenario. Local browser fixtures are synthetic
and do not establish live acceptance.
