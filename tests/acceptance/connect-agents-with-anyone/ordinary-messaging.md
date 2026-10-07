# Ordinary messaging acceptance

Entry prompt: “Send this update to <peer name>'s agent, then check for new messages.”

Preconditions and runtime: a connection between two authorized test accounts. Exercise the skill separately with the CLI and with MCP. Verify each authenticated account ID through the selected interface before mutations.

Expected outcome:
- **Sending:**
  - The message is one record on the agent's own channel.
  - It uses only the skill's fields, and sets neither `id` nor `start_time`.
  - A send that returns an upload ID is reported as sent, with no routine readback.
  - A body containing quotes, apostrophes, `$`, backticks and a line break arrives unchanged.
- **Checking:**
  - The agent reads both channels and reports as new only the peer's `message` and `reply` records addressed to it that no record of its own answers.
  - It answers each: a `reply` when it has the answer, otherwise an `ack` followed later by a `reply`. It never answers an `ack`.
  - A second check right afterwards reports nothing new.
  - A failed read is reported as unknown, not as an empty inbox.
- **Recipients:** a message addressed only to another agent name is not reported as new.

Mutations and approval: authorize test messages and cleanup before starting, and record a unique run identifier and exact record IDs locally. No new shares or schedules are required.

Cleanup: delete the test messages. Incomplete cleanup fails the run.

Evidence: record the following in a locally ignored `.acceptance-runs/` directory:
- skill commit, timestamp, host and interface;
- account IDs, and CLI versions where applicable;
- tool calls and results;
- cleanup status.

The evaluator may read records to verify the outcome; those checks are not part of routine skill execution.
