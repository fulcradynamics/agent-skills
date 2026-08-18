"""One bounded cursor read over the workspace channel.

This is the whole discovery mechanism. An agent asks "anything new for me since
X?" and gets an answer in a fixed number of operations, whatever the history has
grown to. Nothing here interprets the work: events carry pointers, and the
pointed-at Store document remains authoritative and human-readable.

FAIL-CLOSED. Anything this cannot read or parse makes the whole read UNKNOWN,
never a shorter list. An empty inbox and an unreadable inbox must not render the
same — a partial answer that looks complete is the failure this exists to stop.
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .authority import AUTHORITY_PATH, parse_authority
from .jsonutil import compact_json
from .model import Authority, Cursor, Outcome, State, is_valid_name, parse_event

#: Re-read slightly before the cursor so an event written during the previous
#: read's round trip cannot fall between two windows. Duplicates are removed by
#: id; a gap could not be.
_OVERLAP_SECONDS = 120
_CURSOR_SCHEMA = "fulcra.workspaces-cursor.v1"

#: A rotated channel is invisible from the client side: the old data type keeps
#: answering, and it answers EMPTY. So a local authority is re-checked against
#: the durable one on a bounded schedule — whichever of these comes first.
#: Without it, Core Rule 4 ("an agent pointed at a stale channel sees an empty
#: inbox and cannot tell") describes this module instead of warning about it.
_AUTHORITY_CLEAR_LIMIT = 12
_AUTHORITY_MAX_AGE = timedelta(hours=6)


def _parse_time(value: object) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _render_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_local(path: Path, content: str) -> bool:
    """Atomic write. Returns False instead of raising: a cursor we could not
    persist means the next read must not believe this one advanced."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(path.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.replace(tmp, path)
    except OSError:
        return False
    return True


def _cursor_json(cursor: Cursor) -> str:
    return compact_json({
        "schema": _CURSOR_SCHEMA,
        "last_read": cursor.last_read,
        "seen": list(cursor.seen),
        "session_nonce": cursor.session_nonce,
        "authority_validated_at": cursor.authority_validated_at,
        "consecutive_clear": cursor.consecutive_clear,
    })


def _parse_cursor(raw: object) -> Cursor | None:
    """``None`` means UNREADABLE. The caller distinguishes that from absence."""
    if not isinstance(raw, str):
        return None
    try:
        payload = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(payload, dict) or payload.get("schema") != _CURSOR_SCHEMA:
        return None
    last_read = payload.get("last_read")
    if not isinstance(last_read, str) or _parse_time(last_read) is None:
        return None
    seen = payload.get("seen")
    if not isinstance(seen, list) or not all(isinstance(s, str) for s in seen):
        return None
    consecutive_clear = payload.get("consecutive_clear", 0)
    if not isinstance(consecutive_clear, int) or consecutive_clear < 0:
        return None
    # An absent validation stamp is not an error — it reads as "never
    # validated", which makes the next read revalidate rather than trust.
    validated_at = payload.get("authority_validated_at") or ""
    if not isinstance(validated_at, str):
        return None
    return Cursor(
        last_read=last_read,
        seen=tuple(seen),
        session_nonce=str(payload.get("session_nonce") or ""),
        authority_validated_at=validated_at,
        consecutive_clear=consecutive_clear,
    )


