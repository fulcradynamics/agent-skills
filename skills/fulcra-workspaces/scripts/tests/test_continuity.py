import json

from fulcra_workspaces.continuity import ContinuityService
from fulcra_workspaces.model import State
from fulcra_workspaces.roles import RoleService


class MemoryTransport:
    def __init__(self):
        self.files = {}
        self.fail_latest = False
        self.fail_path = None

    def read_file(self, path):
        if path not in self.files:
            return None, "absent"
        return self.files[path], "ok"

    def write_file(self, path, content):
        if self.fail_path == path:
            return False
        if self.fail_latest and path.endswith("/latest.json"):
            return False
        self.files[path] = content
        return True


SNAPSHOT = {
    "objective": "Ship the bounded coordination demo",
    "decisions": ["Use one account Bus"],
    "completed": ["Defined the event envelope"],
    "next_actions": ["Run acceptance tests"],
    "open_questions": [],
    "pointers": ["team/demo/message/example.md"],
}


def claimed_role(transport, tmp_path):
    roles = RoleService(transport, tmp_path)
    roles.define("demo", "reviewer", "exclusive", 3600, "Review work")
    roles.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:00:00Z",
        event_id="00000000-0000-0000-0000-000000000009",
        session_nonce="session-a",
    )
    return roles


def test_checkpoints_are_append_only_and_latest_is_verified_projection():
    transport = MemoryTransport()
    service = ContinuityService(transport)

    first = service.checkpoint(
        "demo", "analyst", SNAPSHOT,
        checkpoint_id="00000000-0000-0000-0000-000000000001",
        timestamp="2026-08-14T10:00:00Z",
    )
    second = service.checkpoint(
        "demo", "analyst", SNAPSHOT,
        checkpoint_id="00000000-0000-0000-0000-000000000002",
        timestamp="2026-08-14T10:05:00Z",
    )

    assert first.state is State.DATA
    assert second.state is State.DATA
    history = sorted(path for path in transport.files if "/checkpoint/" in path)
    assert len(history) == 2
    latest = json.loads(transport.files["team/demo/member/analyst/continuity/latest.json"])
    assert latest["ptr"] == history[-1]


def test_failed_latest_write_leaves_canonical_history_resumable_by_pointer():
    transport = MemoryTransport()
    transport.fail_latest = True
    service = ContinuityService(transport)

    outcome = service.checkpoint(
        "demo", "analyst", SNAPSHOT,
        checkpoint_id="00000000-0000-0000-0000-000000000001",
        timestamp="2026-08-14T10:00:00Z",
    )

    assert outcome.state is State.DURABLE_ONLY
    assert outcome.data["ptr"] in transport.files


def test_resume_is_bounded_and_fails_closed_on_stale_malformed_or_oversized():
    transport = MemoryTransport()
    service = ContinuityService(transport)
    assert service.checkpoint(
        "demo", "analyst", SNAPSHOT,
        checkpoint_id="00000000-0000-0000-0000-000000000001",
        timestamp="2026-08-14T10:00:00Z",
    ).state is State.DATA

    fresh = service.resume(
        "demo", "analyst", now="2026-08-14T10:30:00Z",
        max_age_seconds=3600, max_bytes=10_000,
    )
    assert fresh.state is State.DATA
    assert fresh.data["checkpoint"]["objective"] == SNAPSHOT["objective"]

    stale = service.resume(
        "demo", "analyst", now="2026-08-14T12:00:01Z",
        max_age_seconds=3600, max_bytes=10_000,
    )
    assert stale.state is State.UNKNOWN

    oversized = service.resume(
        "demo", "analyst", now="2026-08-14T10:30:00Z",
        max_age_seconds=3600, max_bytes=10,
    )
    assert oversized.state is State.UNKNOWN

    transport.files["team/demo/member/analyst/continuity/latest.json"] = "{"
    assert service.resume(
        "demo", "analyst", now="2026-08-14T10:30:00Z",
        max_age_seconds=3600, max_bytes=10_000,
    ).state is State.UNKNOWN


def test_role_checkpoint_projects_one_bounded_resume_pointer(tmp_path):
    transport = MemoryTransport()
    roles = claimed_role(transport, tmp_path)
    service = ContinuityService(transport, role_service=roles)

    outcome = service.checkpoint(
        "demo", "alice", SNAPSHOT, role="reviewer",
        checkpoint_id="00000000-0000-0000-0000-000000000001",
        timestamp="2026-08-14T10:00:00Z",
    )
    resumed = service.resume_role(
        "demo", "reviewer", now="2026-08-14T10:30:00Z",
        max_age_seconds=3600, max_bytes=10_000,
    )

    assert outcome.state is State.DATA
    assert resumed.state is State.DATA
    assert resumed.data["checkpoint"]["role"] == "reviewer"
    assert resumed.data["checkpoint"]["identity"] == "alice"


def test_role_checkpoint_rejects_a_non_holder_before_writing(tmp_path):
    transport = MemoryTransport()
    roles = claimed_role(transport, tmp_path)
    service = ContinuityService(transport, role_service=roles)

    outcome = service.checkpoint(
        "demo", "bob", SNAPSHOT, role="reviewer",
        checkpoint_id="00000000-0000-0000-0000-000000000002",
        timestamp="2026-08-14T10:30:00Z",
    )

    assert outcome.state is State.UNKNOWN
    assert "team/demo/roles/reviewer/continuity/latest.json" not in transport.files
    assert not any(
        "/member/bob/continuity/" in path for path in transport.files
    )


def test_role_resume_fails_closed_on_conflicting_projection(tmp_path):
    transport = MemoryTransport()
    roles = claimed_role(transport, tmp_path)
    service = ContinuityService(transport, role_service=roles)
    service.checkpoint(
        "demo", "alice", SNAPSHOT, role="reviewer",
        checkpoint_id="00000000-0000-0000-0000-000000000001",
        timestamp="2026-08-14T10:00:00Z",
    )
    ptr = "team/demo/roles/reviewer/continuity/latest.json"
    projection = json.loads(transport.files[ptr])
    projection["identity"] = "mallory"
    transport.files[ptr] = json.dumps(projection)

    outcome = service.resume_role(
        "demo", "reviewer", now="2026-08-14T10:30:00Z",
        max_age_seconds=3600, max_bytes=10_000,
    )

    assert outcome.state is State.UNKNOWN


def test_failed_role_projection_keeps_the_checkpoint_durable(tmp_path):
    transport = MemoryTransport()
    roles = claimed_role(transport, tmp_path)
    transport.fail_path = "team/demo/roles/reviewer/continuity/latest.json"
    service = ContinuityService(transport, role_service=roles)

    outcome = service.checkpoint(
        "demo", "alice", SNAPSHOT, role="reviewer",
        checkpoint_id="00000000-0000-0000-0000-000000000001",
        timestamp="2026-08-14T10:00:00Z",
    )

    assert outcome.state is State.DURABLE_ONLY
    assert outcome.data["ptr"] in transport.files
