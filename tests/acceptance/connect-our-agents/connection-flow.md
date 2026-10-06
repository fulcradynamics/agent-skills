# Connection and polling acceptance

Entry prompt: “Connect with the agent in this invitation on my behalf.” Supply a designated test peer's account ID, share name, introduction fields, and an explicit peer-owner acceptance step.

Preconditions and runtime: two authorized test accounts; run independently through a CLI-capable agent and an MCP-only agent. Verify each authenticated account ID through that interface before mutations.

Expected outcome: use the initial connection request as authorization for the dedicated share. Create one `Event/<uuid>` channel with the skill's fields, and share exactly that ID with the peer, with no other types, files, or `share_all_data`. Preserve invitation values. Wait for the peer owner's acceptance before the peer creates its return share. Report awaiting a reply until the return channel is shared and an `ack` whose `in_reply_to` is the introduction's `message_id` arrives. Resume in another session by discovering the connection from share listings and channel records, without creating duplicate channels. An on-demand check retrieves replies without installing a schedule. An explicitly requested recurring check reports its actual configuration status.

Variant, no known peer ID: the invitation carries the user's ID and channel; the peer shares back and introduces itself; the inviter then shares its channel and acknowledges.

Variant, legacy peer: the peer shares a `MomentAnnotation` mesh outbox. The agent reads it, sends new messages only on its v1 channel, and uses its own mesh outbox only for one message pointing the peer to the new skill.

Mutations: dedicated test channels, shares, introductions, acknowledgments, cursor files; a schedule only in the separately authorized recurring-check case. Give artifacts a unique run identifier and record exact IDs and paths as they are created.

Approval gates: authorize the peer-visible test exchange and cleanup before starting. Honor the peer's acceptance step and obtain authorization for any test schedule.

Cleanup: remove a test schedule, revoke test shares, delete test messages, remove test files, then archive test channels. Clean only manifest-listed artifacts; incomplete cleanup fails acceptance.

Evidence: skill commit, timestamp, host/interface, account IDs, CLI versions where applicable, invitation-field readback, actual share scope, peer acknowledgment, reuse on resumption, schedule status, and cleanup. Keep raw receipts locally in an ignored `.acceptance-runs/` directory. No live acceptance is implied by structural validation.
