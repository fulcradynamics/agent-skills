# Fulcra MCP for Tracking and Dashboards

Use `get_data_catalog(category="user_configured")` and `get_data_catalog(category="base_type")` to discover schemas. Use `create_data_type` to create one.

After required consent, use `record_data`; timezone-aware timestamps are required and durations need start and end. Verify with `get_records`, or `get_time_series` only when the catalog lists it as compatible. MCP cannot delete individual records; use CLI for corrections requiring deletion.
