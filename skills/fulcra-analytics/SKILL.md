---
name: fulcra-analytics
description: "Analyze Fulcra user data with privacy-respecting Python and CLI workflows: fetch records or metrics, normalize them into DataFrames, compute descriptive summaries, and produce auditable JSON or OKF-ready reports."
homepage: https://github.com/fulcradynamics/agent-skills
license: MIT
user-invocable: true
tags:
  - fulcra
  - analytics
  - data-science
  - okf
  - pandas
metadata:
  openclaw:
    emoji: "📊"
  fulcra:
    default_output_namespace: analytics/
---

# Fulcra Analytics

Use this skill when a user wants to inspect, summarize, or statistically analyze Fulcra data such as health metrics, calendar records, location visits, annotations, activity records, or team/agent activity logs.

Fulcra Analytics is an early-stage modular Python skill template. It provides a CLI-backed Fulcra client, record normalization utilities, DataFrame descriptive statistics, and a command-line entrypoint for quickly producing JSON summaries.

The core principle is privacy-respecting analysis: keep raw personal data local by default, compute summaries and aggregates, and only upload sanitized reports or explicitly approved artifacts.

## When to Use

Use this skill when the user asks to:

- Analyze a Fulcra data type, metric, export, or time range.
- Summarize records from `fulcra-api get-records` or `fulcra-api metric-time-series`.
- Inspect JSON, JSONL/NDJSON, or CSV exports from Fulcra.
- Compute missingness, numeric summaries, categorical frequencies, boolean ratios, datetime ranges, or grouped summaries.
- Build an OKF-ready report from aggregate findings.
- Create a repeatable local analysis workflow for Fulcra data.

Do not use this skill when:

- The user only wants to create or configure custom data types; use Fulcra onboarding/tracking workflows instead.
- The task requires publishing raw health, location, calendar, or personal annotation data to a shared space without explicit authorization.
- The user needs advanced modeling, causal inference, forecasting, or visualization beyond descriptive summaries. This package can be a starting point, but the current implementation is intentionally lightweight.

## Installed Package Layout

The skill directory contains a Python package under `skills/fulcra-analytics/`:

```text
skills/fulcra-analytics/
  SKILL.md
  README.md
  pyproject.toml
  docs/
    architecture.md
    cli.md
    client.md
    loader.md
    statistics.md
  src/fulcra_analytics/
    __init__.py
    __main__.py
    cli.py
    client.py
    loader.py
    schemas.py
    statistics.py
  tests/
    test_cli.py
    test_client.py
    test_loader.py
    test_statistics.py
```

## Main Interfaces

### Command-line entrypoint

Use the CLI for routine analysis. It writes JSON to stdout.

```bash
uv tool run fulcra-analytics records StepCount "1 week" --pretty
uv tool run fulcra-analytics metrics HeartRate "1 day" --pretty
uv tool run fulcra-analytics file path/to/export.json --pretty
uv tool run fulcra-analytics catalog --base-types-only --pretty
uv tool run fulcra-analytics user-info --pretty
```

You can also run the package module directly inside a checkout or installed environment:

```bash
python -m fulcra_analytics records StepCount "1 week"
```

### Python modules

Use the Python API when composing analysis workflows in scripts or notebooks:

```python
from fulcra_analytics import FulcraClient, summarize_dataframe

client = FulcraClient()
df = client.get_records_dataframe("StepCount", "1 week")
summary = summarize_dataframe(df, group_by="source")
print(summary.to_dict())
```

Key modules:

- `fulcra_analytics.client`: CLI-backed Fulcra API wrapper.
- `fulcra_analytics.loader`: load JSON/JSONL/CSV exports and normalize Fulcra payloads into DataFrames.
- `fulcra_analytics.statistics`: descriptive statistics over DataFrames.
- `fulcra_analytics.cli`: Typer CLI for `uv tool run fulcra-analytics`.

## Recommended Workflow

1. Clarify the user's analysis question.
   - Example: "How did my steps vary over the last week?"
   - Identify data type, date/time range, grouping dimensions, and desired output.

2. Prefer local or CLI-backed data access.
   - Fetch records with `FulcraClient` or the CLI commands.
   - Keep raw data local unless the user explicitly authorizes upload.

3. Normalize records into a DataFrame.
   - Use `fulcra_analytics.loader` or CLI commands.
   - Supported local formats: `.json`, `.jsonl`, `.ndjson`, `.csv`.

4. Compute summaries.
   - Use `summarize_dataframe(df)`.
   - Add `group_by=<column>` when grouping by source, category, day, device, or another column is meaningful.

5. Report aggregate findings.
   - Use JSON for machine-readable output.
   - Convert findings to OKF markdown when storing in Fulcra File Store.
   - Include the question, data used, methods, findings, caveats, and next steps.

6. Verify outputs.
   - Confirm commands succeeded.
   - Confirm output is valid JSON or valid OKF markdown.
   - Cite exact paths or commands used.

## CLI Recipes

### Summarize records from Fulcra

```bash
uv tool run fulcra-analytics records StepCount "1 week" --pretty
```

This runs Fulcra CLI through `FulcraClient`, normalizes the result through the loader, computes descriptive summaries, and prints JSON.

