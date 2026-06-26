---
type: Module Design
title: fulcra_analytics.loader Implementation Notes
description: Loader module behavior for Fulcra CLI JSON output and exported files.
---

# fulcra_analytics.loader Implementation Notes

## Purpose

The `loader` module turns Fulcra CLI JSON output or exported JSON/JSONL/CSV files into normalized `pandas.DataFrame` objects for downstream analysis.

## Supported inputs

- JSON files containing a list of records.
- JSON files with common wrapper keys: `records`, `data`, `items`, `results`, `samples`, or `values`.
- JSONL/NDJSON files with one JSON payload per line.
- CSV files.
- Fulcra CLI JSON output through helper functions such as `get_records_dataframe()` and `metric_time_series_dataframe()`.

## Normalization rules

- Nested dictionaries are flattened using dotted column names, e.g. `metric.value`.
- Scalar list items become `value` records.
- Dicts keyed by record id become rows and preserve the outer key as `record_key`.
- Obvious timestamp/date columns are converted with `pandas.to_datetime(..., utc=True)` when possible.
- Lists are preserved as cell values unless they are top-level record containers.

## Public API

- `extract_records(payload)`
- `records_to_dataframe(records)`
- `dataframe_from_payload(payload)`
- `load_records(path)`
- `load_dataframe(path)`
- `run_fulcra_cli(args)`
- `dataframe_from_fulcra_cli(args)`
- `get_records_dataframe(data_type, time_range)`
- `metric_time_series_dataframe(data_type, time_range)`

## Verification

The implementation includes tests for:

- wrapped JSON payloads,
- nested Fulcra-like records,
- timestamp coercion,
- JSONL and CSV exports,
- dicts keyed by record id.
