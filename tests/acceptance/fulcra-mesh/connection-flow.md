# Connection and polling acceptance

Entry prompt: “Connect with the agent in this invitation on my behalf.” Supply a designated test peer's account ID, share name, addressing and handshake fields, and an explicit peer-owner acceptance step.

Preconditions and runtime: two authorized test accounts; run independently through a CLI-capable agent and an MCP-only agent. Verify each authenticated account ID through that interface before mutations.

Expected outcome: use the initial connection request as authorization for the dedicated share. Preserve invitation values. Wait for the peer owner's acceptance before creating its return share. Report awaiting a reply until a return outbox and acknowledgment referencing the introduction arrive. Resume in another session by discovering the connection from share listings and outbox records, without creating duplicate channels. An on-demand check retrieves replies without installing a schedule. An explicitly requested recurring check reports its actual configuration status.

Mutations: dedicated test outboxes, shares, introductions, acknowledgments, cursor files; a schedule only in the separately authorized recurring-check case. Give artifacts a unique run identifier and record exact IDs and paths as they are created.

Approval gates: authorize the peer-visible test exchange and cleanup before starting. Honor the peer's acceptance step and obtain authorization for any test schedule.

Cleanup: remove a test schedule, revoke test shares, remove test files and messages, then archive test types. Clean only manifest-listed artifacts; incomplete cleanup fails acceptance.

Evidence: skill commit, timestamp, host/interface, account IDs, CLI versions where applicable, invitation-field readback, actual share scope, peer acknowledgment, reuse on resumption, schedule status, and cleanup. Keep raw receipts locally in an ignored `.acceptance-runs/` directory. No live acceptance is implied by structural validation.
