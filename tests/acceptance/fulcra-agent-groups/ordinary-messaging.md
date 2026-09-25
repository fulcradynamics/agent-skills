# Ordinary group messaging acceptance

Entry prompt: "Post 'acceptance update' to our test group, share the file `acceptance-note.md` with the group, then check the group for new messages." Create `acceptance-note.md` locally before the run.

Scripted reply when the agent asks for confirmation: "Yes, go ahead."

During the run, the test peer posts a message addressed by name to the agent under test. Scripted follow-up turn after it arrives: "Check the group again."

Once that check is done, the test is over. Scripted follow-up turn after that: "The test is done, clean up now."

Preconditions and runtime: a test group with at least three members on different accounts. Exercise sending and receiving separately with the CLI and the MCP. Verify each authenticated account ID before mutations.

Expected outcome: a successful tool result is sufficient to report that the update was posted. Every other member reads it on its next check. A message to one member by name is answered by that member; a request is answered with the outcome, or acknowledged and followed up. A file the user asks to share is shared into the group, announced with a message, and readable by the other members.

Mutations and approval: authorize test messages, the test file share, and cleanup before starting; record a unique run identifier, exact record and share IDs, and changed cursor paths locally.

Cleanup: remove the test messages and file share and restore the prior cursor state. Incomplete cleanup fails the run.

Evidence: skill commit, timestamp, host/interface, account IDs, CLI versions, tool calls/results, and cleanup status, kept in a locally ignored `.acceptance-runs/` directory.
