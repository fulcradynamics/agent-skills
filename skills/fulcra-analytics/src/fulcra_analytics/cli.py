"""Command-line interface for Fulcra Analytics.

Examples:
    uv tool run fulcra-analytics records StepCount "1 week"
    uv tool run fulcra-analytics metrics HeartRate "1 day" --group-by source
    uv tool run fulcra-analytics file export.json --pretty
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

from .client import FulcraClient, FulcraClientError, default_client
from .loader import load_dataframe
from .statistics import summarize_dataframe

app = typer.Typer(help="Analyze Fulcra data from the Fulcra CLI or local exports.")
console = Console()
error_console = Console(stderr=True)


def _emit_json(payload: Any, *, pretty: bool = False) -> None:
    """Write a JSON payload to stdout without Rich wrapping."""

    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=pretty, default=str)
    print(text)


def _handle_error(exc: Exception) -> None:
    """Render a CLI error and exit with status 1."""

    error_console.print(f"[red]Error:[/red] {exc}")
    raise typer.Exit(code=1) from exc


@app.command("records")
def records_command(
    data_type: Annotated[str, typer.Argument(help="Fulcra data type, e.g. StepCount")],
    time_range: Annotated[str, typer.Argument(help='Range accepted by Fulcra CLI, e.g. "1 week"')],
    group_by: Annotated[
        str | None,
        typer.Option("--group-by", "-g", help="Optional column to group summary statistics by."),
    ] = None,
    pretty: Annotated[bool, typer.Option("--pretty", help="Pretty-print JSON output.")] = False,
) -> None:
    """Fetch records with Fulcra CLI and print descriptive statistics as JSON."""

    try:
        df = default_client().get_records_dataframe(data_type, time_range)
        summary = summarize_dataframe(
            df,
            group_by=group_by,
            metadata={"source": "get-records", "data_type": data_type, "time_range": time_range},
        )
        _emit_json(summary.to_dict(), pretty=pretty)
    except (FulcraClientError, KeyError, ValueError) as exc:
        _handle_error(exc)


@app.command("metrics")
def metrics_command(
    data_type: Annotated[str, typer.Argument(help="Fulcra metric data type, e.g. HeartRate")],
    time_range: Annotated[str, typer.Argument(help='Range accepted by Fulcra CLI, e.g. "1 day"')],
    group_by: Annotated[
        str | None,
        typer.Option("--group-by", "-g", help="Optional column to group summary statistics by."),
    ] = None,
    pretty: Annotated[bool, typer.Option("--pretty", help="Pretty-print JSON output.")] = False,
) -> None:
    """Fetch metric time-series data and print descriptive statistics as JSON."""

    try:
        df = default_client().metric_time_series_dataframe(data_type, time_range)
        summary = summarize_dataframe(
            df,
            group_by=group_by,
            metadata={"source": "metric-time-series", "data_type": data_type, "time_range": time_range},
        )
        _emit_json(summary.to_dict(), pretty=pretty)
    except (FulcraClientError, KeyError, ValueError) as exc:
        _handle_error(exc)


@app.command("file")
def file_command(
    path: Annotated[Path, typer.Argument(help="Local JSON, JSONL/NDJSON, or CSV export path.")],
    group_by: Annotated[
        str | None,
        typer.Option("--group-by", "-g", help="Optional column to group summary statistics by."),
    ] = None,
    pretty: Annotated[bool, typer.Option("--pretty", help="Pretty-print JSON output.")] = False,
) -> None:
    """Load a local export and print descriptive statistics as JSON."""

    try:
        df = load_dataframe(path)
        summary = summarize_dataframe(
            df,
            group_by=group_by,
            metadata={"source": "file", "path": str(path)},
        )
        _emit_json(summary.to_dict(), pretty=pretty)
    except (OSError, KeyError, ValueError) as exc:
        _handle_error(exc)


@app.command("catalog")
def catalog_command(
    base_types_only: Annotated[
        bool,
        typer.Option("--base-types-only", help="Return only base data types."),
    ] = False,
    pretty: Annotated[bool, typer.Option("--pretty", help="Pretty-print JSON output.")] = False,
) -> None:
    """Print Fulcra catalog JSON via the Fulcra client."""

    try:
        _emit_json(default_client().catalog(base_types_only=base_types_only), pretty=pretty)
    except FulcraClientError as exc:
        _handle_error(exc)


@app.command("user-info")
def user_info_command(
    pretty: Annotated[bool, typer.Option("--pretty", help="Pretty-print JSON output.")] = False,
) -> None:
    """Print authenticated Fulcra user info JSON."""

    try:
        _emit_json(default_client().user_info(), pretty=pretty)
    except FulcraClientError as exc:
        _handle_error(exc)


def main() -> None:
    """Run the Typer application."""

    app()


if __name__ == "__main__":
    main()
