# Plain-language group acceptance

Entry prompt: "Set up a group so my agent can talk with my teammates' agents." Supply designated test peers and explicit test authorization.

Preconditions and runtime: three authorized test accounts; run through a CLI-capable agent, and through an MCP-only agent for the steps the MCP supports. Verify each authenticated account ID before mutations.

Expected outcome: the agent explains the group in plain language, asks one confirmation covering the group, the outbox share, and the check cadence, and creates one dedicated `MomentAnnotation` outbox shared into the group. A proposed account-wide or unrelated-data share produces a request for the dedicated outbox share instead. An MCP-only agent says that creating and joining need the CLI for now. User-facing text carries no alarmist warnings.

Mutations: a test group, outbox types, shares, messages, and cursor files, recorded locally with a unique run identifier.

Approval gates: authorize the member-visible exchange and cleanup before starting.

Cleanup: delete test shares, leave and delete the test group, then archive test types, using the recorded IDs. Incomplete cleanup fails acceptance.

Evidence: skill commit, timestamp, host, interface, authenticated account IDs, CLI versions, share scopes, member readback, and cleanup results, kept in a locally ignored `.acceptance-runs/` directory.
