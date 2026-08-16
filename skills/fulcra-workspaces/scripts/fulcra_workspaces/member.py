from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from .jsonutil import compact_json
from .model import Authority, Outcome, State


_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_PROFILE_SCHEMA = "fulcra.workspaces-member.v1"
_LATEST_SCHEMA = "fulcra.workspaces-member-latest.v1"
_DIMENSIONS = frozenset(("machine", "cloud", "harness", "model"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_member(raw: object) -> dict[str, Any] | None:
    try:
        doc = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("schema") != _PROFILE_SCHEMA:
        return None
    if _UUID.fullmatch(str(doc.get("join_id") or "")) is None:
        return None
    if any(_NAME.fullmatch(str(doc.get(key) or "")) is None for key in (
        "workspace", "identity"
    )):
        return None
    dimensions = doc.get("dimensions")
    if not isinstance(dimensions, dict):
        return None
    if not set(dimensions).issubset(_DIMENSIONS):
        return None
    if any(not isinstance(value, str) or not value for value in dimensions.values()):
        return None
    if not isinstance(doc.get("timestamp"), str) or not doc["timestamp"]:
        return None
    moved_from = doc.get("moved_from")
    if moved_from is not None and not isinstance(moved_from, str):
        return None
    return doc


class MemberService:
    def __init__(self, transport: Any, authority: Authority):
        self.transport = transport
        self.authority = authority

    def join(
        self,
        workspace: str,
        identity: str,
        dimensions: dict[str, str],
        *,
        join_id: str | None = None,
        timestamp: str | None = None,
    ) -> Outcome:
        join_id = join_id or str(uuid.uuid4())
        timestamp = timestamp or _now()
        base = f"team/{workspace}/member/{identity}/profile"
        latest_ptr = f"{base}/latest.json"
        latest_raw, latest_state = self.transport.read_file(latest_ptr)
        moved_from = None
        if latest_state == "ok":
            try:
                latest = json.loads(latest_raw)
            except (TypeError, ValueError):
                return Outcome(State.UNKNOWN, "member latest profile is malformed", exit_code=3)
            if not isinstance(latest, dict) or latest.get("schema") != _LATEST_SCHEMA:
                return Outcome(State.UNKNOWN, "member latest profile has unknown schema", exit_code=3)
            previous_ptr = latest.get("ptr")
            previous_raw, previous_state = self.transport.read_file(previous_ptr)
            previous = parse_member(previous_raw) if previous_state == "ok" else None
            if previous is None:
                return Outcome(State.UNKNOWN, "previous member profile is unreadable", exit_code=3)
            if previous["dimensions"] != dimensions:
                moved_from = previous_ptr
        elif latest_state != "absent":
            return Outcome(State.UNKNOWN, "member profile state is unreadable", exit_code=3)

        profile = {
            "schema": _PROFILE_SCHEMA,
            "join_id": join_id,
            "workspace": workspace,
            "identity": identity,
            "dimensions": dimensions,
            "timestamp": timestamp,
            "moved_from": moved_from,
        }
        rendered = compact_json(profile)
        if parse_member(rendered) is None:
            return Outcome(State.UNKNOWN, "member profile fields are invalid", exit_code=2)
        ptr = f"{base}/history/{join_id}.json"
        existing, state = self.transport.read_file(ptr)
        if state == "ok" and existing != rendered:
            return Outcome(State.UNKNOWN, "member join id collision", exit_code=3)
        if state == "error":
            return Outcome(State.UNKNOWN, "member profile path is unreadable", exit_code=3)
        if state == "absent" and not self.transport.write_file(ptr, rendered):
            return Outcome(State.UNKNOWN, "member profile write failed", exit_code=3)
        readback, read_state = self.transport.read_file(ptr)
        if read_state != "ok" or readback != rendered:
            return Outcome(State.UNKNOWN, "member profile read-back mismatch", exit_code=3)

        latest_body = compact_json({
            "schema": _LATEST_SCHEMA,
            "workspace": workspace,
            "identity": identity,
            "ptr": ptr,
            "timestamp": timestamp,
        })
        if not self.transport.write_file(latest_ptr, latest_body):
            return Outcome(State.DURABLE_ONLY, "profile saved but latest projection failed", {"ptr": ptr}, 2)
        latest_readback, state = self.transport.read_file(latest_ptr)
        if state != "ok" or latest_readback != latest_body:
            return Outcome(State.DURABLE_ONLY, "profile saved but latest projection mismatched", {"ptr": ptr}, 2)

        note = compact_json({
            "v": 1,
            "workspace": workspace,
            "to": identity,
            "kind": "directive",
            "pri": "P2",
            "slug": "identity-joined",
            "ptr": ptr,
        })
        data = {"ptr": ptr, "moved": moved_from is not None}
        if not self.transport.record_write(
            self.authority.data_type,
            self.authority.api_version,
            note,
            identity,
            tags=(self.authority.base_tag,),
        ):
            return Outcome(State.DURABLE_ONLY, "profile is durable but Bus announcement failed", data, 2)
        return Outcome(State.DATA, "workspace identity joined", data)
