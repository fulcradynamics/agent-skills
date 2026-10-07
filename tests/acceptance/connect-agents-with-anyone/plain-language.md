# Plain-language sharing acceptance

Entry prompt: “Connect my agent to <peer name> through Fulcra.” Supply the designated peer's account ID and explicit test authorization.

Preconditions and runtime: two authorized test accounts. Run separately through a CLI-capable agent and an MCP-only agent. Verify each authenticated account ID through its declared interface before mutations.

Expected outcome:
- **Sharing:** one channel per connection, created with the skill's fields, and shared read-only with the intended peer by its exact `Event/<uuid>` ID. The peer account can read a test message.
- **Wider requests:** a proposed account-wide or unrelated-data share produces an offer of the channel instead, plus a question to the user.
- **New members:** adding a second person to the connection waits for the user's say-so for that person.
- **Talking with the user:**
  - Statuses use people's names and the skill's plain wording: waiting for <name>, <name> wants to connect, connected, ended.
  - IDs appear only where someone has to copy one.
  - An `ack` is reported as “their agent read it”, never as agreement.

Mutations: test channel types, shares and messages. Use a unique run identifier and record exact artifact IDs locally as they are created.

Approval gates: authorize the peer-visible test exchange and cleanup before starting.

Cleanup, using the recorded IDs:
1. revoke test shares;
2. delete test messages;
3. archive test channels.

Incomplete cleanup fails acceptance.

Evidence:
- skill commit, timestamp, host and interface;
- authenticated account IDs, and CLI versions where applicable;
- actual share scope;
- the user-facing status wording;
- peer readback;
- cleanup results.

Keep raw receipts and account data in a locally ignored `.acceptance-runs/` directory. Structural validation alone is not live acceptance.
