# Fulcra Situational Awareness MCP Reference

Call `get_data_updates(start_time, end_time)` with timezone-aware timestamps. Inspect `data_types` and `file_changes`, then use `get_data_catalog` and its reported compatible tools to query changed data, or `read_file` for changed files.

Read `workspace/<name>/index.md` for its `MomentAnnotation/<uuid>` channel, then use `get_records` with timezone-aware bounds. Parse each record's `note` and follow `fulcra-workspaces` for addressing, replies, and deduplication.