class QueueService:
    """The bounded read, and the cursor that bounds it."""

    def __init__(
        self,
        transport: Any,
        authority: Authority,
        identity: str,
        state_dir: Path,
        session_nonce: str | None = None,
    ):
        if not is_valid_name(identity):
            # The identity is a path segment AND the address events are matched
            # against. Refusing here makes the unsafe state unrepresentable
            # rather than validated at each of the places it is used.
            raise ValueError("identity is not a valid protocol name")
        self.transport = transport
        self.authority = authority
        self.identity = identity
        self.state_dir = Path(state_dir) / identity
        self.local_cursor_path = self.state_dir / "cursor.json"
        self.session_nonce = session_nonce or uuid.uuid4().hex

    def seed_cursor(self, at: str) -> bool:
        """Start reading from ``at``. Explicit, because guessing a start point
        either re-delivers history or silently skips it."""
        if _parse_time(at) is None:
            return False
        return _write_local(
            self.local_cursor_path,
            _cursor_json(Cursor(last_read=at, session_nonce=self.session_nonce)),
        )

    def _revalidate_authority(self, cursor: Cursor, now_dt: datetime) -> Cursor | None:
        """Re-check the local channel against the durable authority, on a
        schedule. ``None`` means the channel could not be CONFIRMED — which is
        UNKNOWN, never CLEAR, because an unconfirmed channel and an empty one
        are the same observation from here."""
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
            authority_validated_at=_render_time(now_dt),
            consecutive_clear=0,
        )
        # Persisting the stamp is an optimisation — it only defers the next
        # confirmation. If the write fails, say nothing about the channel: it
        # WAS confirmed, and reporting that as "could not confirm" would name a
        # conclusion where we have an observation. The read continues, and the
        # cursor write at the end is the one place persistence is reported.
        _write_local(self.local_cursor_path, _cursor_json(refreshed))
        return refreshed

    def _load_cursor(self) -> Cursor | None:
        try:
            raw = self.local_cursor_path.read_text(encoding="utf-8")
        except OSError:
            return None
        return _parse_cursor(raw)

    def read_queue(self, now: str) -> Outcome:
        """Everything addressed to this agent since the cursor, in one window."""
        now_dt = _parse_time(now)
        if now_dt is None:
            return Outcome(State.UNKNOWN, "read time is invalid", exit_code=3)

        cursor = self._load_cursor()
        if cursor is None:
            return Outcome(
                State.BACKLOG,
                "cursor is absent or unreadable; seed it before reading",
                exit_code=2,
            )
        cursor_dt = _parse_time(cursor.last_read)
        if cursor_dt is None:
            return Outcome(State.UNKNOWN, "cursor timestamp is invalid", exit_code=3)
        if now_dt < cursor_dt:
            return Outcome(State.UNKNOWN, "read time precedes the cursor", exit_code=3)
        if (now_dt - cursor_dt).total_seconds() > self.authority.max_window_seconds:
            # More history than one bounded read can answer. Say so rather than
            # returning the tail and letting it look like the whole answer.
            return Outcome(
                State.BACKLOG,
                "cursor is outside the bounded read horizon; re-seed",
                {"last_read": cursor.last_read, "now": now},
                2,
            )

        cursor = self._revalidate_authority(cursor, now_dt)
        if cursor is None:
            return Outcome(
                State.UNKNOWN,
                "the channel in use could not be confirmed against the durable "
                "authority; a rotated channel answers EMPTY, not an error",
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

        seen_order: list[str] = list(cursor.seen)
        seen = set(seen_order)
        events: list[dict[str, Any]] = []
        for row in sorted(rows, key=lambda r: str(r.get("recorded_at") or "")):
            record_id = row.get("id")
            event = parse_event(row.get("note"))
            if event is None or not isinstance(record_id, str) or not record_id:
                # One unreadable row poisons the window: it may be addressed to
                # us and we cannot tell, so "everything else" is not the answer.
                return Outcome(
                    State.UNKNOWN,
                    "a record in the window could not be parsed",
                    exit_code=3,
                )
            if record_id in seen:
                continue
            seen.add(record_id)
            seen_order.append(record_id)
            if event.to != self.identity:
                continue          # addressed elsewhere; counted as seen
            events.append({
                "id": record_id,
                "kind": event.kind,
                "pointer": event.ptr,
            })

        advanced = Cursor(
            last_read=now,
            # Keep the MOST RECENTLY OBSERVED ids. Sorting here would discard by
            # lexical value, so a fresh low-sorting id could be dropped and then
            # re-delivered by the next overlap window — the exact guarantee the
            # overlap exists to provide.
            seen=tuple(seen_order[-self.authority.max_records:]),
            session_nonce=self.session_nonce,
            authority_validated_at=cursor.authority_validated_at,
            # A run of clear reads is the signature of a rotated channel, so it
            # is also what schedules the next confirmation. Any delivery proves
            # the channel is live and resets the count.
            consecutive_clear=cursor.consecutive_clear + 1 if not events else 0,
        )
        if not _write_local(self.local_cursor_path, _cursor_json(advanced)):
            # Coverage is a fact about what this process READ. If we cannot
            # record it, we must not claim it; the next read repeats the window.
            return Outcome(
                State.UNKNOWN,
                "events were read but the cursor could not be persisted",
                {"events": events},
                3,
            )
        if not events:
            return Outcome(State.CLEAR, "no new events in the window")
        return Outcome(State.DATA, f"{len(events)} event(s)", {"events": events})
