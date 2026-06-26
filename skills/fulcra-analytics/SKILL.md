---
name: fulcra-analytics
description: Analyze Fulcra user data exports with privacy-respecting, reproducible Python data-science workflows and OKF-ready reports.
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

Use this skill when a user wants statistical analysis of Fulcra data such as calendar events, location visits, health metrics, annotations, activity records, or team/agent activity logs.

The skill emphasizes practical, privacy-respecting analysis: load data, normalize it into analysis-ready tables, compute descriptive statistics and trends, and write OKF-compatible markdown reports with links to any generated artifacts.

## Capabilities

- Load Fulcra CLI JSON output or exported JSON/JSONL/CSV files.
- Normalize common Fulcra record shapes into tabular data.
- Compute descriptive statistics, missingness, time ranges, grouping summaries, and simple trend features.
- Compare time windows such as week-over-week or month-over-month.
- Produce OKF markdown reports suitable for Fulcra File Store namespaces.
- Keep raw sensitive data local unless the user explicitly asks to upload it.

## Dependencies

The scaffolded Python package uses:

- `pandas`
- `numpy`
- `scipy`
- `pydantic`
- `python-dateutil`
- `typer`
- `rich`

Optional future visualization dependencies may include `matplotlib`, `seaborn`, or `plotly`.

## Default workflow

1. Clarify the analysis question and the data types involved.
2. Fetch or receive Fulcra data using `uv tool run fulcra-api ...` or local export files.
3. Store raw data locally; do not upload raw personal data unless explicitly authorized.
4. Normalize records into tables with `fulcra_analytics.loader`.
5. Run descriptive summaries with `fulcra_analytics.statistics`.
6. Write a concise OKF report in `analytics/<topic>.md` or a team artifact path.
7. Verify outputs exist and cite exact paths.

## Privacy rules

- Prefer summaries, aggregates, and links over raw records.
- Treat health, location, calendar, and personal annotations as sensitive.
- For shared team spaces, upload only sanitized reports or explicitly approved artifacts.
- Include a `Data Used` section in every report so users can audit inputs.

## Suggested report structure

```markdown
---
type: Analytics Report
title: <topic>
period: <time range>
privacy: summary-only
---

# <topic>

## Question
## Data Used
## Methods
## Findings
## Caveats
## Next Steps
```

## Scaffold status

This initial artifact is a project scaffold. It defines package layout, dependencies, core modules, and architecture, but does not yet implement every Fulcra data connector.
