"""Load and normalize Fulcra records into pandas DataFrames.

The loader accepts two sources:

1. Local exports: JSON, JSONL/NDJSON, and CSV files.
2. Fulcra CLI JSON output via ``uv tool run fulcra-api ...``.

Fulcra endpoints and exports can wrap records in several shapes, so this module
normalizes common containers such as ``records``, ``data``, ``items``, and
``results``. It also flattens nested dictionaries with dotted column names and
preserves list values unless they are lists of record dictionaries.
"""

from __future__ import annotations

import csv
import json
import subprocess
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import pandas as pd

_RECORD_KEYS = ("records", "data", "items", "results", "samples", "values", "rows")
_METADATA_KEYS = ("metadata", "meta", "pagination", "links")


class FulcraLoaderError(RuntimeError):
    """Raised when Fulcra records cannot be loaded or normalized."""


def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _flatten_dict(record: Mapping[str, Any], *, prefix: str = "", sep: str = ".") -> dict[str, Any]:
    """Flatten nested dictionaries while preserving arrays/lists as values."""

    flattened: dict[str, Any] = {}
    for key, value in record.items():
        name = f"{prefix}{sep}{key}" if prefix else str(key)
        if isinstance(value, Mapping):
            flattened.update(_flatten_dict(value, prefix=name, sep=sep))
        else:
            flattened[name] = value
    return flattened


def _coerce_record(item: Any) -> dict[str, Any]:
    if isinstance(item, Mapping):
        return _flatten_dict(item)
    return {"value": item}


def extract_records(payload: Any) -> list[dict[str, Any]]:
    """Extract records from common Fulcra JSON response shapes.

    Supported shapes include:

    - ``[{...}, {...}]``
    - ``{"records": [...]}``
    - ``{"data": [...]}``
    - ``{"items": [...]}``
    - ``{"results": [...]}``
    - single record dictionaries
    - scalar values, represented as ``{"value": scalar}``
    """

    if payload is None:
        return []

    if isinstance(payload, list):
        return [_coerce_record(item) for item in payload]

    if isinstance(payload, Mapping):
        for key in _RECORD_KEYS:
            value = payload.get(key)
            if isinstance(value, list):
                return [_coerce_record(item) for item in value]
            if isinstance(value, Mapping):
                return [_coerce_record(value)]

        # Some APIs return a dict keyed by record id. If every non-metadata value
        # is itself a record-like mapping, treat values as records and retain the
        # outer key as ``record_key`` when no id is present.
        candidate_items = [(k, v) for k, v in payload.items() if k not in _METADATA_KEYS]
        if candidate_items and all(isinstance(v, Mapping) for _, v in candidate_items):
            records = []
            for key, value in candidate_items:
                record = dict(value)
                record.setdefault("record_key", key)
                records.append(_coerce_record(record))
            return records

        return [_coerce_record(payload)]

    return [_coerce_record(payload)]


def records_to_dataframe(records: Iterable[Mapping[str, Any]]) -> pd.DataFrame:
    """Convert normalized records into a DataFrame with light type coercion."""

    df = pd.DataFrame(list(records))
    if df.empty:
        return df

    # Best-effort datetime coercion for obvious timestamp columns.
    for column in df.columns:
        lower = str(column).lower()
        if any(token in lower for token in ("time", "date", "timestamp", "created", "updated")):
            converted = pd.to_datetime(df[column], errors="coerce", utc=True)
            if converted.notna().any():
                df[column] = converted
    return df


def dataframe_from_payload(payload: Any) -> pd.DataFrame:
    """Extract records from a JSON-like payload and return a DataFrame."""

    return records_to_dataframe(extract_records(payload))


def load_records(path: str | Path) -> list[dict[str, Any]]:
    """Load normalized records from JSON, JSONL/NDJSON, or CSV.

    This preserves the original scaffold API by returning a list of dictionaries.
    Use ``load_dataframe`` for pandas output.
    """

    source = Path(path)
    suffix = source.suffix.lower()

    if suffix == ".json":
        payload = json.loads(source.read_text(encoding="utf-8"))
        return extract_records(payload)

    if suffix in {".jsonl", ".ndjson"}:
        records: list[dict[str, Any]] = []
        for line in source.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.extend(extract_records(json.loads(line)))
        return records

    if suffix == ".csv":
        with source.open("r", encoding="utf-8", newline="") as f:
            return [_coerce_record(row) for row in csv.DictReader(f)]

    raise FulcraLoaderError(f"Unsupported file type: {source}")


def load_dataframe(path: str | Path) -> pd.DataFrame:
    """Load a local export file into a normalized pandas DataFrame."""

    return records_to_dataframe(load_records(path))


def run_fulcra_cli(args: Sequence[str], *, timeout: int = 120) -> Any:
    """Run ``uv tool run fulcra-api`` and parse JSON stdout.

    Args:
        args: Fulcra CLI arguments after ``fulcra-api``. Example:
            ``["get-records", "StepCount", "1 week"]``.
        timeout: Subprocess timeout in seconds.

    Returns:
        Parsed JSON payload.
    """

    cmd = ["uv", "tool", "run", "fulcra-api", *args]
    result = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False)
    if result.returncode != 0:
        raise FulcraLoaderError(
            f"fulcra-api failed with exit code {result.returncode}: "
            f"{(result.stderr or result.stdout).strip()}"
        )
    stdout = result.stdout.strip()
    if not stdout:
        return []
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise FulcraLoaderError(f"fulcra-api did not return JSON: {stdout[:500]}") from exc


def dataframe_from_fulcra_cli(args: Sequence[str], *, timeout: int = 120) -> pd.DataFrame:
    """Run Fulcra CLI and normalize its JSON output into a DataFrame."""

    return dataframe_from_payload(run_fulcra_cli(args, timeout=timeout))


def get_records_dataframe(data_type: str, time_range: str, *, timeout: int = 120) -> pd.DataFrame:
    """Fetch ``get-records`` output for a Fulcra data type and return a DataFrame."""

    return dataframe_from_fulcra_cli(["get-records", data_type, time_range], timeout=timeout)


def metric_time_series_dataframe(data_type: str, time_range: str, *, timeout: int = 120) -> pd.DataFrame:
    """Fetch ``metric-time-series`` output for a Fulcra metric and return a DataFrame."""

    return dataframe_from_fulcra_cli(["metric-time-series", data_type, time_range], timeout=timeout)
