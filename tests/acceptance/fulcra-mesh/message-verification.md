# Message verification acceptance

Entry prompt: “Send this message to our established test peer and verify its status.” Supply a body with apostrophes, quotes, Unicode, multiline text, and literal shell syntax.

Preconditions and runtime: an existing dedicated relationship between two authorized test accounts; exercise a CLI-capable agent and an MCP-only agent separately. Verify the authenticated account IDs through the chosen interface before mutations.

Expected outcome: the record's `note` contains the serialized envelope. Readback matches the exact `mid` and body and is reported as saved. A peer acknowledgment provides receipt evidence. An absent result or query failure leaves the write unconfirmed; a retry retains the envelope and `mid`. The receiver handles duplicate `mid`s in its outbox once, including when different record IDs exist. An old message on the same slug, a changed body with the same ID, an empty result, or a malformed note does not falsely confirm the write. Identical IDs in another peer's outbox do not suppress unrelated work.

Mutations: test messages, acknowledgments, and cursor updates within the established test relationship. Record exact IDs and file paths locally using a unique run identifier. No new shares are required by this scenario.

Approval gates: authorize the peer-visible test messages and cleanup before starting.

Cleanup: restore prior test cursor state and remove the test messages by manifest-listed IDs. Leave the pre-existing relationship in place. Incomplete cleanup fails acceptance.

Evidence: exact skill commit, timestamp, runtime/interface, account IDs, CLI versions where applicable, encoded note and readback results, peer acknowledgment, duplicate handling, and cleanup. Keep raw receipts locally in an ignored `.acceptance-runs/` directory. Offline fixtures establish encoding and verification behavior only.
