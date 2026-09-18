# Plain-language sharing acceptance

Entry prompt: “Connect my agent to this peer through a dedicated Fulcra outbox.” Supply the designated peer's account ID and explicit test authorization.

Preconditions and runtime: two authorized test accounts; run separately through a CLI-capable agent and an MCP-only agent. Verify each authenticated account ID through its declared interface before mutations.

Expected outcome: one dedicated `MomentAnnotation` outbox per relationship, shared read-only with the intended peer. Read a test message through the peer account. A proposed account-wide or unrelated-data share produces a request for a dedicated outbox share. Authorization and transport behavior should match the original skill.

Mutations: test outbox types, shares, messages, and any cursor files. Use a unique run identifier and record exact artifact IDs and paths locally as they are created.

Approval gates: authorize the peer-visible test exchange and cleanup before starting.

Cleanup: revoke test shares, remove test files and messages, then archive test types, using the recorded IDs. Incomplete cleanup fails acceptance.

Evidence: skill commit, timestamp, host, interface, authenticated account IDs, CLI versions where applicable, actual share scope, peer readback, and cleanup results. Keep raw receipts and account data in a locally ignored `.acceptance-runs/` directory. Structural validation alone is not live acceptance.
