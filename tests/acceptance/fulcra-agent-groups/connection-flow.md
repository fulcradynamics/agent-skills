# Group creation and joining acceptance

Entry prompt: "Create a Fulcra group for our agents and invite this test peer." Supply a designated test peer and explicit test authorization.

Scripted reply when the agent asks for confirmation: "Yes, create the test group and outbox, check it hourly, and clean everything up when the test is done."

Scripted follow-up turn after the peer has joined: "Check the group."

Preconditions and runtime: three authorized test accounts; the creator and one joiner run through CLI-capable agents. When an MCP-only agent is available, a third member reads through it after a CLI join; otherwise record that leg as not run. Verify each authenticated account ID before mutations.

Expected outcome: one confirmation covers the group, the outbox share, and the check cadence. The creator creates a group with no data types, joins it, shares a dedicated outbox into it, sets up or reports its check cadence, posts a handshake to `all`, and produces an invite prompt that contains the group id and the skill URL. The joiner, following only the prompt, joins, shares its outbox, posts a handshake with its agent name and user ID, and reports its check cadence. Each member finds the others through group grants on its next check, skipping its own shares, and reads their handshakes with no other share between the accounts. Resuming in another session reuses the existing group and outbox.

Mutations: a test group, outbox types, shares, handshakes, cursor files, and schedules. Give artifacts a unique run identifier and record exact IDs as they are created.

Approval gates: authorize the test group, the member-visible exchange, any test schedule, and cleanup before starting.

Cleanup: remove test schedules, delete test shares, leave and delete the test group, then archive test types. Clean only recorded artifacts; incomplete cleanup fails acceptance.

Evidence: skill commit, timestamp, host/interface, account IDs, CLI versions, the invite prompt, share scopes, handshake readback per member, reuse on resumption, schedule status, and cleanup. Keep raw receipts locally in an ignored `.acceptance-runs/` directory.
