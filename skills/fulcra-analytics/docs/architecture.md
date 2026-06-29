---
type: Architecture Document
title: fulcra-analytics Modular Architecture
description: Initial modular architecture for parsing and statistically analyzing Fulcra user data.
---

# fulcra-analytics Modular Architecture

## Design goals

- Accept Fulcra CLI JSON, JSONL, and CSV exports.
- Normalize heterogeneous Fulcra records into predictable tables.
- Keep analysis reproducible and inspectable.
- Separate raw-data parsing from statistical summarization and report writing.
- Avoid uploading raw personal data unless explicitly authorized.

## Modules

### `fulcra_analytics.schemas`

Defines lightweight Pydantic models for input metadata, analysis windows, and summary results. These models are intentionally generic so the package can support many Fulcra data types over time.

### `fulcra_analytics.loader`

Loads JSON, JSONL, and CSV files and returns analysis-ready records. Future versions should add direct wrappers around commands such as:

```bash
uv tool run fulcra-api get-records <DataType> <Range>
uv tool run fulcra-api metric-time-series <DataType> <Range>
```

### `fulcra_analytics.statistics`

Computes descriptive statistics:

- row counts,
- column presence and missingness,
- numeric summaries,
- timestamp ranges,
- grouped summaries,
- simple window comparisons.

### `fulcra_analytics.reports` (future)

Will convert summary objects into OKF markdown reports with `Question`, `Data Used`, `Methods`, `Findings`, `Caveats`, and `Next Steps` sections.

### `fulcra_analytics.cli`

Typer-based CLI entrypoint for local analysis workflows.

## Data flow

```text
Fulcra CLI / export file
        ↓
loader.py
        ↓
normalized records/table
        ↓
statistics.py
        ↓
summary objects
        ↓
reports.py
        ↓
OKF markdown report / optional artifact
```

## MVP milestones

1. Scaffold package and dependencies.
2. Implement robust loading for JSON/JSONL/CSV exports.
3. Implement descriptive summaries for numeric and timestamp fields.
4. Generate an OKF markdown report.
5. Add direct Fulcra CLI fetch helpers.
6. Add privacy/sanitization checks before upload.
