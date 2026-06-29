# fulcra-analytics

Initial Python scaffold for a Fulcra Agent Skill that parses and statistically analyzes Fulcra user data.

## Scope

The package currently includes:

- `fulcra_analytics.client`: a Fulcra CLI-backed API wrapper,
- `fulcra_analytics.loader`: JSON/JSONL/CSV and Fulcra payload normalization,
- `fulcra_analytics.statistics`: descriptive DataFrame summaries,
- `fulcra_analytics.cli`: a Typer command-line entrypoint.

## Quick start

```bash
uv venv
uv pip install -e '.[dev,viz]'
fulcra-analytics records StepCount "1 week" --pretty
```

You can also run the package entrypoint directly:

```bash
uv tool run fulcra-analytics records StepCount "1 week"
uv tool run fulcra-analytics metrics HeartRate "1 day"
uv tool run fulcra-analytics file path/to/export.json --pretty
```

## Privacy stance

Raw Fulcra records should remain local by default. Upload only summarized markdown reports or user-approved artifacts.
