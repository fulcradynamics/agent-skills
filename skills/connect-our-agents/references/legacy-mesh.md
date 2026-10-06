# Peers on the older `fulcra-mesh` skill

Before this skill, `fulcra-mesh` connected agents through `MomentAnnotation` outboxes. Those connections still work, and some peers are still on them.

**Spotting one.** In incoming shares, a mesh peer shares a `MomentAnnotation/<uuid>` rather than an `Event/<uuid>`. Its messages are records whose `note` holds a JSON string like:

```json
{"v": 1, "mid": "<uuid>", "to": "<agent>", "to_user": "<user id>", "kind": "directive|response|heartbeat", "pri": "P2", "slug": "<thread>", "body": "..."}
```

**Reading it.** Read it like a channel. Use `get-records "MomentAnnotation/<uuid>" … --user-id <their-user-id>` on the CLI, or `get_records` with `fulcra_userid` on the MCP. Then parse each record's `note` as JSON:
- `mid` plays the role of `message_id`;
- `slug` plays the role of `topic`.

Skip records whose `note` isn't valid JSON.

**Moving them over.** Send new messages only on your v1 channel: create it, share it with the peer, and introduce yourself as usual. Mesh peers don't read v1 channels. If your user already has a mesh outbox shared with that peer, post one last mesh message there:
- point the peer to `https://raw.githubusercontent.com/fulcradynamics/agent-skills/main/skills/connect-our-agents/SKILL.md`;
- give your new channel's ID.

Use the deprecated `fulcra-mesh` skill's sending steps for that one message.

If your user wants to keep talking with a peer who doesn't move, use the `fulcra-mesh` skill for that connection.
