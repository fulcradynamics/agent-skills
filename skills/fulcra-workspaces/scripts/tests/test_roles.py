import json

from fulcra_workspaces.model import State
from fulcra_workspaces.roles import RoleService


UUID_1 = "00000000-0000-0000-0000-000000000001"
UUID_2 = "00000000-0000-0000-0000-000000000002"
UUID_3 = "00000000-0000-0000-0000-000000000003"
UUID_4 = "00000000-0000-0000-0000-000000000004"


class MemoryTransport:
    def __init__(self):
        self.files = {}
        self.listing_state = "ok"
        self.extra_names = []

    def read_file(self, path):
        if path not in self.files:
            return None, "absent"
        return self.files[path], "ok"

    def write_file(self, path, content):
        self.files[path] = content
        return True

    def list_dir(self, path):
        if self.listing_state != "ok":
            return None, self.listing_state
        prefix = path.rstrip("/") + "/"
        names = {
            key.removeprefix(prefix).split("/", 1)[0]
            for key in self.files
            if key.startswith(prefix)
        }
        return sorted(names | set(self.extra_names)), "ok"


def define(service, policy="exclusive", lease_seconds=3600):
    return service.define("demo", "reviewer", policy, lease_seconds, "Review work")


def test_definition_is_write_once_and_idempotent(tmp_path):
    service = RoleService(MemoryTransport(), tmp_path)

    first = define(service)
    same = define(service)
    conflict = define(service, policy="shared")

    assert first.state is State.DATA
    assert same.state is State.DATA
    assert conflict.state is State.UNKNOWN


def test_claim_refresh_release_are_append_only(tmp_path):
    transport = MemoryTransport()
    service = RoleService(transport, tmp_path)
    assert define(service).state is State.DATA

    first = service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:00:00Z",
        event_id=UUID_1, session_nonce="session-a",
    )
    refresh = service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:15:00Z",
        event_id=UUID_2, session_nonce="session-a",
    )
    release = service.release(
        "demo", "reviewer", "alice", now="2026-08-14T10:20:00Z",
        event_id=UUID_3, session_nonce="session-a",
    )

    assert first.state is State.DATA
    assert refresh.state is State.DATA
    assert release.state is State.DATA
    history = [path for path in transport.files if "/history/" in path]
    assert len(history) == 3
    status = service.status("demo", "reviewer", now="2026-08-14T10:21:00Z")
    assert status.state is State.CLEAR
    assert status.data == {"status": "VACANT", "policy": "exclusive", "holders": []}


def test_live_foreign_nonce_requires_explicit_takeover(tmp_path):
    transport = MemoryTransport()
    service = RoleService(transport, tmp_path)
    define(service)
    service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:00:00Z",
        event_id=UUID_1, session_nonce="session-a",
    )

    refused = service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:10:00Z",
        event_id=UUID_2, session_nonce="session-b",
    )
    accepted = service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:10:00Z",
        event_id=UUID_2, session_nonce="session-b", takeover=True,
    )

    assert refused.state is State.UNKNOWN
    assert accepted.state is State.DATA
    latest = json.loads(transport.files[
        "team/demo/roles/reviewer/leases/alice/latest.json"
    ])
    lease = json.loads(transport.files[latest["ptr"]])
    assert lease["session_nonce"] == "session-b"


def test_stale_lease_allows_a_new_session_without_takeover(tmp_path):
    transport = MemoryTransport()
    service = RoleService(transport, tmp_path)
    define(service, lease_seconds=60)
    service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:00:00Z",
        event_id=UUID_1, session_nonce="session-a",
    )

    outcome = service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:01:01Z",
        event_id=UUID_2, session_nonce="session-b",
    )

    assert outcome.state is State.DATA


def test_exclusive_contention_and_shared_holders_fold_deterministically(tmp_path):
    for policy, expected in (("exclusive", "CONTESTED"), ("shared", "HELD")):
        transport = MemoryTransport()
        service = RoleService(transport, tmp_path / policy)
        define(service, policy=policy)
        service.claim(
            "demo", "reviewer", "alice", now="2026-08-14T10:00:00Z",
            event_id=UUID_1, session_nonce="session-a",
        )
        service.claim(
            "demo", "reviewer", "bob", now="2026-08-14T10:01:00Z",
            event_id=UUID_2, session_nonce="session-b",
        )

        status = service.status("demo", "reviewer", now="2026-08-14T10:02:00Z")

        assert status.state is State.DATA
        assert status.data["status"] == expected
        assert status.data["holders"] == ["alice", "bob"]


def test_status_fails_closed_on_unreadable_malformed_or_unbounded_state(tmp_path):
    transport = MemoryTransport()
    service = RoleService(transport, tmp_path, max_holders=1)
    define(service)
    service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:00:00Z",
        event_id=UUID_1, session_nonce="session-a",
    )

    transport.listing_state = "error"
    assert service.status(
        "demo", "reviewer", now="2026-08-14T10:01:00Z"
    ).state is State.UNKNOWN

    transport.listing_state = "ok"
    transport.files["team/demo/roles/reviewer/leases/alice/latest.json"] = "{"
    assert service.status(
        "demo", "reviewer", now="2026-08-14T10:01:00Z"
    ).state is State.UNKNOWN

    transport.extra_names = ["bob"]
    assert service.status(
        "demo", "reviewer", now="2026-08-14T10:01:00Z"
    ).state is State.UNKNOWN


def test_release_rejects_a_foreign_live_session(tmp_path):
    transport = MemoryTransport()
    service = RoleService(transport, tmp_path)
    define(service)
    service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:00:00Z",
        event_id=UUID_1, session_nonce="session-a",
    )

    outcome = service.release(
        "demo", "reviewer", "alice", now="2026-08-14T10:10:00Z",
        event_id=UUID_2, session_nonce="session-b",
    )

    assert outcome.state is State.UNKNOWN
    assert len([path for path in transport.files if "/history/" in path]) == 1


def test_status_accepts_store_directory_suffixes(tmp_path):
    transport = MemoryTransport()
    service = RoleService(transport, tmp_path)
    define(service)
    service.claim(
        "demo", "reviewer", "alice", now="2026-08-14T10:00:00Z",
        event_id=UUID_1, session_nonce="session-a",
    )
    transport.list_dir = lambda path: (["alice/"], "ok")

    outcome = service.status("demo", "reviewer", now="2026-08-14T10:01:00Z")

    assert outcome.state is State.DATA
    assert outcome.data["holders"] == ["alice"]
