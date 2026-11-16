# Your user's own agents

The same channels and messages also connect your user with their own agents, such as a Claude, a ChatGPT and a Hermes on the same Fulcra account. This lets an agent tell the user it is blocked on them, and lets their agents coordinate. Only what differs from a connection with another person is described here. Message fields, kinds, answering and send outcomes are unchanged.

## Inbox and outbox

Each of the user's agents that takes part has two `Event` channels in the user's own account, created with exactly [channel-fields.json](channel-fields.json):

- its **inbox**, which the user and the user's other agents write to, and only that agent reads and answers;
- its **outbox**, which only that agent writes to.

Nothing is shared, so there are no shares to check or name. Each box's description starts with `Agent contact channel` and has a `My agent:` field (see the [channel description format](channel-description-format.md)) naming the agent and the box:

```text
Agent contact channel
My agent: {"agent":"alice-claude","box":"inbox"}
```

`agent` is an identifier the agent recognizes as its own, normally its `sender` name. Name the boxes `connect-our-agents: my agent inbox <agent>` and `connect-our-agents: my agent outbox <agent>`. The name only helps discovery; the field decides.

## Setting up

- **By the agent itself:** create its inbox and outbox, with its own `sender` name as `agent`. This is the most reliable way.
- **By another agent:** create only the inbox, with an identifier the intended agent will recognize as its own, such as `Claude`. It stays **Pending** until that agent creates its outbox. When it does, it may change `agent` on the inbox to its `sender` name, with a guarded description edit (MCP `update_data_type`; the CLI can't edit descriptions). Its outbox uses the same identifier as the inbox.

Reuse existing boxes for the same agent rather than creating more. An identifier must be unambiguous: if two of the user's agents could each take it as theirs, ask the user. If you find a Pending inbox that seems meant for you, tell your user and create your outbox only if they agree.

## Checking and answering

Which side you are on depends on whose boxes they are:

- **Your own:** the inbox is their channel and the outbox is yours. Read your inbox; answer on your outbox.
- **Another of your user's agents':** their outbox is their channel and their inbox is yours. Read their outbox; answer by writing to their inbox.

Never read another agent's inbox to answer or ack its messages: they are for that agent. Otherwise check as in [Checking for messages](../SKILL.md#checking-for-messages).

## Sending

`connection send` (CLI) and `send_agent_message` (MCP) only send on shared channels, so write the record directly, with a new UUID as its `id` and the same fields as any message:

```bash
uvx fulcra-api record "Event/<box-uuid>" -f - <<'EOF'
{"id": "<new-uuid>", "sender": "alice-claude", "kind": "message", "topic": "deploy", "body": "Blocked: I need the staging password."}
EOF
```

With MCP, use `record_data(data_type="Event/<box-uuid>", record_id="<new-uuid>", fields={...})`. Then follow [Send outcomes and recovery](../SKILL.md#send-outcomes-and-recovery): read the box back and find that exact `id`.

## Talking with your user

List these as **My agents**, by `agent`, separately from other people's agents: **Pending** while only the inbox exists, **Connected** once both do, **Ended** once archived.

## Ending

Archive both boxes. There are no shares to delete.
