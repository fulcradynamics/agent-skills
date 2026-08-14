from fulcra_workspaces.continuity import ContinuityService
from fulcra_workspaces.handoff import RoleHandoffService
from fulcra_workspaces.model import State
from fulcra_workspaces.roles import RoleService


UUID_1 = "00000000-0000-0000-0000-000000000001"
UUID_2 = "00000000-0000-0000-0000-000000000002"
UUID_3 = "00000000-0000-0000-0000-000000000003"

SNAPSHOT = {
    "objective": "Review the release",
    "decisions": ["Require an exact head"],
    "completed": ["Reviewed the implementation"],
    "next_actions": ["Watch the merge"],
    "open_questions": [],
    "pointers": ["team/demo/message/review.md"],
}


class MemoryTransport:
    def __init__(self):
        self.files = {}
        self.writes = []
        self.fail_path = None

    def read_file(self, path):
        if path not in self.files:
            return None, "absent"
        return self.files[path], "ok"

    def write_file(self, path, content):
        self.writes.append(path)
        if path == self.fail_path:
            return False
        self.files[path] = content
        return True

    def list_dir(self, path):
        prefix = path.rstrip("/") + "/"
        names = {
            key.removeprefix(prefix).split("/", 1)[0]
            for key in self.files
            if key.startswith(prefix)
        }
        return sorted(names), "ok"


def services(transport, tmp_path):
    roles = RoleService(transport, tmp_path)
    continuity = ContinuityService(transport)
    roles.define("demo", "reviewer", "exclusive", 3600, "Review work")
    roles.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:00:00Z",
        event_id=UUID_1, session_nonce="session-a",
    )
    return roles, continuity, RoleHandoffService(roles, continuity)


def test_handoff_checkpoints_before_release(tmp_path):
    transport = MemoryTransport()
    roles, continuity, handoffs = services(transport, tmp_path)

    outcome = handoffs.handoff(
        "demo", "reviewer", "alice", SNAPSHOT,
        now="2026-08-14T10:30:00Z", checkpoint_id=UUID_2,
        release_event_id=UUID_3, session_nonce="session-a",
    )

    role_continuity_ptr = "team/demo/roles/reviewer/continuity/latest.json"
    release_ptr = (
        "team/demo/roles/reviewer/leases/alice/history/"
        "00000000-0000-0000-0000-000000000003.json"
    )
    assert outcome.state is State.DATA
    assert transport.writes.index(role_continuity_ptr) < transport.writes.index(release_ptr)
    assert roles.status(
        "demo", "reviewer", now="2026-08-14T10:31:00Z"
    ).state is State.CLEAR
    assert continuity.resume_role(
        "demo", "reviewer", now="2026-08-14T10:31:00Z",
        max_age_seconds=3600, max_bytes=10_000,
    ).data["checkpoint"]["identity"] == "alice"


def test_handoff_does_not_release_when_checkpoint_projection_fails(tmp_path):
    transport = MemoryTransport()
    roles, _, handoffs = services(transport, tmp_path)
    transport.fail_path = "team/demo/roles/reviewer/continuity/latest.json"

    outcome = handoffs.handoff(
        "demo", "reviewer", "alice", SNAPSHOT,
        now="2026-08-14T10:30:00Z", checkpoint_id=UUID_2,
        release_event_id=UUID_3, session_nonce="session-a",
    )

    assert outcome.state is State.DURABLE_ONLY
    assert roles.status(
        "demo", "reviewer", now="2026-08-14T10:31:00Z"
    ).data["status"] == "HELD"
    assert not any('"state":"released"' in body for body in transport.files.values())


def test_handoff_keeps_checkpoint_when_release_session_conflicts(tmp_path):
    transport = MemoryTransport()
    roles, continuity, handoffs = services(transport, tmp_path)

    outcome = handoffs.handoff(
        "demo", "reviewer", "alice", SNAPSHOT,
        now="2026-08-14T10:30:00Z", checkpoint_id=UUID_2,
        release_event_id=UUID_3, session_nonce="session-b",
    )

    assert outcome.state is State.DURABLE_ONLY
    assert continuity.resume_role(
        "demo", "reviewer", now="2026-08-14T10:31:00Z",
        max_age_seconds=3600, max_bytes=10_000,
    ).state is State.DATA
