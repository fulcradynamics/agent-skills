# Fulcra Situational Awareness MCP Reference

Call `get_data_updates(start_time, end_time)` with timezone-aware timestamps. Inspect `data_types` and `file_changes`, then use `get_data_catalog` and its reported compatible tools to query changed data, or `read_file` for changed files.

Check an inbox with `list_files(path="team/<team_name>/member/<your_agent_name>/inbox/")` and follow the `fulcra-workspaces` inbox lifecycle.
