# Connection and checking acceptance

Entry prompt, inviter: “Connect my agent with <peer name>'s agent.” Supply no peer ID, so the agent must write an invitation.

Entry prompt, invitee: the invitation the inviter's agent wrote, pasted with “Connect with this agent.”

Preconditions and runtime: two authorized test accounts. Run preparation and acceptance through both CLI and MCP in separately authorized runs, including CLI preparation followed by MCP completion on the same saved outbox. A CLI-only inviter can prepare and verify ready-to-share text; at later consumption/completion it reports Pending and hands off for guarded metadata updates, with no stateless return-share. Verify each authenticated account ID through that interface before mutations. These are manual scenarios, not evidence of live execution.

Expected outcome:
- **Inviter:**
  - checks read-only for an appropriate prepared invitation; if verified, skips creation and reuses its exact saved code, channel and audience;
  - otherwise calls `create_agent_invitation` once or uses CLI creation with a secure code, full Event schema and named prepared invitation metadata, with no extra conversational confirmation or mandatory mechanics lecture, while respecting host approval/denial;
  - verifies saved state through public catalog/share reads without requiring a legacy marker wrapper;
  - presents ready-to-share text with the user's name, full Fulcra ID, skill URL and exact first-message topic;
  - reports prepared/reused, not sent or connected; shares nothing yet when no recipient ID was supplied.
- **Invitee:**
  - creates its own channel;
  - shares exactly that ID with the inviter, with no other types, no files, and no `share_all_data`;
  - sends an introduction.
