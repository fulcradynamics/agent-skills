# Connection and checking acceptance

Entry prompt, inviter: “Connect my agent with <peer name>'s agent.” Supply no peer ID, so the agent must write an invitation.

Entry prompt, invitee: the invitation the inviter's agent wrote, pasted with “Connect with this agent.”

Preconditions and runtime: two authorized test accounts. Run independently through a CLI-capable agent and an MCP-only agent, and also with one side on each interface. Verify each authenticated account ID through that interface before mutations.

Expected outcome:
- **Inviter:**
  - creates one `Event/<uuid>` channel with the skill's fields;
  - writes an invitation that carries its user's name, full Fulcra user ID, the skill URL, and the three steps (create a channel, share it, introduce yourself);
  - reports “waiting for <peer>”;
  - shares nothing yet.
- **Invitee:**
  - creates its own channel;
  - shares exactly that ID with the inviter, with no other types, no files, and no `share_all_data`;
  - sends an introduction.
- **Inviter, on its next check:**
  - finds the invitee's channel by share name;
  - checks its fields once;
  - shares back to the user ID on the incoming share;
  - replies to the introduction with `in_reply_to` set to its `id`;
  - reports “connected”.
- **Resuming:** a later session, or a second agent for the same user, rediscovers the connection from share listings alone. It creates no duplicate channel and finds nothing unanswered.
- **Checks:** an on-demand check installs no schedule. A recurring check is set up only when explicitly requested, and it reports its actual configuration status.

Variant, known peer ID:
- The inviter shares first and sends its introduction.
- The invitee's agent, asked to check its connections, reports “<inviter> wants to connect” with the introduction's content.
- It shares back only after its user agrees.

Variant, unsolicited request: a channel shared by someone the user never mentioned is reported as a request and is never shared back without the user's agreement.

Variant, legacy peer:
- The peer shares a `MomentAnnotation` mesh outbox.
- The agent reads it, and sends new messages only on its own channel.
- It uses its own mesh outbox only for one message pointing the peer to the new skill.

Mutations: test channels, shares, introductions, replies and acks, plus a schedule only in the separately authorized recurring-check case. Give artifacts a unique run identifier and record exact IDs as they are created.

Approval gates: authorize the peer-visible test exchange and cleanup before starting. Get the invitee user's agreement in the unsolicited variant, and authorization for any test schedule.

Cleanup, using only manifest-listed artifacts:
1. remove any test schedule;
2. revoke test shares;
3. delete test messages;
4. archive test channels.

Incomplete cleanup fails acceptance.

Evidence:
- skill commit, timestamp, host and interface;
- account IDs, and CLI versions where applicable;
- the invitation text and actual share scope;
- the introduction, reply and ack IDs;
- reuse on resumption, schedule status, and cleanup.

Keep raw receipts locally in an ignored `.acceptance-runs/` directory. Structural validation alone is not live acceptance.
