import json

from fulcra_workspaces.member import MemberService
from fulcra_workspaces.model import Authority, State


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
        self.events = []

    def read_file(self, path):
        return (self.files[path], "ok") if path in self.files else (None, "absent")

    def write_file(self, path, content):
        self.files[path] = content
        return True

    def record_write(self, data_type, api_version, note, source, *, tags=()):
        self.events.append(json.loads(note))
        return True


def test_join_is_append_only_bus_announced_and_records_identity_movement():
    transport = MemoryTransport()
    service = MemberService(transport, AUTHORITY)
    first = service.join(
        "demo", "analyst",
        {"machine": "workstation", "cloud": "local", "harness": "codex"},
        join_id="00000000-0000-0000-0000-000000000001",
        timestamp="2026-08-14T10:00:00Z",
    )
    second = service.join(
        "demo", "analyst",
        {"machine": "build-host", "cloud": "remote", "harness": "claude-code"},
        join_id="00000000-0000-0000-0000-000000000002",
        timestamp="2026-08-14T11:00:00Z",
    )

    assert first.state is State.DATA
    assert second.state is State.DATA
    assert len(transport.events) == 2
    moved = json.loads(transport.files[second.data["ptr"]])
    assert moved["moved_from"] == first.data["ptr"]
    assert moved["dimensions"]["harness"] == "claude-code"

