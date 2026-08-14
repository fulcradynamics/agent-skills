from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .jsonutil import compact_json


_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_KINDS = frozenset(("directive", "response"))
_PRIORITIES = frozenset(("P0", "P1", "P2", "P3"))


class State(str, Enum):
    DATA = "DATA"
    CLEAR = "CLEAR"
    UNKNOWN = "UNKNOWN"
    BACKLOG = "BACKLOG"
    STORE_ONLY = "STORE_ONLY"
    DURABLE_ONLY = "DURABLE_ONLY"


@dataclass(frozen=True)
class Event:
    workspace: str
    to: str
    kind: str
    priority: str
    slug: str
    ptr: str


@dataclass(frozen=True)
class Authority:
    data_type: str
    api_version: str
    protocol: int
    base_tag: str
    max_window_seconds: int
    max_records: int


@dataclass(frozen=True)
class Cursor:
    last_read: str
    seen: tuple[str, ...] = ()


@dataclass(frozen=True)
class Outcome:
    state: State
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    exit_code: int = 0

    def to_json(self) -> str:
        return compact_json({
            "type": "workspaces-result",
            "state": self.state.value,
            "message": self.message,
            "data": self.data,
        })


def parse_event(note: object) -> Event | None:
    if not isinstance(note, str) or not note.startswith("{"):
        return None
    try:
        payload = json.loads(note)
    except ValueError:
        return None
    if not isinstance(payload, dict) or payload.get("v") != 1:
        return None

    workspace = payload.get("workspace")
    recipient = payload.get("to")
    kind = payload.get("kind")
    priority = payload.get("pri")
    slug = payload.get("slug")
    ptr = payload.get("ptr")
    if not all(isinstance(value, str) and value for value in (
        workspace, recipient, kind, priority, slug, ptr
    )):
        return None
    if _NAME.fullmatch(workspace) is None or _NAME.fullmatch(recipient) is None:
        return None
    if _NAME.fullmatch(slug) is None:
        return None
    if kind not in _KINDS or priority not in _PRIORITIES:
        return None
    if not ptr.startswith(f"team/{workspace}/") or ".." in ptr.split("/"):
        return None
    return Event(
        workspace=workspace,
        to=recipient,
        kind=kind,
        priority=priority,
        slug=slug,
        ptr=ptr,
    )
