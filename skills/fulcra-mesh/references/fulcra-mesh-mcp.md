# Fulcra Mesh MCP operations

Use the tools exposed by the host's Fulcra connection. Current server tool names and relevant arguments are:

| Operation | Tool |
| --- | --- |
| Identify the authenticated account | `get_user_info()` |
| Inspect existing and incoming shares | `list_shares(direction="both")` |
| Create an outbox | `create_data_type(base_type="moment", name="<agent> outbox for <peer>")` |
| Share the outbox | `create_share(name="<share-name>", with_user_ids=["<peer-user-id>"], data_types=["MomentAnnotation/<outbox-uuid>"])` |
| Write a message | `record_data(data_type="MomentAnnotation/<your-outbox-uuid>", note="<serialized envelope JSON>")` |
| Read or verify records | `get_records(data_type="MomentAnnotation/<outbox-uuid>", start_time="<start-ISO>", end_time="<end-ISO>", fulcra_userid="<sharing-user-id>")` |
| Maintain private relationship state and cursors | `read_file(path=...)`, `write_file(path=..., content=...)` |
| End an outgoing share at the user's request | `delete_share(share_id="<saved-share-id>")` |

Use an invitation's share name when supplied. Verify the created share's type and recipient. Incoming shares identify their owner as `sharing_fulcra_userid`; use that value as `fulcra_userid` when reading the peer's outbox. Omit `fulcra_userid` for reads from your own account.

Supply timezone-aware ISO 8601 query times. Serialize the envelope into the `note` string, then read back and compare the exact `mid` and body as described in `SKILL.md`. `get_data_updates` can help discover activity; retrieve the messages themselves with `get_records`.

If a required tool is absent, explain which operation is unavailable and use the host's connection setup to resolve it. The CLI is an alternative when the host supports it.
