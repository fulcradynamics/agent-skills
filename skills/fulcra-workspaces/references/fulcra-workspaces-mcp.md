# Fulcra Workspaces MCP Reference

Use `get_data_updates` with timezone-aware timestamps to detect activity. Use `list_files`, `read_file`, and `write_file(path, content, content_type="text/markdown")` for workspace coordination. Read current shared content before modifying it.

Use `delete_file` only after archive verification; use `list_files(path, include_versions=true)` and `restore_file` for recovery. Preserve naming, OKF, archive-before-delete, and concurrency rules. Use CLI for binary/local artifacts.
