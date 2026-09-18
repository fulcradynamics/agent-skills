# Ordinary messaging acceptance

Entry prompt: “Send this update to our connected test peer, then check for new messages.”

Preconditions and runtime: a dedicated connection between two authorized test accounts. Exercise the skill separately with the CLI and MCP. Verify each authenticated account ID through the selected interface before mutations.

Expected outcome: a successful tool result is sufficient to report that the update was posted. Routine sending and cursor updates do not trigger readback checks. Reply to a peer's request with the outcome when available; if the work is pending, acknowledge receipt on the shared outbox and follow up with the outcome.

Mutations and approval: authorize test messages and cleanup before starting; record a unique run identifier, exact record IDs, and changed cursor paths locally. No new shares or schedules are required.

Cleanup: remove the test messages and restore the prior test cursor state. Incomplete cleanup fails the run.

Evidence: record the skill commit, timestamp, host/interface, account IDs, CLI versions where applicable, tool calls/results, and cleanup status in a locally ignored `.acceptance-runs/` directory. The evaluator may read records to verify the test outcome; those checks are not part of routine skill execution.
