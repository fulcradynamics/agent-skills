import json

from fulcra_workspaces.model import Authority, State
from fulcra_workspaces.transfer import TransferService


AUTHORITY = Authority(
    data_type="MomentAnnotation/00000000-0000-0000-0000-000000000001",
    api_version="v1alpha1",
    protocol=1,
    base_tag="00000000-0000-0000-0000-000000000002",
    max_window_seconds=3600,
    max_records=500,
)


class MemoryTransport:
    def __init__(self):
        self.files = {}
        self.bytes = {}
        self.events = []

    def read_file(self, path):
        if path not in self.files:
            return None, "absent"
        return self.files[path], "ok"

    def write_file(self, path, content):
        self.files[path] = content
        return True

    def read_bytes(self, path):
        if path not in self.bytes:
            return None, "absent"
        return self.bytes[path], "ok"

    def write_bytes(self, path, content):
        self.bytes[path] = content
        return True

    def record_write(self, data_type, api_version, note, source, *, tags=()):
        self.events.append(json.loads(note))
        return True


def service(transport):
    return TransferService(transport, AUTHORITY)


def test_transfer_uploads_verified_bytes_then_manifest_then_pointer_event():
    transport = MemoryTransport()
    outcome = service(transport).send(
        "demo", "sender", "receiver", "report.txt", b"hello",
        media_type="text/plain", disclosure="User approved project report",
        transfer_id="00000000-0000-0000-0000-000000000001",
        timestamp="2026-08-14T10:00:00Z",
    )

    assert outcome.state is State.DATA
    manifest = json.loads(transport.files[outcome.data["ptr"]])
    assert manifest["size"] == 5
    assert manifest["sha256"] == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    )
    assert outcome.data["inbox_ptr"] in transport.files
    assert transport.events[0]["ptr"] == outcome.data["ptr"]


def test_transfer_refuses_collision_and_missing_disclosure():
    transport = MemoryTransport()
    transfer_id = "00000000-0000-0000-0000-000000000001"
    transport.bytes[f"team/demo/transfer/{transfer_id}/payload/report.txt"] = b"old"

    collision = service(transport).send(
        "demo", "sender", "receiver", "report.txt", b"new",
        media_type="text/plain", disclosure="Approved", transfer_id=transfer_id,
    )
    assert collision.state is State.UNKNOWN

    missing = service(MemoryTransport()).send(
        "demo", "sender", "receiver", "report.txt", b"new",
        media_type="text/plain", disclosure="", transfer_id=transfer_id,
    )
    assert missing.state is State.UNKNOWN


def test_receive_verifies_recipient_digest_and_replays_existing_receipt():
    transport = MemoryTransport()
    sent = service(transport).send(
        "demo", "sender", "receiver", "report.txt", b"hello",
        media_type="text/plain", disclosure="Approved", 
        transfer_id="00000000-0000-0000-0000-000000000001",
        timestamp="2026-08-14T10:00:00Z",
    )

    wrong_recipient = service(transport).receive(sent.data["ptr"], "other")
    assert wrong_recipient.state is State.UNKNOWN

    accepted = service(transport).receive(sent.data["ptr"], "receiver")
    assert accepted.state is State.DATA
    reads_before = len([path for path in transport.bytes])
    replay = service(transport).receive(sent.data["ptr"], "receiver")
    assert replay.state is State.DATA
    assert len([path for path in transport.bytes]) == reads_before


def test_receive_records_rejected_digest_receipt():
    transport = MemoryTransport()
    sent = service(transport).send(
        "demo", "sender", "receiver", "report.txt", b"hello",
        media_type="text/plain", disclosure="Approved",
        transfer_id="00000000-0000-0000-0000-000000000001",
    )
    manifest = json.loads(transport.files[sent.data["ptr"]])
    transport.bytes[manifest["payload_ptr"]] = b"tampered"

    rejected = service(transport).receive(sent.data["ptr"], "receiver")

    assert rejected.state is State.UNKNOWN
    receipt = json.loads(transport.files[rejected.data["receipt_ptr"]])
    assert receipt["status"] == "rejected"
