---
type: Module Design
title: fulcra_analytics.client Implementation Notes
description: Python client wrapper for Fulcra API/CLI interactions used by fulcra-analytics.
---

# fulcra_analytics.client Implementation Notes

## Purpose

The `client` module provides a typed Python interface for Fulcra API interactions used by analytics workflows.

This first implementation uses the supported Fulcra CLI invocation:

```bash
uv tool run fulcra-api ...
```

That keeps authentication, token refresh, and CLI/API compatibility centralized in the existing Fulcra tooling while still giving the analytics package a clean client object.

## Public API

- `FulcraClient`
- `FulcraClientError`
- `default_client()`

## FulcraClient methods

Core execution:

- `command(args)`
- `run(args, timeout=None)`
- `json(args, timeout=None)`
- `text(args, timeout=None)`

Data methods:

- `catalog(base_types_only=False)`
- `user_info()`
- `data_updates(period)`
- `get_records(data_type, time_range)`
- `get_records_dataframe(data_type, time_range)`
- `metric_time_series(data_type, time_range)`
- `metric_time_series_dataframe(data_type, time_range)`

File Store helpers:

- `file_list(path)`
- `file_stat(path)`
- `file_download(remote_path, local_path)`
- `file_upload(local_path, remote_path)`
- `file_delete(remote_path)`

## Error handling

`FulcraClientError` is raised when:

- the CLI exits with a non-zero status,
- the CLI subprocess exceeds the configured timeout,
- JSON parsing fails for a method expected to return JSON.

Error messages include the command and stderr/stdout snippet (or timeout value) to aid debugging without hiding the underlying Fulcra CLI failure.

## DataFrame integration

`get_records_dataframe()` and `metric_time_series_dataframe()` pass raw JSON payloads through `fulcra_analytics.loader.dataframe_from_payload()` so client consumers get the same normalization behavior as file exports.

## Verification

Tests mock `subprocess.run` and verify:

- command construction,
- JSON parsing,
- non-zero exit error handling,
- DataFrame normalization integration,
- file download/upload command shape.
