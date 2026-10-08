# Fulcra Agent Backup MCP Reference

Use `list_files(path, include_versions=true)` to inspect backup versions and `restore_file(version_id)` to restore one. MCP `write_file` accepts text only, so use the CLI reference to upload or download `memory.tar.gz`.

Keep local tar creation, inspection, explicit overwrite confirmation, and extraction in the shell. Use `read_file(path, include_binary=true)` only for a small archive whose base64 safely fits context.
