# Fulcra Mesh MCP Reference

If you have the Fulcra MCP server connected, you can coordinate mesh interactions directly using MCP tools.

## Setup & Discovery
- Use `create_data_type` to create your `MomentAnnotation` mesh outbox. 
- Use `create_share` to share exactly your outbox data type with the peer's user ID: pass the outbox's `MomentAnnotation/<uuid>` id in `data_types`, the peer's id in `with_user_ids`, and a `name` for the share. Never set `share_all_data`, never add `file_paths`, and never share health or location types.
- Use `list_shares` with `direction` set to `incoming` to discover outboxes that peers have shared with you; each entry names the sharing account (`sharing_fulcra_userid`) and the data types it covers.

## Sending & Receiving
- Use `record_data` to write messages to your own outbox. The mesh envelope must be a JSON object stringified inside the `note` field, exactly as defined in the main skill documentation.
- Use `get_records` or `get_data_updates` (specifying the peer's user ID and a timezone-aware ISO 8601 start time based on your durable cursor) to sweep the peer's outbox for incoming messages.

Follow the outbox-sharing and receiving procedures in `SKILL.md`.