- **Inviter, on its next check:**
  - verifies the exact invitation topic on the incoming channel's first record and its actual share owner, not its name or a body claim;
  - reads existing named `Connection details` or legacy metadata and follows the [public-tool completion sequence](../../../skills/connect-our-agents/references/invite.md#complete-a-single-person-invitation): verified consumed binding, narrow return share/readback, verified completed binding and peer association; unsafe metadata stops writes rather than invoking an unspecified workflow;
  - replies to the introduction only when separately authorized, with `in_reply_to` set to its `id`;
  - reports “connected” only after verifying reciprocal grants.
- **Resuming:** a later session, or a second agent for the same user, rediscovers the connection from share listings alone. It creates no duplicate channel and finds nothing unanswered.
- **Checks:** an on-demand check installs no schedule. A recurring check is set up only when explicitly requested, and it reports its actual configuration status.

Variant, invitation with known peer ID:
- Pass the exact supplied ID as MCP `recipient_userid` or CLI share `--user-id` with only the returned outbox as `--data-type`; verify only that outbox was shared immediately.
- Preparation sends no introduction and does not establish acceptance; the recipient still agrees before sharing back.

Variant, creation error or denial:
- With either CLI or MCP, even a validation-style error can follow partial writes. Stop writes and reconcile read-only; no automatic retry, new code/channel or generic-tool fallback, including switching to the other preparation path.
- Host approval/denial is honored. No ready-to-share text is presented without verified saved state.

Variant, separately authorized direct connection with known peer ID:
- Generic CLI/MCP create/share and authorized introduction remain supported; this is not a fallback for invitation failure.
- The invitee's agent reports the request and shares back only after its user agrees.

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

## Named invitation lifecycle regression

Offline scripted acceptance case: supply synthetic public-tool receipts to the agent and inspect its requested calls without executing writes. This is a scenario specification, not a claim of native-agent or live-service execution. The static tests enforce the documented sequence and guards; they do not run the server state machine.

Use exact synthetic IDs: inviter `00000000-0000-0000-0000-000000000001`, recipient `00000000-0000-0000-0000-000000000002`, owned outbox `Event/00000000-0000-0000-0000-000000000010`, incoming channel `Event/00000000-0000-0000-0000-000000000020`. Supply compatible active Event schemas and complete catalog/share/history receipts.

1. Return canonical `create_agent_invitation` success without a recipient ID (`shared_with:null`). Supply the saved description below and no outgoing targeted grants. Expect reuse verification to read the existing `invitation`, show exact `handshake 0123456789abcdef0123456789abcdef`, and make no post-creation writes.

   ```text
   Agent contact channel
   Contact label: "Recipient's agent"
   Connection details: {"version":1,"invitation":{"code":"0123456789abcdef0123456789abcdef","state":"prepared","prefix":"handshake","extra":{"note":"literal } and [agent_connection: inside JSON"}},"unknown":{"keep":[1,2]}}
   Unrelated notes: preserve exactly
   ```

2. Recipient accepts and shares only the incoming channel directly to the inviter. Supply complete history containing one first record with `kind:"message"`, the exact saved topic and a timezone-qualified timestamp. A body claiming a different ID must not change the selected owner. No preliminary ack/reply. Expect public catalog/share/history reads, then `update_data_type` with the full previous description as `expected_description`: only state becomes `consumed` and the exact `peer_userid`/`incoming_data_type` binding is added. Return `verified:true` and independent catalog readback; no share is allowed before both.
3. With unchanged evidence and no targeted outgoing grant, expect exactly one public `create_share` for the owned outbox and actual recipient ID, with no groups/files/time bounds or all-data access. Supply a valid direct outgoing grant on independent `list_shares`. Expect a second guarded metadata update to `completed` and `peers:[{"fulcra_userid":"00000000-0000-0000-0000-000000000002","data_type":"Event/00000000-0000-0000-0000-000000000020"}]`. Its `expected_description` is the consumed description, not the original prepared one. Supply verified update, catalog readback and reciprocal grants. Only now report Connected; no automatic reply.
4. Compare both saved descriptions: code, prefix, unknown nested keys, string containing braces/marker text, label and unrelated bytes survive. Repeat with folded whitespace and with the existing legacy `[agent_connection: <same JSON>]` wrapper. On the deliberate consumption edit, replace only that field with `Connection details: <edited JSON>`, adding separator newlines if its brackets touch adjacent text. Do not append a duplicate or migrate other fields. Read-only discovery must leave the legacy wrapper untouched.

Replay each interruption as a separate resumed session:

| Receipt or interruption | Expected calls/outcome |
|---|---|
| Consumed, valid narrow grant present, same binding | Recheck evidence, finish completed update/peer association with fresh expected_description; zero create_share calls. |
| Consumed, grant absent or revoked | Read-only Pending; zero writes, no automatic retry or recreation. |
| Completed, grants present | Read-only Connected; no repeated updates, shares or duplicate peers. |
| Completed, grant revoked | Read-only discovery reports access missing, not Connected; no reset/re-share. |
| Consumed, changed binding or account | Read-only Pending; no rebinding, sharing or completion. |
| Prepared with valid existing recipient grant | Consume then complete after readback, without another create_share. |
| Wider/malformed targeted grant, group/time-bound incoming grant, duplicate matching channels, tied first timestamps or partial history | No completion/share; report unavailable or ambiguous evidence. |
| Consumption update uncertain, verified=false, stale expected_description, or host denial | Stop writes; reconcile read-only. No return share or alternate route. |
| Share uncertain after consumption | Stop writes; re-read. A later authorized check may complete only if the exact grant is independently present; absence never authorizes retry. |
| Completion update uncertain | Stop writes and re-read. Already completed means discovery only; consumed plus valid grant may finish on a later authorized check, never re-share. |
| Malformed/truncated JSON, invalid version/state/binding, duplicate JSON keys, duplicate fields or mixed old/new target fields | Reject before any write; do not choose one field or invent repair. |

For any future execution, capture the exact ordered public calls, description before/after each guarded update and independent grant receipts. Do not count static phrase assertions as execution of this lifecycle.

Keep raw receipts locally in an ignored `.acceptance-runs/` directory. Structural validation alone is not live acceptance.
