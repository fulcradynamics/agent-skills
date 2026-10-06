# Ordinary messaging acceptance

Entry prompt: “Send this update to our connected test peer, then check for new messages.”

Preconditions and runtime: a dedicated connection between two authorized test accounts. Exercise the skill separately with the CLI and MCP. Verify each authenticated account ID through the selected interface before mutations.

Expected outcome: the message is one record on the agent's own channel with the skill's fields and a fresh `message_id`, and no fields outside them. A send that returns an upload ID is reported as sent; routine sending and cursor updates do not trigger readback checks. A message body containing quotes and apostrophes arrives intact. Reading resumes from the cursor with an overlap, skips `message_id`s already handled, and reports a failed read as unknown rather than empty. Reply to a peer's request with the outcome when available; if the work is pending, send an `ack` with `in_reply_to` and follow up with the outcome.

Mutations and approval: authorize test messages and cleanup before starting; record a unique run identifier, exact record IDs, and changed cursor paths locally. No new shares or schedules are required.

Cleanup: delete the test messages and restore the prior test cursor state. Incomplete cleanup fails the run.

Evidence: record the skill commit, timestamp, host/interface, account IDs, CLI versions where applicable, tool calls/results, and cleanup status in a locally ignored `.acceptance-runs/` directory. The evaluator may read records to verify the test outcome; those checks are not part of routine skill execution.
