from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .jsonutil import compact_json
from .model import Outcome, State


_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_ROLE_SCHEMA = "fulcra.workspaces-role.v1"
_LEASE_SCHEMA = "fulcra.workspaces-role-lease.v1"
_LATEST_SCHEMA = "fulcra.workspaces-role-lease-latest.v1"
_POLICIES = frozenset(("exclusive", "shared"))
_LEASE_STATES = frozenset(("held", "released"))


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


def _render_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _valid_name(value: object) -> bool:
    return isinstance(value, str) and _NAME.fullmatch(value) is not None


def parse_role(raw: object) -> dict[str, Any] | None:
    try:
        doc = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("schema") != _ROLE_SCHEMA:
        return None
    if not _valid_name(doc.get("workspace")) or not _valid_name(doc.get("role")):
        return None
    if doc.get("policy") not in _POLICIES:
        return None
    if not isinstance(doc.get("lease_seconds"), int) or doc["lease_seconds"] <= 0:
        return None
    if not isinstance(doc.get("description"), str) or not doc["description"].strip():
        return None
    return doc


def parse_lease(raw: object) -> dict[str, Any] | None:
    try:
        doc = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("schema") != _LEASE_SCHEMA:
        return None
    if _UUID.fullmatch(str(doc.get("event_id") or "")) is None:
        return None
    if any(not _valid_name(doc.get(key)) for key in ("workspace", "role", "identity")):
        return None
    if doc.get("state") not in _LEASE_STATES:
        return None
    nonce = doc.get("session_nonce")
    if not isinstance(nonce, str) or not nonce:
        return None
    timestamp = _parse_time(doc.get("timestamp"))
    expires = _parse_time(doc.get("expires_at"))
    if timestamp is None or expires is None or expires < timestamp:
        return None
    return doc


