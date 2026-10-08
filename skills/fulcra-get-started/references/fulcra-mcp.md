# Fulcra MCP

The connector handles authentication. Use `get_user_info`, `get_data_catalog`, `get_records`, `get_time_series`, and `get_data_updates` for discovery and retrieval. Always pass timezone-aware ISO 8601 timestamps.

Use `create_data_type`, `record_data`, `archive_data_type`, and `restore_data_type` for custom annotations. Use `list_files`, `read_file`, `write_file`, `delete_file`, and `restore_file` for versioned text files. `write_file` accepts text content; use CLI for local or binary file transfer.
