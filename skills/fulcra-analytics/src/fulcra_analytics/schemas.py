"""Shared schemas for Fulcra Analytics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DataSource:
    """Description of an input dataset."""

    path: str
    data_type: str | None = None
    time_range: str | None = None
    privacy: str = "local-raw"


@dataclass
class SummaryResult:
    """Small serializable summary object for early scaffold work."""

    row_count: int
    fields: list[str]
    numeric: dict[str, dict[str, float]] = field(default_factory=dict)
    missing: dict[str, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
