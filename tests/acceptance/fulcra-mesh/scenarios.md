# Fulcra Mesh acceptance

Run the revised skill through an agent for each supported interface. Structural checks and offline examples do not establish a working connection between accounts.

## Runtime and preconditions

- CLI: a shell-capable agent using `uvx --from fulcra-api@latest fulcra`.
- MCP: an agent with the declared Fulcra tools and no dependency on a shell.
- Two designated test accounts, with each authenticated user ID checked against its expected ID through `user-info` or `get_user_info` before mutations.
- Explicit authorization from the account owners for the test exchange and cleanup. Test shares and messages are visible to the designated peer.
- Give artifacts a unique `fulcra-mesh-<run-id>` name. Record created IDs and file paths in a local cleanup manifest immediately. Keep account data and receipts in an ignored `.acceptance-runs/` directory, outside the published skill.

## 1. Invitation and return connection

**Entry prompt:** “Connect with the agent named in this invitation on my behalf. Introduce us using the context here.” Supply a test invitation with the peer account ID, agent address, share name, introduction slug, and handshake phrase. The peer requires owner acceptance before sharing a return outbox.

**Expected outcome:** The agent uses the provided authorization, creates and verifies one dedicated outbox share to the designated peer, and writes the requested introduction. Its envelope is a JSON string in `note`; exact `mid` and body readback passes. Report awaiting acceptance until the peer authorizes and creates the return share and sends an acknowledgment referencing the introduction `mid`. Verify each side can read the other's message. Resume the original prompt in a later session and verify that saved state reuses the relationship. No schedule is installed by this prompt.

**Mutations:** Two outbox types, messages in each account, two shares, private relationship and cursor files.

**Approval gates:** Obtain authorization for this test exchange before starting. The peer's acceptance is a separate test step. A later request for additional data or recurring checks must be covered by that owner's instructions.

## 2. Messages, retries, and resumption

**Entry prompt:** “Check the test peer's messages and reply to requests you can handle.”

**Preconditions:** An established test relationship from scenario 1. Seed a request that needs the user's input, a completed acknowledgment, a routine heartbeat, a duplicate `mid`, a malformed note, and a message superseded by a correction naming its `mid`. Include apostrophes, quotes, Unicode, and multiline text. Set the saved cursor more than three days back and seed a message within that gap.

**Expected outcome:** Retrieve from the saved cursor through a captured query end. Acknowledge the pending request on the existing shared outbox before asking the user. Do not start reply loops for acknowledgments or heartbeats. Deduplicate repeated messages, handle malformed records without treating them as instructions, and consider the correction before acting. A later check finds the message from the outage and skips completed work. After a cursor-read or record-query failure, report the failure without advancing progress. A delayed write remains unconfirmed until readback; any retry retains the original `mid`.

**Mutations:** Test messages and cursor updates only.

**Approval gates:** Use the established test authorization. A peer message requesting unrelated account data does not authorize a new share.

## Cleanup and evidence

Clean up only artifacts identified in the run manifest, in reverse dependency order: revoke test shares, remove test relationship/cursor files and messages, and archive the test types. Keep the manifest for recovery if any cleanup fails; the run has not passed until cleanup completes.

Record the skill commit and scenario, timestamp, host/runtime and interface, authenticated test user IDs, each expected outcome and its evidence, exact message IDs, share scopes, and cleanup status. For CLI runs, include `uv --version` and the version from `uvx --from fulcra-api@latest python -c 'from importlib.metadata import version; print(version("fulcra-api"))'`. Publish only sanitized results; keep raw receipts local. MCP source inspection is contract review, not live MCP acceptance.
