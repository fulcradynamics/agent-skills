import json

from fulcra_workspaces.authority import AuthorityStore
from fulcra_workspaces.continuity import ContinuityService
from fulcra_workspaces.delivery import DeliveryService
from fulcra_workspaces.doctor import DoctorService
from fulcra_workspaces.member import MemberService
from fulcra_workspaces.model import State
from fulcra_workspaces.queue import QueueService
from fulcra_workspaces.transfer import TransferService


class Account:
    def __init__(self):
        self.files = {}
        self.bytes = {}
        self.rows = []
        self.created = 0
        self.event_time = "2026-08-14T10:01:00Z"
        self.records_fail = False

    def read_file(self, path):
        return (self.files[path], "ok") if path in self.files else (None, "absent")

    def write_file(self, path, content):
        self.files[path] = content
        return True

    def read_bytes(self, path):
        return (self.bytes[path], "ok") if path in self.bytes else (None, "absent")

    def write_bytes(self, path, content):
        self.bytes[path] = content
        return True

    def list_dir(self, path):
        prefix = path.rstrip("/") + "/"
        names = sorted({
            key.removeprefix(prefix).split("/", 1)[0]
            for key in self.files if key.startswith(prefix)
        })
        return names, "ok"

    def records(self, data_type, since, until, *, max_records):
        if self.records_fail:
            return None
        return [row for row in self.rows if since <= row["recorded_at"] <= until]

    def record_write(self, data_type, api_version, note, source, *, tags=()):
        self.rows.append({
            "id": f"record-{len(self.rows) + 1}",
            "recorded_at": self.event_time,
            "sources": [source],
            "note": note,
        })
        return True

    def create_annotation(self, name):
        self.created += 1
        return "MomentAnnotation/00000000-0000-0000-0000-000000000001"

    def set_annotation_spec(self, data_type, default_note):
        return True

    def verify_annotation(self, data_type):
        return True

    def create_tag(self, name):
        return "00000000-0000-0000-0000-000000000002"


def test_two_agent_coordination_acceptance(tmp_path):
    account = Account()
    authority = AuthorityStore(account, tmp_path / "alice-authority.json").setup()
    adopted = AuthorityStore(account, tmp_path / "bob-authority.json").setup()
    assert adopted == authority
    assert account.created == 1

    members = MemberService(account, authority)
    assert members.join(
        "demo", "alice", {"machine": "host-a", "harness": "codex"},
        join_id="00000000-0000-0000-0000-000000000001",
        timestamp="2026-08-14T10:00:00Z",
    ).state is State.DATA
    assert members.join(
        "demo", "bob", {"machine": "host-b", "harness": "claude-code"},
        join_id="00000000-0000-0000-0000-000000000002",
        timestamp="2026-08-14T10:00:00Z",
    ).state is State.DATA

    account.event_time = "2026-08-14T10:05:00Z"
    sent = DeliveryService(account, authority).send_message(
        "demo", "alice", "bob", "review-plan", "Please review the plan.",
        message_id="00000000-0000-0000-0000-000000000003",
        timestamp="2026-08-14T10:05:00Z",
    )
    assert sent.state is State.DATA

    bob = QueueService(
        account, authority, "bob", tmp_path / "bob", session_nonce="bob-session"
    )
    assert bob.seed_cursor("2026-08-14T09:59:00Z")
    batch = bob.read_queue("2026-08-14T10:10:00Z")
    assert batch.state is State.DATA
    assert len(batch.data["events"]) == 2
    for item in list(batch.data["events"]):
        assert bob.complete(item["record_id"], "completed").state is State.DATA

    replay = QueueService(
        account, authority, "bob", tmp_path / "replay", session_nonce="replay-session"
    )
    assert replay.seed_cursor("2026-08-14T09:59:00Z")
    assert replay.read_queue("2026-08-14T10:10:00Z").state is State.CLEAR

    continuity = ContinuityService(account)
    snapshot = {
        "objective": "Review Alice's plan",
        "decisions": ["Approve bounded reads"],
        "completed": ["Reviewed the plan"],
        "next_actions": ["Receive the artifact"],
        "open_questions": [],
        "pointers": [sent.data["ptr"]],
    }
    assert continuity.checkpoint(
        "demo", "bob", snapshot,
        checkpoint_id="00000000-0000-0000-0000-000000000004",
        timestamp="2026-08-14T10:15:00Z",
    ).state is State.DATA
    assert continuity.resume(
        "demo", "bob", now="2026-08-14T10:20:00Z",
        max_age_seconds=3600, max_bytes=10_000,
    ).state is State.DATA

    account.event_time = "2026-08-14T10:25:00Z"
    transfer = TransferService(account, authority).send(
        "demo", "alice", "bob", "plan.txt", b"approved plan",
        media_type="text/plain", disclosure="User approved plan transfer",
        transfer_id="00000000-0000-0000-0000-000000000005",
        timestamp="2026-08-14T10:25:00Z",
    )
    assert transfer.state is State.DATA
    transfer_batch = bob.read_queue("2026-08-14T10:30:00Z")
    assert transfer_batch.state is State.DATA
    transfer_event = transfer_batch.data["events"][0]
    assert transfer_event["message_id"] == transfer.data["id"]
    assert TransferService(account, authority).receive(
        transfer.data["ptr"], "bob"
    ).state is State.DATA
    assert bob.complete(transfer_event["record_id"], "completed").state is State.DATA

    account.records_fail = True
    assert bob.read_queue("2026-08-14T10:35:00Z").state is State.UNKNOWN
    account.records_fail = False

    legacy = Account()
    legacy.files["team/legacy/progress.md"] = "legacy"
    assert DoctorService(legacy, tmp_path).check(
        None, workspace="legacy"
    ).state is State.STORE_ONLY

