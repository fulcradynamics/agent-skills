---
type: Module Design
title: fulcra_analytics.cli Implementation Notes
description: Command-line entrypoint for fetching Fulcra data and printing descriptive statistics.
---

# fulcra_analytics.cli Implementation Notes

## Purpose

The CLI lets users run Fulcra Analytics directly from the command line with:

```bash
uv tool run fulcra-analytics ...
```

It uses `FulcraClient` for Fulcra CLI/API interactions, `loader` normalization for DataFrame creation, and `statistics` for descriptive summaries.

## Commands

### `records`

Fetch records via `fulcra-api get-records` and print JSON summary statistics:

```bash
uv tool run fulcra-analytics records StepCount "1 week" --pretty
```

### `metrics`

Fetch metric time-series data via `fulcra-api metric-time-series` and print JSON summary statistics:

```bash
uv tool run fulcra-analytics metrics HeartRate "1 day" --group-by source
```

### `file`

Analyze a local JSON, JSONL/NDJSON, or CSV export:

```bash
uv tool run fulcra-analytics file export.json --pretty
```

### `catalog`

Print Fulcra catalog JSON:

```bash
uv tool run fulcra-analytics catalog --base-types-only --pretty
```

### `user-info`

Print authenticated Fulcra user info JSON:

```bash
uv tool run fulcra-analytics user-info --pretty
```

## Output

All commands write JSON to stdout. Summary commands include a `metadata` section identifying the input source, data type, and time range or file path.

## Verification

Tests use Typer's `CliRunner` and mocked client objects to verify:

- `records` uses the client and statistics summary path,
- `metrics` uses metric time-series data,
- `file` loads local exports,
- `catalog` and `user-info` pass through client JSON.
