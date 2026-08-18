"""The bounded read, and every way it must refuse to answer.

The point of these is not that the happy path works — it is that a read which
could not see everything never renders as a read that saw nothing. An empty
inbox and an unreadable inbox must be distinguishable at every failure.
"""

import json
from pathlib import Path

from fulcra_workspaces.model import Authority, State
from fulcra_workspaces.queue import QueueService

AUTHORITY = Authority(
    data_type="Workspace/abc",
    api_version="v1alpha1",
    protocol=1,
    base_tag="ws",
    max_window_seconds=3600,
    max_records=50,
)


class FakeTransport:
    """Returns a fixed window. ``None`` is the unreadable case, which is the
    one that matters: the real client cannot distinguish empty from failed, so
    it returns None and the caller must not guess."""

    def __init__(self, rows):
        self.rows = rows
        self.calls = 0

    def records(self, data_type, since, until, max_records=None):
        self.calls += 1
        return self.rows


def event(record_id, *, to="alice", kind="directive", ptr="team/ws/p.md", at="2026-01-01T00:00:10Z"):
    return {
        "record_id": record_id,
        "recorded_at": at,
        "note": json.dumps({
            "v": 1, "workspace": "ws", "to": to, "kind": kind,
            "pri": "P2", "slug": "s", "ptr": ptr,
        }),
    }


def svc(tmp_path: Path, rows):
    return QueueService(FakeTransport(rows), AUTHORITY, "alice", tmp_path)


# --- the read itself ---------------------------------------------------------

def test_a_seeded_cursor_reads_the_window_and_returns_its_events(tmp_path):
    q = svc(tmp_path, [event("r1"), event("r2")])
    assert q.seed_cursor("2026-01-01T00:00:00Z")
    out = q.read_queue("2026-01-01T00:01:00Z")
    assert out.state is State.DATA
    assert [e["id"] for e in out.data["events"]] == ["r1", "r2"]


def test_an_empty_window_is_CLEAR_and_says_so(tmp_path):
    q = svc(tmp_path, [])
    q.seed_cursor("2026-01-01T00:00:00Z")
    out = q.read_queue("2026-01-01T00:01:00Z")
    assert out.state is State.CLEAR and out.exit_code == 0


def test_an_event_already_seen_is_not_delivered_twice(tmp_path):
    q = svc(tmp_path, [event("r1")])
    q.seed_cursor("2026-01-01T00:00:00Z")
    assert q.read_queue("2026-01-01T00:01:00Z").state is State.DATA
    # Same row still inside the overlap window on the next read.
    assert q.read_queue("2026-01-01T00:02:00Z").state is State.CLEAR


def test_the_window_reaches_BACK_past_the_cursor_so_nothing_falls_between_reads(tmp_path):
    """An event written during the previous read's round trip must still be
    caught. Duplicates are removed by id; a gap could not be."""
    seen = {}

    class Recording(FakeTransport):
        def records(self, data_type, since, until, max_records=None):
            seen["since"] = since
            return []

    q = QueueService(Recording([]), AUTHORITY, "alice", tmp_path)
    q.seed_cursor("2026-01-01T01:00:00Z")
    q.read_queue("2026-01-01T01:00:30Z")
    assert seen["since"] < "2026-01-01T01:00:00Z", (
        f"the window started at or after the cursor: {seen['since']}")


# --- every refusal -----------------------------------------------------------

def test_an_UNREADABLE_window_is_UNKNOWN_never_CLEAR(tmp_path):
    """THE regression this protocol exists for: a failed read must not render
    as an empty inbox."""
    q = svc(tmp_path, None)
    q.seed_cursor("2026-01-01T00:00:00Z")
    out = q.read_queue("2026-01-01T00:01:00Z")
    assert out.state is State.UNKNOWN and out.exit_code == 3


def test_ONE_unparseable_row_poisons_the_whole_window(tmp_path):
    """It may be addressed to us and we cannot tell, so 'everything else' is
    not the answer — a shorter list that looks complete is the failure."""
    q = svc(tmp_path, [event("r1"), {"record_id": "bad", "note": "not json"}])
    q.seed_cursor("2026-01-01T00:00:00Z")
    out = q.read_queue("2026-01-01T00:01:00Z")
    assert out.state is State.UNKNOWN
    assert "could not be parsed" in out.message


def test_an_ABSENT_cursor_is_BACKLOG_not_an_empty_read(tmp_path):
    q = svc(tmp_path, [event("r1")])
    out = q.read_queue("2026-01-01T00:01:00Z")
    assert out.state is State.BACKLOG and out.exit_code == 2


def test_an_UNREADABLE_cursor_is_also_BACKLOG_not_a_fresh_start(tmp_path):
    """Silently re-seeding would skip everything written before now."""
    q = svc(tmp_path, [event("r1")])
    q.local_cursor_path.parent.mkdir(parents=True, exist_ok=True)
    q.local_cursor_path.write_text("{ not json", encoding="utf-8")
    assert q.read_queue("2026-01-01T00:01:00Z").state is State.BACKLOG


def test_a_cursor_older_than_the_horizon_is_BACKLOG_not_a_partial_answer(tmp_path):
    """More history than one bounded read can answer. Say so rather than
    returning the tail and letting it look like the whole answer."""
    q = svc(tmp_path, [event("r1")])
    q.seed_cursor("2026-01-01T00:00:00Z")
    out = q.read_queue("2026-01-01T09:00:00Z")     # > max_window_seconds
    assert out.state is State.BACKLOG and out.exit_code == 2
    assert q.transport.calls == 0, "it queried the store despite refusing to answer"


def test_a_read_time_BEFORE_the_cursor_is_UNKNOWN(tmp_path):
    q = svc(tmp_path, [])
    q.seed_cursor("2026-01-01T01:00:00Z")
    assert q.read_queue("2026-01-01T00:00:00Z").state is State.UNKNOWN


def test_an_invalid_read_time_is_UNKNOWN(tmp_path):
    q = svc(tmp_path, [])
    q.seed_cursor("2026-01-01T00:00:00Z")
    assert q.read_queue("not-a-time").state is State.UNKNOWN


def test_a_cursor_that_cannot_be_PERSISTED_does_not_claim_the_read(tmp_path):
    """Coverage is a fact about what this process read. If we cannot record
    that we read it, we must not claim it — the next read repeats the window."""
    q = svc(tmp_path, [event("r1")])
    q.seed_cursor("2026-01-01T00:00:00Z")
    q.local_cursor_path.parent.chmod(0o500)          # read-only dir
    try:
        out = q.read_queue("2026-01-01T00:01:00Z")
    finally:
        q.local_cursor_path.parent.chmod(0o700)
    assert out.state is State.UNKNOWN
    assert "could not be persisted" in out.message
    assert out.data["events"], "the events it did read were withheld from the caller"


def test_seed_refuses_an_invalid_start_time(tmp_path):
    assert svc(tmp_path, []).seed_cursor("nonsense") is False
