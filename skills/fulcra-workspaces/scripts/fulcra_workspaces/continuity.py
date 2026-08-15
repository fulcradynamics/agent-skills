from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from .jsonutil import compact_json
from .model import Outcome, State


_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_CHECKPOINT_SCHEMA = "fulcra.workspaces-checkpoint.v1"
_LATEST_SCHEMA = "fulcra.workspaces-continuity-latest.v1"
_ROLE_LATEST_SCHEMA = "fulcra.workspaces-role-continuity-latest.v1"
_LIST_FIELDS = (
    "decisions",
    "completed",
    "next_actions",
    "open_questions",
    "pointers",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _sha256(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def parse_checkpoint(raw: object) -> dict[str, Any] | None:
    try:
        doc = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("schema") != _CHECKPOINT_SCHEMA:
        return None
    if _UUID.fullmatch(str(doc.get("id") or "")) is None:
        return None
    if any(_NAME.fullmatch(str(doc.get(key) or "")) is None for key in (
        "workspace", "identity"
    )):
        return None
    role = doc.get("role")
    if role is not None and _NAME.fullmatch(str(role)) is None:
        return None
    if _parse_time(doc.get("timestamp")) is None:
        return None
    if not isinstance(doc.get("objective"), str) or not doc["objective"]:
        return None
    for key in _LIST_FIELDS:
        value = doc.get(key)
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            return None
    return doc


class ContinuityService:
    def __init__(self, transport: Any, *, role_service: Any | None = None):
        self.transport = transport
        self.role_service = role_service

    def checkpoint(
        self,
        workspace: str,
        identity: str,
        snapshot: dict[str, Any],
        *,
        checkpoint_id: str | None = None,
        timestamp: str | None = None,
        role: str | None = None,
        role_session_nonce: str | None = None,
        role_service: Any | None = None,
    ) -> Outcome:
        checkpoint_id = checkpoint_id or str(uuid.uuid4())
        timestamp = timestamp or _now()
        if role is not None:
            verifier = role_service or self.role_service
            if verifier is None:
                return Outcome(
                    State.UNKNOWN,
                    "role lease verifier is unavailable",
                    exit_code=3,
                )
            holder = verifier.verify_holder(
                workspace,
                role,
                identity,
                now=timestamp,
                session_nonce=role_session_nonce,
            )
            if holder.state is not State.DATA:
                return holder
        doc = {
            "schema": _CHECKPOINT_SCHEMA,
            "id": checkpoint_id,
            "workspace": workspace,
            "identity": identity,
            "role": role,
            "timestamp": timestamp,
            "objective": snapshot.get("objective"),
            **{key: snapshot.get(key) for key in _LIST_FIELDS},
        }
        rendered = compact_json(doc)
        if parse_checkpoint(rendered) is None:
            return Outcome(State.UNKNOWN, "checkpoint fields are invalid", exit_code=2)

        base = f"team/{workspace}/member/{identity}/continuity"
        ptr = f"{base}/checkpoint/{checkpoint_id}.json"
        existing, state = self.transport.read_file(ptr)
        if state == "ok" and existing != rendered:
            return Outcome(State.UNKNOWN, "checkpoint id collision", {"ptr": ptr}, 3)
        if state == "error":
            return Outcome(State.UNKNOWN, "checkpoint path is unreadable", exit_code=3)
        if state == "absent" and not self.transport.write_file(ptr, rendered):
            return Outcome(State.UNKNOWN, "checkpoint write failed", exit_code=3)
        readback, read_state = self.transport.read_file(ptr)
        if read_state != "ok" or readback != rendered:
            return Outcome(State.UNKNOWN, "checkpoint read-back mismatch", exit_code=3)

        latest_ptr = f"{base}/latest.json"
        latest = compact_json({
            "schema": _LATEST_SCHEMA,
            "workspace": workspace,
            "identity": identity,
            "timestamp": timestamp,
            "ptr": ptr,
            "sha256": _sha256(rendered),
        })
        if not self.transport.write_file(latest_ptr, latest):
            return Outcome(
                State.DURABLE_ONLY,
                "checkpoint is durable but latest projection failed",
                {"ptr": ptr},
                2,
            )
        latest_readback, latest_state = self.transport.read_file(latest_ptr)
        if latest_state != "ok" or latest_readback != latest:
            return Outcome(
                State.DURABLE_ONLY,
                "checkpoint is durable but latest projection mismatched",
                {"ptr": ptr},
                2,
            )
        if role is not None:
            role_latest_ptr = f"team/{workspace}/roles/{role}/continuity/latest.json"
            role_latest = compact_json({
                "schema": _ROLE_LATEST_SCHEMA,
                "workspace": workspace,
                "role": role,
                "identity": identity,
                "timestamp": timestamp,
                "ptr": ptr,
                "sha256": _sha256(rendered),
            })
            if not self.transport.write_file(role_latest_ptr, role_latest):
                return Outcome(
                    State.DURABLE_ONLY,
                    "checkpoint is durable but role projection failed",
                    {"ptr": ptr},
                    2,
                )
            role_readback, role_state = self.transport.read_file(role_latest_ptr)
            if role_state != "ok" or role_readback != role_latest:
                return Outcome(
                    State.DURABLE_ONLY,
                    "checkpoint is durable but role projection mismatched",
                    {"ptr": ptr},
                    2,
                )
        return Outcome(State.DATA, "checkpoint saved", {"ptr": ptr})

    def resume(
        self,
        workspace: str,
        identity: str,
        *,
        now: str,
        max_age_seconds: int,
        max_bytes: int,
    ) -> Outcome:
        if max_age_seconds <= 0 or max_bytes <= 0:
            return Outcome(State.UNKNOWN, "resume bounds must be positive", exit_code=2)
        now_dt = _parse_time(now)
        if now_dt is None:
            return Outcome(State.UNKNOWN, "resume time is invalid", exit_code=2)
        latest_ptr = f"team/{workspace}/member/{identity}/continuity/latest.json"
        latest_raw, state = self.transport.read_file(latest_ptr)
        if state != "ok":
            return Outcome(State.UNKNOWN, "latest continuity is unreadable", exit_code=3)
        try:
            latest = json.loads(latest_raw)
        except (TypeError, ValueError):
            return Outcome(State.UNKNOWN, "latest continuity is malformed", exit_code=3)
        if not isinstance(latest, dict) or latest.get("schema") != _LATEST_SCHEMA:
            return Outcome(State.UNKNOWN, "latest continuity has unknown schema", exit_code=3)
        ptr = latest.get("ptr")
        timestamp_dt = _parse_time(latest.get("timestamp"))
        if (
            latest.get("workspace") != workspace
            or latest.get("identity") != identity
            or not isinstance(ptr, str)
            or not ptr.startswith(f"team/{workspace}/member/{identity}/continuity/checkpoint/")
            or timestamp_dt is None
            or timestamp_dt > now_dt
            or (now_dt - timestamp_dt).total_seconds() > max_age_seconds
        ):
            return Outcome(State.UNKNOWN, "latest continuity is stale or conflicting", exit_code=3)
        checkpoint_raw, checkpoint_state = self.transport.read_file(ptr)
        if checkpoint_state != "ok" or not isinstance(checkpoint_raw, str):
            return Outcome(State.UNKNOWN, "checkpoint is unreadable", exit_code=3)
        if len(checkpoint_raw.encode("utf-8")) > max_bytes:
            return Outcome(State.UNKNOWN, "checkpoint exceeds resume byte bound", exit_code=3)
        checkpoint = parse_checkpoint(checkpoint_raw)
        if checkpoint is None or _sha256(checkpoint_raw) != latest.get("sha256"):
            return Outcome(State.UNKNOWN, "checkpoint failed verification", exit_code=3)
        return Outcome(State.DATA, "continuity resumed", {"checkpoint": checkpoint, "ptr": ptr})

    def resume_role(
        self,
        workspace: str,
        role: str,
        *,
        now: str,
        max_age_seconds: int,
        max_bytes: int,
    ) -> Outcome:
        if max_age_seconds <= 0 or max_bytes <= 0:
            return Outcome(State.UNKNOWN, "resume bounds must be positive", exit_code=2)
        now_dt = _parse_time(now)
        if now_dt is None or _NAME.fullmatch(role) is None:
            return Outcome(State.UNKNOWN, "role resume fields are invalid", exit_code=2)
        latest_ptr = f"team/{workspace}/roles/{role}/continuity/latest.json"
        latest_raw, state = self.transport.read_file(latest_ptr)
        if state != "ok":
            return Outcome(State.UNKNOWN, "latest role continuity is unreadable", exit_code=3)
        try:
            latest = json.loads(latest_raw)
        except (TypeError, ValueError):
            latest = None
        identity = latest.get("identity") if isinstance(latest, dict) else None
        ptr = latest.get("ptr") if isinstance(latest, dict) else None
        timestamp_dt = _parse_time(latest.get("timestamp")) if isinstance(latest, dict) else None
        if (
            not isinstance(latest, dict)
            or latest.get("schema") != _ROLE_LATEST_SCHEMA
            or latest.get("workspace") != workspace
            or latest.get("role") != role
            or not isinstance(identity, str)
            or _NAME.fullmatch(identity) is None
            or not isinstance(ptr, str)
            or not ptr.startswith(
                f"team/{workspace}/member/{identity}/continuity/checkpoint/"
            )
            or timestamp_dt is None
            or timestamp_dt > now_dt
            or (now_dt - timestamp_dt).total_seconds() > max_age_seconds
        ):
            return Outcome(State.UNKNOWN, "latest role continuity is stale or conflicting", exit_code=3)
        checkpoint_raw, checkpoint_state = self.transport.read_file(ptr)
        if checkpoint_state != "ok" or not isinstance(checkpoint_raw, str):
            return Outcome(State.UNKNOWN, "role checkpoint is unreadable", exit_code=3)
        if len(checkpoint_raw.encode("utf-8")) > max_bytes:
            return Outcome(State.UNKNOWN, "role checkpoint exceeds resume byte bound", exit_code=3)
        checkpoint = parse_checkpoint(checkpoint_raw)
        if (
            checkpoint is None
            or checkpoint.get("workspace") != workspace
            or checkpoint.get("identity") != identity
            or checkpoint.get("role") != role
            or _sha256(checkpoint_raw) != latest.get("sha256")
        ):
            return Outcome(State.UNKNOWN, "role checkpoint failed verification", exit_code=3)
        return Outcome(
            State.DATA,
            "role continuity resumed",
            {"checkpoint": checkpoint, "ptr": ptr},
        )
