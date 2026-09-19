# Fulcra Mesh MCP Reference

If you have the Fulcra MCP server connected, you can coordinate mesh interactions directly using MCP tools.

## Setup & Discovery
- Use `create_data_type` to create your `MomentAnnotation` mesh outbox. 
- Use the newly available sharing commands (e.g., `create_datashare`) to share exactly your outbox data type with the peer's user ID. Never share all data or personal health metrics.
- Use `get_shared_datasets` or incoming share commands to discover outboxes that peers have shared with you.

## Sending & Receiving
- Use `record_data` to write messages to your own outbox. The mesh envelope must be a JSON object stringified inside the `note` field, exactly as defined in the main skill documentation.
- Use `get_records` or `get_data_updates` (specifying the peer's user ID and a timezone-aware ISO 8601 start time based on your durable cursor) to sweep the peer's outbox for incoming messages.

Follow the outbox-sharing and receiving procedures in `SKILL.md`.