class RoleService:
    def __init__(self, transport: Any, state_dir: Path, *, max_holders: int = 100):
        self.transport = transport
        self.state_dir = Path(state_dir)
        self.max_holders = max_holders

    def define(
        self,
        workspace: str,
        role: str,
        policy: str,
        lease_seconds: int,
        description: str,
    ) -> Outcome:
        doc = {
            "schema": _ROLE_SCHEMA,
            "workspace": workspace,
            "role": role,
            "policy": policy,
            "lease_seconds": lease_seconds,
            "description": description,
        }
        rendered = compact_json(doc)
        if parse_role(rendered) is None:
            return Outcome(State.UNKNOWN, "role definition fields are invalid", exit_code=2)
        ptr = self._definition_ptr(workspace, role)
        existing, state = self.transport.read_file(ptr)
        if state == "ok":
            if existing == rendered:
                return Outcome(State.DATA, "role definition is ready", {"ptr": ptr})
            return Outcome(State.UNKNOWN, "role definition conflicts with existing state", exit_code=3)
        if state != "absent":
            return Outcome(State.UNKNOWN, "role definition path is unreadable", exit_code=3)
        if not self.transport.write_file(ptr, rendered):
            return Outcome(State.UNKNOWN, "role definition write failed", exit_code=3)
        readback, read_state = self.transport.read_file(ptr)
        if read_state != "ok" or readback != rendered:
            return Outcome(State.UNKNOWN, "role definition read-back mismatch", exit_code=3)
        return Outcome(State.DATA, "role definition created", {"ptr": ptr})

    def claim(
        self,
        workspace: str,
        role: str,
        identity: str,
        *,
        now: str,
        event_id: str | None = None,
        session_nonce: str | None = None,
        takeover: bool = False,
    ) -> Outcome:
        definition, error = self._definition(workspace, role)
        if error is not None:
            return error
        now_dt = _parse_time(now)
        if now_dt is None or not _valid_name(identity):
            return Outcome(State.UNKNOWN, "claim fields are invalid", exit_code=2)
        nonce = self._nonce(workspace, role, identity, session_nonce)
        if nonce is None:
            return Outcome(State.UNKNOWN, "local role nonce is unreadable", exit_code=3)
        current, current_error = self._current(workspace, role, identity)
        if current_error is not None:
            return current_error
        if (
            current is not None
            and current["state"] == "held"
            and _parse_time(current["expires_at"]) > now_dt
            and current["session_nonce"] != nonce
            and not takeover
        ):
            return Outcome(
                State.UNKNOWN,
                "live role lease belongs to another session; explicit takeover required",
                exit_code=3,
            )
        expires_at = _render_time(now_dt + timedelta(seconds=definition["lease_seconds"]))
        outcome = self._transition(
            workspace, role, identity, "held", nonce, now, expires_at,
            event_id=event_id,
        )
        if outcome.state is State.DATA and not self._save_nonce(
            workspace, role, identity, nonce
        ):
            return Outcome(
                State.DURABLE_ONLY,
                "role lease is durable but local nonce could not be saved",
                outcome.data,
                2,
            )
        return outcome

    def release(
        self,
        workspace: str,
        role: str,
        identity: str,
        *,
        now: str,
        event_id: str | None = None,
        session_nonce: str | None = None,
    ) -> Outcome:
        _, error = self._definition(workspace, role)
        if error is not None:
            return error
        now_dt = _parse_time(now)
        if now_dt is None or not _valid_name(identity):
            return Outcome(State.UNKNOWN, "release fields are invalid", exit_code=2)
        nonce = self._nonce(workspace, role, identity, session_nonce, create=False)
        if nonce is None:
            return Outcome(State.UNKNOWN, "local role nonce is unavailable", exit_code=3)
        current, current_error = self._current(workspace, role, identity)
        if current_error is not None:
            return current_error
        if current is None or current["state"] == "released" or _parse_time(
            current["expires_at"]
        ) <= now_dt:
            return Outcome(
                State.CLEAR,
                "role lease is not held",
                {"status": "VACANT", "identity": identity},
            )
        if current["session_nonce"] != nonce:
            return Outcome(State.UNKNOWN, "live role lease belongs to another session", exit_code=3)
        outcome = self._transition(
            workspace, role, identity, "released", nonce, now, now,
            event_id=event_id,
        )
        if outcome.state is State.DATA:
            self._remove_nonce(workspace, role, identity)
        return outcome

    def status(self, workspace: str, role: str, *, now: str) -> Outcome:
        definition, error = self._definition(workspace, role)
        if error is not None:
            return error
        now_dt = _parse_time(now)
        if now_dt is None or self.max_holders <= 0:
            return Outcome(State.UNKNOWN, "role status bounds are invalid", exit_code=2)
        names, listing_state = self.transport.list_dir(
            f"team/{workspace}/roles/{role}/leases"
        )
        if (
            listing_state != "ok"
            or names is None
            or len(names) > self.max_holders
            or any(not _valid_name(name) for name in names)
        ):
            return Outcome(
                State.UNKNOWN,
                "role holder listing is unreadable or unbounded",
                exit_code=3,
            )
        holders = []
        for identity in sorted(set(names)):
            lease, lease_error = self._current(workspace, role, identity)
            if lease_error is not None or lease is None:
                return lease_error or Outcome(
                    State.UNKNOWN, "role holder projection is absent", exit_code=3
                )
            if lease["state"] == "held" and _parse_time(lease["expires_at"]) > now_dt:
                holders.append(identity)
        data = {"policy": definition["policy"], "holders": holders}
        if not holders:
            return Outcome(State.CLEAR, "role is vacant", {"status": "VACANT", **data})
        status = (
            "CONTESTED"
            if definition["policy"] == "exclusive" and len(holders) > 1
            else "HELD"
        )
        return Outcome(State.DATA, f"role is {status.lower()}", {"status": status, **data})

    def _definition(self, workspace: str, role: str) -> tuple[dict[str, Any] | None, Outcome | None]:
        if not _valid_name(workspace) or not _valid_name(role):
            return None, Outcome(State.UNKNOWN, "role path fields are invalid", exit_code=2)
        raw, state = self.transport.read_file(self._definition_ptr(workspace, role))
        definition = parse_role(raw) if state == "ok" else None
        if definition is None:
            return None, Outcome(State.UNKNOWN, "role definition is unreadable", exit_code=3)
        if definition["workspace"] != workspace or definition["role"] != role:
            return None, Outcome(State.UNKNOWN, "role definition conflicts with path", exit_code=3)
        return definition, None

    def _current(
        self, workspace: str, role: str, identity: str
    ) -> tuple[dict[str, Any] | None, Outcome | None]:
        latest_ptr = self._latest_ptr(workspace, role, identity)
        raw, state = self.transport.read_file(latest_ptr)
        if state == "absent":
            return None, None
        if state != "ok":
            return None, Outcome(State.UNKNOWN, "role lease projection is unreadable", exit_code=3)
        try:
            latest = json.loads(raw)
        except (TypeError, ValueError):
            latest = None
        prefix = f"team/{workspace}/roles/{role}/leases/{identity}/history/"
        if (
            not isinstance(latest, dict)
            or latest.get("schema") != _LATEST_SCHEMA
            or latest.get("workspace") != workspace
            or latest.get("role") != role
            or latest.get("identity") != identity
            or not isinstance(latest.get("ptr"), str)
            or not latest["ptr"].startswith(prefix)
            or not isinstance(latest.get("sha256"), str)
        ):
            return None, Outcome(State.UNKNOWN, "role lease projection is malformed", exit_code=3)
        lease_raw, lease_state = self.transport.read_file(latest["ptr"])
        lease = parse_lease(lease_raw) if lease_state == "ok" else None
        if (
            lease is None
            or _sha256(lease_raw) != latest["sha256"]
            or lease["workspace"] != workspace
            or lease["role"] != role
            or lease["identity"] != identity
        ):
            return None, Outcome(State.UNKNOWN, "role lease failed verification", exit_code=3)
        return lease, None

    def _transition(
        self,
        workspace: str,
        role: str,
        identity: str,
        state: str,
        nonce: str,
        timestamp: str,
        expires_at: str,
        *,
        event_id: str | None,
    ) -> Outcome:
        event_id = event_id or str(uuid.uuid4())
        doc = {
            "schema": _LEASE_SCHEMA,
            "event_id": event_id,
            "workspace": workspace,
            "role": role,
            "identity": identity,
            "state": state,
            "session_nonce": nonce,
            "timestamp": timestamp,
            "expires_at": expires_at,
        }
        rendered = compact_json(doc)
        if parse_lease(rendered) is None:
            return Outcome(State.UNKNOWN, "role lease fields are invalid", exit_code=2)
        base = f"team/{workspace}/roles/{role}/leases/{identity}"
        ptr = f"{base}/history/{event_id}.json"
        existing, existing_state = self.transport.read_file(ptr)
        if existing_state == "ok" and existing != rendered:
            return Outcome(State.UNKNOWN, "role lease event id collision", {"ptr": ptr}, 3)
        if existing_state == "error":
            return Outcome(State.UNKNOWN, "role lease event path is unreadable", exit_code=3)
        if existing_state == "absent" and not self.transport.write_file(ptr, rendered):
            return Outcome(State.UNKNOWN, "role lease event write failed", exit_code=3)
        readback, read_state = self.transport.read_file(ptr)
        if read_state != "ok" or readback != rendered:
            return Outcome(State.UNKNOWN, "role lease event read-back mismatch", exit_code=3)
        latest = compact_json({
            "schema": _LATEST_SCHEMA,
            "workspace": workspace,
            "role": role,
            "identity": identity,
            "ptr": ptr,
            "sha256": _sha256(rendered),
        })
        latest_ptr = f"{base}/latest.json"
        if not self.transport.write_file(latest_ptr, latest):
            return Outcome(
                State.DURABLE_ONLY,
                "role lease event is durable but projection failed",
                {"ptr": ptr},
                2,
            )
        latest_readback, latest_state = self.transport.read_file(latest_ptr)
        if latest_state != "ok" or latest_readback != latest:
            return Outcome(
                State.DURABLE_ONLY,
                "role lease event is durable but projection mismatched",
                {"ptr": ptr},
                2,
            )
        return Outcome(State.DATA, f"role lease {state}", {"ptr": ptr, "identity": identity})

    def _nonce(
        self,
        workspace: str,
        role: str,
        identity: str,
        supplied: str | None,
        *,
        create: bool = True,
    ) -> str | None:
        if supplied is not None:
            return supplied if supplied else None
        path = self._nonce_path(workspace, role, identity)
        try:
            existing = path.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            existing = ""
        except OSError:
            return None
        if existing:
            return existing
        return str(uuid.uuid4()) if create else None

    def _save_nonce(self, workspace: str, role: str, identity: str, nonce: str) -> bool:
        path = self._nonce_path(workspace, role, identity)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(nonce + "\n", encoding="utf-8")
        except OSError:
            return False
        return True

    def _remove_nonce(self, workspace: str, role: str, identity: str) -> None:
        try:
            self._nonce_path(workspace, role, identity).unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass

    def _nonce_path(self, workspace: str, role: str, identity: str) -> Path:
        return self.state_dir / "roles" / workspace / role / f"{identity}.nonce"

    @staticmethod
    def _definition_ptr(workspace: str, role: str) -> str:
        return f"team/{workspace}/roles/{role}/definition.json"

    @staticmethod
    def _latest_ptr(workspace: str, role: str, identity: str) -> str:
        return f"team/{workspace}/roles/{role}/leases/{identity}/latest.json"
