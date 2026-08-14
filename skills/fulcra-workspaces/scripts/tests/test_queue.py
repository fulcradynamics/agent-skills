import json
from datetime import datetime, timezone

from fulcra_workspaces.jsonutil import compact_json
from fulcra_workspaces.model import Authority, State
from fulcra_workspaces.queue import QueueService
from fulcra_workspaces.store import Message, render_message


AUTHORITY = Authority(
    data_type="MomentAnnotation/00000000-0000-0000-0000-000000000001",
    api_version="v1alpha1",
    protocol=1,
    base_tag="00000000-0000-0000-0000-000000000002",
    max_window_seconds=3600,
    max_records=500,
)
NOW = "2026-08-14T01:00:00Z"
START = "2026-08-14T00:30:00Z"


def event(record_id, workspace="research", recipient="analyst", message_id=None):
    message_id = message_id or f"00000000-0000-0000-0000-{record_id:012d}"
    return {
        "id": f"r-{record_id}",
        "recorded_at": f"2026-08-14T00:{40 + record_id:02d}:00Z",
        "sources": ["planner"],
        "note": compact_json({
            "v": 1,
            "workspace": workspace,
            "to": recipient,
            "kind": "directive",
            "pri": "P1",
            "slug": f"work-{record_id}",
            "ptr": f"team/{workspace}/message/{message_id}.md",
        }),
    }


def message_for(row):
    payload = json.loads(row["note"])
    message_id = payload["ptr"].rsplit("/", 1)[-1].removesuffix(".md")
    return render_message(Message.create(
        message_id=message_id,
        workspace=payload["workspace"],
        sender="planner",
        recipient=payload["to"],
        slug=payload["slug"],
        priority=payload["pri"],
        body=f"Body for {message_id}",
        timestamp=row["recorded_at"],
    ))


class FakeTransport:
    def __init__(self, rows=None):
        self.rows = rows
        self.files = {}
        self.calls = []
        self.write_ok = True
        for row in rows or []:
            payload = json.loads(row["note"])
            if "ptr" in payload:
                self.files[payload["ptr"]] = message_for(row)

    def records(self, data_type, since, until, *, max_records):
        self.calls.append(("records", data_type, since, until, max_records))
        return self.rows

    def read_file(self, path):
        self.calls.append(("read", path))
        if path not in self.files:
            return None, "absent"
        return self.files[path], "ok"

    def write_file(self, path, content):
        self.calls.append(("write", path))
        if not self.write_ok:
            return False
        self.files[path] = content
        return True

    def list_dir(self, path):
        self.calls.append(("list", path))
        prefix = path.rstrip("/") + "/"
        return sorted(
            key.removeprefix(prefix)
            for key in self.files
            if key.startswith(prefix) and "/" not in key.removeprefix(prefix)
        ), "ok"


def service(tmp_path, transport):
    queue = QueueService(transport, AUTHORITY, "analyst", tmp_path)
    assert queue.seed_cursor(START)
    return queue


def test_one_record_read_returns_multiple_workspaces_and_selected_bodies(tmp_path):
    rows = [
        event(1),
        event(2, workspace="writing"),
        event(3, recipient="someone-else"),
        event(4, workspace="ops", recipient="all"),
    ]
    transport = FakeTransport(rows)
    queue = service(tmp_path, transport)

    outcome = queue.read_queue(NOW)

    assert outcome.state is State.DATA
    assert [item["record_id"] for item in outcome.data["events"]] == [
        "r-1", "r-2", "r-4"
    ]
    assert len([call for call in transport.calls if call[0] == "records"]) == 1
    assert len([call for call in transport.calls if call[0] == "read"]) == 6


def test_unknown_record_window_does_not_advance_cursor(tmp_path):
    transport = FakeTransport(None)
    queue = service(tmp_path, transport)
    before = queue.local_cursor_path.read_text()

    outcome = queue.read_queue(NOW)

    assert outcome.state is State.UNKNOWN
    assert queue.local_cursor_path.read_text() == before


def test_stale_cursor_returns_backlog_without_query(tmp_path):
    transport = FakeTransport([])
    queue = QueueService(transport, AUTHORITY, "analyst", tmp_path)
    assert queue.seed_cursor("2026-08-13T00:00:00Z")

    outcome = queue.read_queue(NOW)

    assert outcome.state is State.BACKLOG
    assert transport.calls == []


def test_clear_advances_only_local_hot_cursor(tmp_path):
    transport = FakeTransport([])
    queue = service(tmp_path, transport)

    outcome = queue.read_queue(NOW)

    assert outcome.state is State.CLEAR
    assert json.loads(queue.local_cursor_path.read_text())["last_read"] == NOW
    assert [call for call in transport.calls if call[0] == "write"] == []


def test_pending_batch_replays_without_a_second_query(tmp_path):
    transport = FakeTransport([event(1)])
    queue = service(tmp_path, transport)

    first = queue.read_queue(NOW)
    second = queue.read_queue(NOW)

    assert first.data == second.data
    assert len([call for call in transport.calls if call[0] == "records"]) == 1


def test_complete_writes_receipt_then_cursor_mirror_and_advances(tmp_path):
    row = event(1)
    transport = FakeTransport([row])
    queue = service(tmp_path, transport)
    assert queue.read_queue(NOW).state is State.DATA

    outcome = queue.complete("r-1", "completed")

    assert outcome.state is State.DATA
    writes = [call[1] for call in transport.calls if call[0] == "write"]
    assert writes == [
        "team/research/member/analyst/receipt/"
        "00000000-0000-0000-0000-000000000001.json",
        "_workspaces/member/analyst/cursor.json",
    ]
    assert json.loads(queue.local_cursor_path.read_text())["last_read"] == NOW
    assert not queue.pending_path.exists()


def test_failed_receipt_write_keeps_batch_pending_and_cursor_unchanged(tmp_path):
    transport = FakeTransport([event(1)])
    queue = service(tmp_path, transport)
    assert queue.read_queue(NOW).state is State.DATA
    transport.write_ok = False

    outcome = queue.complete("r-1", "completed")

    assert outcome.state is State.UNKNOWN
    assert queue.pending_path.exists()
    assert json.loads(queue.local_cursor_path.read_text())["last_read"] == START


def test_receipted_replay_is_suppressed_and_coverage_advances(tmp_path):
    row = event(1)
    transport = FakeTransport([row])
    queue = service(tmp_path, transport)
    message_id = json.loads(row["note"])["ptr"].rsplit("/", 1)[-1][:-3]
    receipt_path = f"team/research/member/analyst/receipt/{message_id}.json"
    transport.files[receipt_path] = compact_json({
        "schema": "fulcra.workspaces-receipt.v1",
        "message_id": message_id,
        "record_id": "r-1",
        "recipient": "analyst",
        "workspace": "research",
        "outcome": "completed",
    })

    outcome = queue.read_queue(NOW)

    assert outcome.state is State.CLEAR
    assert json.loads(queue.local_cursor_path.read_text())["last_read"] == NOW


def test_control_looking_malformed_event_is_unknown_not_skipped(tmp_path):
    row = event(1)
    row["note"] = '{"v":1,"workspace":"research"}'
    transport = FakeTransport([row])
    queue = service(tmp_path, transport)

    assert queue.read_queue(NOW).state is State.UNKNOWN
