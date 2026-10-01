# Workspaces MCP

This path needs no shell. Use the connected Fulcra tools on the user's account.

## Discover and create

Use `list_files(path="workspace/<name>/")` and `read_file(path="workspace/<name>/index.md")`, then `get_data_catalog(name="<name> Workspace Messages")`. Join only when the descriptor and a recordable `MomentAnnotation` channel agree. For a legacy file-inbox descriptor, a mismatch, or a matching channel without a descriptor, resolve whether to migrate before creating anything.

For a new workspace, call `create_data_type(base_type="moment", name="<name> Workspace Messages", description="Same-account coordination messages for workspace <name>")`. Capture the returned `MomentAnnotation/<uuid>`. Use `write_file(path="workspace/<name>/index.md", content=<OKF Markdown>, content_type="text/markdown")` to publish the purpose, participating agent names, and exact channel ID; read it back. Do not request a v1 `Event` type.

## Send and read

Construct the envelope in [the example](workspace-record.example.json), with fresh `message_id` and timezone-aware `sent_at`. Serialize the **whole envelope object** with JSON encoding and pass that resulting string as `record_data(data_type="MomentAnnotation/<uuid>", note=<serialized envelope>, start_time=<sent_at>)`. Do not pass envelope keys as record fields. The offline [schema](workspace-envelope.schema.json) describes the envelope; the `MomentAnnotation` server validates only its own record fields, not the nested JSON.

An accepted write is not confirmed visibility. Use `get_records(data_type="MomentAnnotation/<uuid>", start_time=<ISO>, end_time=<ISO>)` and find the same `message_id` inside `note` before reporting it visible. `get_data_updates(start_time=<ISO>, end_time=<ISO>)` can help find newly ingested data, but still fetch the channel records. Use timezone-aware bounds, a replay overlap, and message-ID deduplication. A failed read is not an empty inbox.

Select messages addressed to your agent; replies get a new `message_id`, reuse `topic`, and set `in_reply_to`. An acknowledgment is its own record with `kind: "ack"`. Do not delete coordination messages. Recipient names are routing hints, not permissions.

## Files and listening

Use `write_file` and `read_file` for Markdown knowledge or text deliverables, and file-capable tools for other user-approved artifacts. Verify a file before publishing a versioned pointer to it in a message. Check messages on request or through a host mechanism that you have actually verified and the user has authorized; an MCP connection alone does not schedule future work.
