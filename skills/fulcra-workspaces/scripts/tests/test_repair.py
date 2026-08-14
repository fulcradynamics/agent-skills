import json

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


class RepairTransport:
    def __init__(self):
        self.files = {}
        self.list_state = "ok"
        self.calls = []

    def list_dir(self, path):
        self.calls.append(("list", path))
        if self.list_state != "ok":
            return None, self.list_state
        prefix = path.rstrip("/") + "/"
        return sorted(
            key.removeprefix(prefix)
            for key in self.files
            if key.startswith(prefix)
        ), "ok"

    def read_file(self, path):
        self.calls.append(("read", path))
        if path not in self.files:
            return None, "absent"
        return self.files[path], "ok"

    def write_file(self, path, content):
        self.files[path] = content
        return True


def add_message(transport, message_id, recipient="analyst"):
    message = Message.create(
        message_id=message_id,
        workspace="research",
        sender="planner",
        recipient=recipient,
        slug="repair-work",
        priority="P2",
        body="Recover me",
        timestamp="2026-08-14T00:00:00Z",
    )
    transport.files[message.path] = render_message(message)
    index = f"team/research/member/{recipient}/inbox/{message_id}.json"
    transport.files[index] = compact_json({
        "schema": "fulcra.workspaces-inbox-pointer.v1",
        "id": message_id,
        "workspace": "research",
        "recipient": recipient,
        "ptr": message.path,
        "sha256": message.sha256,
    })


def test_repair_lists_only_recipient_inbox_and_honors_limit(tmp_path):
    transport = RepairTransport()
    add_message(transport, "00000000-0000-0000-0000-000000000001")
    add_message(transport, "00000000-0000-0000-0000-000000000002")
    queue = QueueService(transport, AUTHORITY, "analyst", tmp_path)

    outcome = queue.repair("research", limit=1)

    assert outcome.state is State.DATA
    assert len(outcome.data["messages"]) == 1
    assert transport.calls[0] == (
        "list", "team/research/member/analyst/inbox/"
    )
    assert all("team/research/message/" not in call[1]
               for call in transport.calls if call[0] == "list")


def test_repair_skips_receipted_message(tmp_path):
    transport = RepairTransport()
    message_id = "00000000-0000-0000-0000-000000000001"
    add_message(transport, message_id)
    transport.files[
        f"team/research/member/analyst/receipt/{message_id}.json"
    ] = "receipt"
    queue = QueueService(transport, AUTHORITY, "analyst", tmp_path)

    assert queue.repair("research", limit=10).state is State.CLEAR


def test_repair_unreadable_listing_is_unknown(tmp_path):
    transport = RepairTransport()
    queue = QueueService(transport, AUTHORITY, "analyst", tmp_path)
    transport.list_state = "error"
    assert queue.repair("research", limit=10).state is State.UNKNOWN



def test_repair_quarantines_bad_index_and_returns_healthy_item(tmp_path):
    transport = RepairTransport()
    add_message(transport, "00000000-0000-0000-0000-000000000001")
    transport.files[
        "team/research/member/analyst/inbox/000-bad.json"
    ] = json.dumps({"schema": "wrong"})
    queue = QueueService(transport, AUTHORITY, "analyst", tmp_path)

    outcome = queue.repair("research", limit=10)

    assert outcome.state is State.DATA
    assert len(outcome.data["messages"]) == 1
    assert outcome.data["poison"] == [{
        "entry": "000-bad.json",
        "reason": "recipient index has unknown schema",
    }]
