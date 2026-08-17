# Fulcra MCP for Third-Party Data Ingestion

Use `get_data_catalog(category="user_configured")` before creating a schema, and `get_data_catalog(category="base_type")` to inspect supported bases. Use `create_data_type` and retain the returned `<BaseType>/<uuid>` ID.

Use `record_data` for individual records and `get_records` to verify them. MCP currently records one item per call and does not expose record deletion or batch JSONL ingestion; use the CLI reference for bulk imports and record correction.

Use `list_files`, `read_file`, `write_file`, `delete_file`, and `restore_file` for text source maps and logs. `write_file` does not accept a local path or arbitrary binary payload, so use CLI for raw exports that are local, binary, or too large for context. Preserve archive-before-delete safeguards.
