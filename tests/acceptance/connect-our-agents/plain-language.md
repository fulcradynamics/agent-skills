# Plain-language sharing acceptance

Entry prompt: “Connect my agent to this peer through Fulcra.” Supply the designated peer's account ID and explicit test authorization.

Preconditions and runtime: two authorized test accounts; run separately through a CLI-capable agent and an MCP-only agent. Verify each authenticated account ID through its declared interface before mutations.

Expected outcome: one dedicated `Event/<uuid>` channel per connection, created with the skill's fields and shared read-only with the intended peer by its exact ID. Read a test message through the peer account. A proposed account-wide or unrelated-data share produces a request for a share of the channel instead. Adding a second person to the connection waits for the user's say-so for that person.

Mutations: test channel types, shares, messages, and any cursor files. Use a unique run identifier and record exact artifact IDs and paths locally as they are created.

Approval gates: authorize the peer-visible test exchange and cleanup before starting.

Cleanup: revoke test shares, delete test messages, remove test files, then archive test channels, using the recorded IDs. Incomplete cleanup fails acceptance.

Evidence: skill commit, timestamp, host, interface, authenticated account IDs, CLI versions where applicable, actual share scope, peer readback, and cleanup results. Keep raw receipts and account data in a locally ignored `.acceptance-runs/` directory. Structural validation alone is not live acceptance.