### Summarize metric time series

```bash
uv tool run fulcra-analytics metrics HeartRate "1 day" --pretty
```

Use this when the Fulcra data type is best represented as a metric time series.

### Group summaries by a column

```bash
uv tool run fulcra-analytics records StepCount "1 week" --group-by source --pretty
```

The `groups` section includes row counts and numeric means for each group.

### Analyze a local export

```bash
uv tool run fulcra-analytics file ./exports/step-count.json --pretty
uv tool run fulcra-analytics file ./exports/annotations.jsonl --pretty
uv tool run fulcra-analytics file ./exports/calendar.csv --group-by calendarName --pretty
```

Use local exports for privacy-sensitive analysis, reproducible tests, or offline workflows.

### Inspect Fulcra catalog or user preferences

```bash
uv tool run fulcra-analytics catalog --base-types-only --pretty
uv tool run fulcra-analytics user-info --pretty
```

These are useful setup/debugging commands before choosing a data type or time range.

## Python API Recipes

### Load a local export

```python
from fulcra_analytics.loader import load_dataframe
from fulcra_analytics.statistics import summarize_dataframe

df = load_dataframe("exports/step-count.json")
summary = summarize_dataframe(df)
print(summary.to_dict())
```

### Fetch Fulcra records

```python
from fulcra_analytics import FulcraClient, summarize_dataframe

client = FulcraClient()
df = client.get_records_dataframe("StepCount", "1 week")
summary = summarize_dataframe(df, group_by="source")
```

### Fetch metric time series

```python
from fulcra_analytics import FulcraClient, summarize_dataframe

client = FulcraClient()
df = client.metric_time_series_dataframe("HeartRate", "1 day")
summary = summarize_dataframe(df)
```

## What the Statistics Include

`summary.to_dict()` returns JSON-friendly sections such as:

- `row_count` and `column_count`.
- `columns`.
- `missing` counts by column.
- `numeric` summaries: count, mean, std, min, max, sum, and quantiles.
- `datetime` summaries: count, min, max, and span in seconds.
- `categorical` summaries: count, unique count, and top values.
- `boolean` summaries: true/false counts and true fraction.
- `groups` when `group_by` is supplied.
- `metadata` describing source, data type, time range, or file path.

## OKF Report Pattern

When writing a Fulcra File Store report, use markdown with YAML frontmatter:

```markdown
---
type: Analytics Report
title: Step Count Summary
period: 1 week
privacy: summary-only
---

# Step Count Summary

## Question
What patterns are visible in StepCount records over the last week?

## Data Used
- Source: `StepCount`
- Range: `1 week`
- Raw records: local only; not uploaded

## Methods
- Fetched with `uv tool run fulcra-analytics records StepCount "1 week"`
- Normalized with `fulcra_analytics.loader`
- Summarized with `fulcra_analytics.statistics`

## Findings
- ...

## Caveats
- ...

## Next Steps
- ...
```

## Privacy Rules

- Treat health, location, calendar, and personal annotation data as sensitive.
- Do not upload raw records to shared team spaces unless the user explicitly authorizes it.
- Prefer aggregate JSON or OKF markdown summaries.
- Include a `Data Used` or `metadata` section so the user can audit the inputs.
- When collaborating with other agents, share links and summaries rather than raw private datasets.

## Common Pitfalls

1. **Uploading raw Fulcra data by default.**
   Keep raw exports local. Upload only sanitized reports or user-approved artifacts.

2. **Forgetting that Fulcra CLI time ranges are strings.**
   Quote ranges like `"1 week"`, `"30 days"`, or `"2026-06-01..2026-06-07"` when the shell would otherwise split them.

3. **Assuming every payload has the same shape.**
   Fulcra outputs and exports may wrap records in `records`, `data`, `items`, `results`, `samples`, or `values`. Use the loader rather than ad hoc parsing.

4. **Grouping by a missing column.**
   `--group-by` raises an error if the column does not exist. Inspect the `columns` section first or run without grouping.

5. **Treating summaries as causal conclusions.**
   Current statistics are descriptive. Avoid causal language unless the analysis explicitly supports it.

6. **Letting Rich wrap JSON output.**
   The CLI writes plain JSON to stdout intentionally, so downstream tools like `jq` or `python -m json.tool` can parse it.

## Verification Checklist

Before reporting success:

- [ ] The command or Python workflow executed successfully.
- [ ] Tests pass when modifying the package: `uv run --with pandas --with pytest --with typer --with rich python -m pytest tests -q`.
- [ ] Python files compile: `uv run --with pandas --with typer --with rich python -m py_compile src/fulcra_analytics/*.py`.
- [ ] CLI JSON parses: pipe output to `python3 -m json.tool` or `jq`.
- [ ] Raw data stayed local unless upload was explicitly authorized.
- [ ] Any Fulcra File Store output is OKF markdown and includes the data source, method, findings, caveats, and next steps.

## Further Reading

- `docs/architecture.md` — package architecture.
- `docs/client.md` — Fulcra CLI-backed client.
- `docs/loader.md` — record loading and normalization.
- `docs/statistics.md` — descriptive statistics behavior.
- `docs/cli.md` — command-line entrypoint.
