# Ordinary group messaging acceptance

Entry prompt: "Post this update to our test group, then check the group for new messages."

Preconditions and runtime: a test group with at least three members on different accounts. Exercise sending and receiving separately with the CLI and the MCP. Verify each authenticated account ID before mutations.

Expected outcome: a successful tool result is sufficient to report that the update was posted. Every other member reads it on its next check. A message to one member by name is answered by that member; a request is answered with the outcome, or acknowledged and followed up. A file the user asks to share is shared into the group, announced with a message, and readable by the other members.

Mutations and approval: authorize test messages, the test file share, and cleanup before starting; record a unique run identifier, exact record and share IDs, and changed cursor paths locally.

Cleanup: remove the test messages and file share and restore the prior cursor state. Incomplete cleanup fails the run.

Evidence: skill commit, timestamp, host/interface, account IDs, CLI versions, tool calls/results, and cleanup status, kept in a locally ignored `.acceptance-runs/` directory.
