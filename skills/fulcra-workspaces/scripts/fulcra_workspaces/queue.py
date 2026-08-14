from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .jsonutil import compact_json
from .authority import AUTHORITY_PATH, parse_authority
from .model import Authority, Cursor, Outcome, State, parse_event
from .store import parse_message


_OVERLAP_SECONDS = 120
_RECEIPT_SCHEMA = "fulcra.workspaces-receipt.v1"
_INBOX_SCHEMA = "fulcra.workspaces-inbox-pointer.v1"
_CURSOR_SCHEMA = "fulcra.workspaces-cursor.v1"
_COLLISION_SCHEMA = "fulcra.workspaces-collision.v1"
_AUTHORITY_CLEAR_LIMIT = 12
_AUTHORITY_MAX_AGE = timedelta(hours=6)


def _parse_time(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _render_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_local(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    staged: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            handle.write(content)
            staged = handle.name
        os.replace(staged, path)
        return True
    except OSError:
        return False
    finally:
        if staged is not None and os.path.exists(staged):
            try:
                os.unlink(staged)
            except OSError:
                pass


def _cursor_json(cursor: Cursor) -> str:
    return compact_json({
        "schema": _CURSOR_SCHEMA,
        "last_read": cursor.last_read,
        "seen": list(cursor.seen),
        "session_nonce": cursor.session_nonce,
        "observed_mirror_nonce": cursor.observed_mirror_nonce,
        "authority_validated_at": cursor.authority_validated_at,
        "consecutive_clear": cursor.consecutive_clear,
    })


def _parse_cursor(raw: object) -> Cursor | None:
    try:
        doc = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(doc, dict) or doc.get("schema") != _CURSOR_SCHEMA:
        return None
    last_read = doc.get("last_read")
    seen = doc.get("seen")
    session_nonce = doc.get("session_nonce", "")
    observed_mirror_nonce = doc.get("observed_mirror_nonce")
    authority_validated_at = doc.get("authority_validated_at") or last_read
    consecutive_clear = doc.get("consecutive_clear", 0)
    if _parse_time(last_read) is None or not isinstance(seen, list):
        return None
    if any(not isinstance(item, str) or not item for item in seen):
        return None
    if not isinstance(session_nonce, str):
        return None
    if observed_mirror_nonce is not None and not isinstance(observed_mirror_nonce, str):
        return None
    if _parse_time(authority_validated_at) is None:
        return None
    if not isinstance(consecutive_clear, int) or consecutive_clear < 0:
        return None
    return Cursor(
        last_read=last_read,
        seen=tuple(seen),
        session_nonce=session_nonce,
        observed_mirror_nonce=observed_mirror_nonce,
        authority_validated_at=authority_validated_at,
        consecutive_clear=consecutive_clear,
    )


class QueueService:
    def __init__(
        self,
        transport: Any,
        authority: Authority,
        identity: str,
        state_dir: Path,
        session_nonce: str | None = None,
    ):
        self.transport = transport
        self.authority = authority
        self.identity = identity
        self.state_dir = state_dir / identity
        self.local_cursor_path = self.state_dir / "cursor.json"
        self.pending_path = self.state_dir / "pending.json"
        self.session_nonce_path = self.state_dir / "session-nonce"
        self.session_nonce = session_nonce or self._load_or_create_session_nonce()

    @property
    def durable_cursor_path(self) -> str:
        return f"_workspaces/member/{self.identity}/cursor.json"

    @property
    def collision_path(self) -> str:
        return f"_workspaces/member/{self.identity}/collision.json"

    def _load_or_create_session_nonce(self) -> str:
        try:
            value = self.session_nonce_path.read_text().strip()
            if value:
                return value
        except OSError:
            pass
        value = str(uuid.uuid4())
        if not _write_local(self.session_nonce_path, value + "\n"):
            return value
        return value

    def seed_cursor(self, at: str) -> bool:
        if _parse_time(at) is None:
            return False
        return _write_local(self.local_cursor_path, _cursor_json(Cursor(
            last_read=at,
            session_nonce=self.session_nonce,
            authority_validated_at=at,
        )))

    def _load_cursor(self) -> Cursor | None:
        try:
            local_raw = self.local_cursor_path.read_text()
        except OSError:
            durable_raw, state = self.transport.read_file(self.durable_cursor_path)
            if state != "ok":
                return None
            durable = _parse_cursor(durable_raw)
            if durable is None:
                return None
            restored = Cursor(
                last_read=durable.last_read,
                seen=durable.seen,
                session_nonce=self.session_nonce,
                observed_mirror_nonce=durable.session_nonce or None,
                authority_validated_at=durable.authority_validated_at,
                consecutive_clear=durable.consecutive_clear,
            )
            if not _write_local(
                self.local_cursor_path, _cursor_json(restored)
            ):
                return None
            return restored
        local = _parse_cursor(local_raw)
        if local is None:
            return None
        if local.session_nonce == self.session_nonce:
            return local
        adopted = Cursor(
            last_read=local.last_read,
            seen=local.seen,
            session_nonce=self.session_nonce,
            observed_mirror_nonce=local.observed_mirror_nonce,
            authority_validated_at=local.authority_validated_at,
            consecutive_clear=local.consecutive_clear,
        )
        if not _write_local(self.local_cursor_path, _cursor_json(adopted)):
            return None
        return adopted

    def _revalidate_authority(self, cursor: Cursor, now_dt: datetime) -> Cursor | None:
        validated_dt = _parse_time(cursor.authority_validated_at)
        due = (
            cursor.consecutive_clear >= _AUTHORITY_CLEAR_LIMIT - 1
            or validated_dt is None
            or now_dt - validated_dt >= _AUTHORITY_MAX_AGE
        )
        if not due:
            return cursor
        raw, state = self.transport.read_file(AUTHORITY_PATH)
        if state != "ok" or parse_authority(raw) != self.authority:
            return None
        refreshed = Cursor(
            last_read=cursor.last_read,
            seen=cursor.seen,
            session_nonce=self.session_nonce,
            observed_mirror_nonce=cursor.observed_mirror_nonce,
            authority_validated_at=_render_time(now_dt),
            consecutive_clear=0,
        )
        if not _write_local(self.local_cursor_path, _cursor_json(refreshed)):
            return None
        return refreshed

    def _record_collision(
        self,
        expected: Cursor,
        observed: Cursor | None,
        detected_at: str,
    ) -> bool:
        body = compact_json({
            "schema": _COLLISION_SCHEMA,
            "identity": self.identity,
            "detected_at": detected_at,
            "session_nonce": self.session_nonce,
            "expected_mirror_nonce": expected.observed_mirror_nonce,
            "expected_last_read": expected.last_read,
            "observed_mirror_nonce": observed.session_nonce if observed else None,
            "observed_last_read": observed.last_read if observed else None,
        })
        existing, state = self.transport.read_file(self.collision_path)
        if state == "ok":
            return True
        if state != "absent" or not self.transport.write_file(self.collision_path, body):
            return False
        readback, read_state = self.transport.read_file(self.collision_path)
        return read_state == "ok" and readback == body

    def _load_pending(self) -> dict[str, Any] | None:
        try:
            raw = json.loads(self.pending_path.read_text())
        except (OSError, ValueError):
            return None
        if not isinstance(raw, dict) or not isinstance(raw.get("events"), list):
            return None
        if not isinstance(raw.get("until"), str):
            return None
        return raw

    def _save_pending(self, pending: dict[str, Any]) -> bool:
        return _write_local(self.pending_path, compact_json(pending))

    def _receipt_path(self, workspace: str, message_id: str) -> str:
        return (
            f"team/{workspace}/member/{self.identity}/receipt/"
            f"{message_id}.json"
        )

    def read_queue(self, now: str) -> Outcome:
        pending = self._load_pending()
        if pending is not None and pending["events"]:
            return Outcome(
                State.DATA,
                "pending batch replayed without another remote query",
                {"events": pending["events"]},
            )

        cursor = self._load_cursor()
        now_dt = _parse_time(now)
        if cursor is None or now_dt is None:
            return Outcome(
                State.BACKLOG if cursor is None else State.UNKNOWN,
                "cursor is absent or invalid; seed or restore before reading",
                exit_code=2,
            )
        cursor_dt = _parse_time(cursor.last_read)
        if cursor_dt is None:
            return Outcome(State.UNKNOWN, "cursor timestamp is invalid", exit_code=3)
        if now_dt < cursor_dt:
            return Outcome(State.UNKNOWN, "queue time precedes cursor", exit_code=3)
        if (now_dt - cursor_dt).total_seconds() > self.authority.max_window_seconds:
            return Outcome(
                State.BACKLOG,
                "cursor is outside the bounded read horizon",
                {"last_read": cursor.last_read, "now": now},
                2,
            )

        cursor = self._revalidate_authority(cursor, now_dt)
        if cursor is None:
            return Outcome(
                State.UNKNOWN,
                "durable Bus authority is unreadable or differs from local authority",
                exit_code=3,
            )

        since = _render_time(cursor_dt - timedelta(seconds=_OVERLAP_SECONDS))
        rows = self.transport.records(
            self.authority.data_type,
            since,
            now,
            max_records=self.authority.max_records,
        )
        if rows is None:
            return Outcome(State.UNKNOWN, "record window is unreadable", exit_code=3)

        selected: list[dict[str, Any]] = []
        seen_ids = set(cursor.seen)
        for row in sorted(
            rows,
            key=lambda item: (str(item.get("recorded_at") or ""), str(item.get("id") or "")),
        ):
            note = row.get("note") if isinstance(row, dict) else None
            parsed = parse_event(note)
            if parsed is None:
                if isinstance(note, str) and note.startswith("{"):
                    try:
                        looks_control = json.loads(note).get("v") == 1
                    except (ValueError, AttributeError):
                        looks_control = False
                    if looks_control:
                        return Outcome(
                            State.UNKNOWN,
                            "malformed schema-v1 control event",
                            exit_code=3,
                        )
                continue
            record_id = row.get("id")
            if not isinstance(record_id, str) or not record_id:
                return Outcome(State.UNKNOWN, "event lacks stable record id", exit_code=3)
            if record_id in seen_ids or parsed.to not in (self.identity, "all"):
                continue
            message_id = parsed.ptr.rsplit("/", 1)[-1].removesuffix(".md")
            receipt_path = self._receipt_path(parsed.workspace, message_id)
            receipt, receipt_state = self.transport.read_file(receipt_path)
            if receipt_state == "error":
                return Outcome(State.UNKNOWN, "receipt state is unreadable", exit_code=3)
            if receipt_state == "ok":
                seen_ids.add(record_id)
                continue
            body, body_state = self.transport.read_file(parsed.ptr)
            if body_state != "ok" or parse_message(body) is None:
                return Outcome(
                    State.UNKNOWN,
                    f"pointed document is {body_state} or invalid",
                    {"ptr": parsed.ptr},
                    3,
                )
            selected.append({
                "record_id": record_id,
                "recorded_at": row["recorded_at"],
                "sender": next(iter(row.get("sources") or []), None),
                "workspace": parsed.workspace,
                "to": parsed.to,
                "kind": parsed.kind,
                "priority": parsed.priority,
                "slug": parsed.slug,
                "ptr": parsed.ptr,
                "message_id": message_id,
                "body": body,
            })

        if selected:
            active = Cursor(
                last_read=cursor.last_read,
                seen=cursor.seen,
                session_nonce=self.session_nonce,
                observed_mirror_nonce=cursor.observed_mirror_nonce,
                authority_validated_at=cursor.authority_validated_at,
                consecutive_clear=0,
            )
            if not _write_local(self.local_cursor_path, _cursor_json(active)):
                return Outcome(State.UNKNOWN, "local cursor write failed", exit_code=3)
            pending_doc = {"until": now, "events": selected}
            if not self._save_pending(pending_doc):
                return Outcome(State.UNKNOWN, "pending batch could not be staged", exit_code=3)
            return Outcome(State.DATA, f"{len(selected)} event(s)", {"events": selected})

        advanced = Cursor(
            last_read=now,
            seen=tuple(sorted(seen_ids)[-1000:]),
            session_nonce=self.session_nonce,
            observed_mirror_nonce=cursor.observed_mirror_nonce,
            authority_validated_at=cursor.authority_validated_at,
            consecutive_clear=cursor.consecutive_clear + 1,
        )
        if not _write_local(self.local_cursor_path, _cursor_json(advanced)):
            return Outcome(State.UNKNOWN, "local cursor write failed", exit_code=3)
        return Outcome(State.CLEAR, "bounded queue read is clear")

    def complete(self, record_id: str, result: str) -> Outcome:
        pending = self._load_pending()
        if pending is None:
            return Outcome(State.UNKNOWN, "no staged batch", exit_code=2)
        event = next(
            (item for item in pending["events"] if item.get("record_id") == record_id),
            None,
        )
        if event is None:
            return Outcome(State.UNKNOWN, "record is not in the staged batch", exit_code=2)
        receipt_path = self._receipt_path(event["workspace"], event["message_id"])
        receipt_body = compact_json({
            "schema": _RECEIPT_SCHEMA,
            "message_id": event["message_id"],
            "record_id": record_id,
            "recipient": self.identity,
            "workspace": event["workspace"],
            "outcome": result,
        })
        existing, state = self.transport.read_file(receipt_path)
        if state == "error" or (state == "ok" and existing != receipt_body):
            return Outcome(State.UNKNOWN, "receipt path is unreadable or conflicting", exit_code=3)
        if state == "absent" and not self.transport.write_file(receipt_path, receipt_body):
            return Outcome(State.UNKNOWN, "receipt write failed", exit_code=3)
        readback, read_state = self.transport.read_file(receipt_path)
        if read_state != "ok" or readback != receipt_body:
            return Outcome(State.UNKNOWN, "receipt read-back mismatch", exit_code=3)

        remaining = [
            item for item in pending["events"] if item.get("record_id") != record_id
        ]
        if remaining:
            pending["events"] = remaining
            if not self._save_pending(pending):
                return Outcome(State.UNKNOWN, "pending batch update failed", exit_code=3)
            return Outcome(State.DATA, "event completed; batch still has work")

        cursor = self._load_cursor()
        if cursor is None:
            return Outcome(State.UNKNOWN, "cursor became unreadable", exit_code=3)
        collision, collision_state = self.transport.read_file(self.collision_path)
        if collision_state == "ok":
            return Outcome(State.UNKNOWN, "identity has unresolved collision evidence", exit_code=3)
        if collision_state == "error":
            return Outcome(State.UNKNOWN, "identity collision state is unreadable", exit_code=3)
        mirror_raw, mirror_state = self.transport.read_file(self.durable_cursor_path)
        mirror = _parse_cursor(mirror_raw) if mirror_state == "ok" else None
        mirror_nonce = mirror.session_nonce if mirror is not None else None
        if (
            mirror_state not in ("ok", "absent")
            or (mirror_state == "ok" and mirror is None)
            or mirror_nonce != cursor.observed_mirror_nonce
            or (mirror is not None and mirror.last_read != cursor.last_read)
        ):
            self._record_collision(cursor, mirror, pending["until"])
            return Outcome(
                State.UNKNOWN,
                "another session advanced this identity; collision recorded",
                exit_code=3,
            )
        seen = tuple(sorted(set(cursor.seen) | {
            item["record_id"] for item in pending["events"]
        })[-1000:])
        advanced = Cursor(
            last_read=pending["until"],
            seen=seen,
            session_nonce=self.session_nonce,
            observed_mirror_nonce=self.session_nonce,
            authority_validated_at=cursor.authority_validated_at,
            consecutive_clear=0,
        )
        rendered = _cursor_json(advanced)
        if not self.transport.write_file(self.durable_cursor_path, rendered):
            return Outcome(State.UNKNOWN, "durable cursor mirror write failed", exit_code=3)
        mirror, mirror_state = self.transport.read_file(self.durable_cursor_path)
        if mirror_state != "ok" or mirror != rendered:
            self._record_collision(cursor, _parse_cursor(mirror), pending["until"])
            return Outcome(
                State.UNKNOWN,
                "durable cursor mirror mismatch; collision recorded",
                exit_code=3,
            )
        if not _write_local(self.local_cursor_path, rendered):
            return Outcome(State.UNKNOWN, "local cursor write failed", exit_code=3)
        try:
            self.pending_path.unlink()
        except OSError:
            return Outcome(State.UNKNOWN, "completed batch could not be cleared", exit_code=3)
        return Outcome(State.DATA, "event completed and coverage advanced")

    def repair(self, workspace: str, *, limit: int) -> Outcome:
        if limit <= 0:
            return Outcome(State.UNKNOWN, "repair limit must be positive", exit_code=2)
        prefix = f"team/{workspace}/member/{self.identity}/inbox/"
        names, state = self.transport.list_dir(prefix)
        if state != "ok" or names is None:
            return Outcome(State.UNKNOWN, "recipient inbox listing is unreadable", exit_code=3)
        messages = []
        for name in names:
            if len(messages) >= limit:
                break
            if "/" in name or not name.endswith(".json"):
                return Outcome(State.UNKNOWN, "recipient inbox entry is malformed", exit_code=3)
            index_raw, index_state = self.transport.read_file(prefix + name)
            if index_state != "ok":
                return Outcome(State.UNKNOWN, "recipient index is unreadable", exit_code=3)
            try:
                index = json.loads(index_raw)
            except (TypeError, ValueError):
                return Outcome(State.UNKNOWN, "recipient index is malformed", exit_code=3)
            if not isinstance(index, dict) or index.get("schema") != _INBOX_SCHEMA:
                return Outcome(State.UNKNOWN, "recipient index has unknown schema", exit_code=3)
            message_id = index.get("id")
            if (
                index.get("workspace") != workspace
                or index.get("recipient") != self.identity
                or not isinstance(message_id, str)
            ):
                return Outcome(State.UNKNOWN, "recipient index fields conflict", exit_code=3)
            receipt_path = self._receipt_path(workspace, message_id)
            _, receipt_state = self.transport.read_file(receipt_path)
            if receipt_state == "error":
                return Outcome(State.UNKNOWN, "receipt state is unreadable", exit_code=3)
            if receipt_state == "ok":
                continue
            body, body_state = self.transport.read_file(index.get("ptr"))
            message = parse_message(body) if body_state == "ok" else None
            if message is None or message.sha256 != index.get("sha256"):
                return Outcome(State.UNKNOWN, "indexed message failed verification", exit_code=3)
            messages.append({
                "message_id": message_id,
                "ptr": index["ptr"],
                "body": body,
            })
        if not messages:
            return Outcome(State.CLEAR, "bounded repair found no unreceipted messages")
        return Outcome(State.DATA, f"{len(messages)} repair item(s)", {"messages": messages})
