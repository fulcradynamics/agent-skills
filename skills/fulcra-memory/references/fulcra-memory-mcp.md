# Fulcra Memory MCP Reference

Use `get_data_updates(start_time, end_time)` to discover changes; timestamps must be timezone-aware. Use `list_files`, `read_file`, and `write_file(path, content, content_type="text/markdown")` to maintain memory. Read the latest version before merging and writing shared content.

Use `list_files(path, include_versions=true)` and `restore_file(version_id)` for history and recovery. Use CLI for local or binary transfer.
