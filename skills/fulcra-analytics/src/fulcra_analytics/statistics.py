"""Descriptive statistics helpers for normalized Fulcra records."""

from __future__ import annotations

from collections import defaultdict
from math import fsum
from typing import Any

from .schemas import SummaryResult


def _is_missing(value: Any) -> bool:
    return value is None or value == ""


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool) or _is_missing(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def summarize_records(records: list[dict[str, Any]]) -> SummaryResult:
    """Compute lightweight descriptive statistics for records.

    This deliberately avoids importing pandas so the scaffold can be smoke-tested
    before optional dependencies are installed. A later implementation can add a
    pandas-backed path for richer summaries.
    """

    fields = sorted({key for record in records for key in record.keys()})
    missing = {field: 0 for field in fields}
    numeric_values: dict[str, list[float]] = defaultdict(list)

    for record in records:
        for field in fields:
            value = record.get(field)
            if _is_missing(value):
                missing[field] += 1
            numeric = _as_float(value)
            if numeric is not None:
                numeric_values[field].append(numeric)

    numeric: dict[str, dict[str, float]] = {}
    for field, values in numeric_values.items():
        if not values:
            continue
        total = fsum(values)
        numeric[field] = {
            "count": float(len(values)),
            "min": min(values),
            "max": max(values),
            "mean": total / len(values),
        }

    return SummaryResult(
        row_count=len(records),
        fields=fields,
        numeric=numeric,
        missing=missing,
    )
