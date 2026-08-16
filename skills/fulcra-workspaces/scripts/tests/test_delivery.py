import json

from fulcra_workspaces.delivery import DeliveryService
from fulcra_workspaces.model import Authority, State
from fulcra_workspaces.store import Message, parse_message, render_message


AUTHORITY = Authority(
    data_type="MomentAnnotation/00000000-0000-0000-0000-000000000001",
    api_version="v1alpha1",
    protocol=1,
    base_tag="00000000-0000-0000-0000-000000000002",
    max_window_seconds=3600,
    max_records=500,
)


class FakeTransport:
    def __init__(self):
        self.files = {}
        self.file_write_ok = True
        self.record_write_ok = True
        self.corrupt_readback = False
        self.fail_write_prefix = None
        self.records = []

    def read_file(self, path):
        if path not in self.files:
            return None, "absent"
        body = self.files[path]
        if self.corrupt_readback:
            body += "corrupt"
        return body, "ok"

    def write_file(self, path, content):
        if not self.file_write_ok or (
            self.fail_write_prefix and path.startswith(self.fail_write_prefix)
        ):
            return False
        self.files[path] = content
        return True

    def record_write(self, data_type, api_version, note, source, *, tags=()):
        if not self.record_write_ok:
            return False
        self.records.append((data_type, api_version, note, source, tags))
        return True


def test_message_roundtrip_is_human_readable_and_digest_bound():
    message = Message.create(
        message_id="00000000-0000-0000-0000-000000000003",
        workspace="research",
        sender="planner",
        recipient="analyst",
        slug="review-map",
        priority="P1",
        body="Review the market map.\n",
        timestamp="2026-08-14T00:00:00Z",
    )
    rendered = render_message(message)

    assert rendered.startswith("---\ntype: Workspaces Message\n")
    assert "# review-map" in rendered
    assert parse_message(rendered) == message
    assert parse_message(rendered.replace("market", "tampered")) is None


def test_failed_document_write_emits_no_event():
    transport = FakeTransport()
    transport.file_write_ok = False
    service = DeliveryService(transport, AUTHORITY)

    outcome = service.send_message(
        "research", "planner", "analyst", "review-map", "Body", "P1",
        message_id="00000000-0000-0000-0000-000000000003",
        timestamp="2026-08-14T00:00:00Z",
    )

    assert outcome.state is State.UNKNOWN
    assert transport.records == []


def test_failed_or_mismatched_readback_emits_no_event():
    transport = FakeTransport()
    transport.corrupt_readback = True
    service = DeliveryService(transport, AUTHORITY)

    outcome = service.send_message(
        "research", "planner", "analyst", "review-map", "Body", "P1",
        message_id="00000000-0000-0000-0000-000000000003",
        timestamp="2026-08-14T00:00:00Z",
    )

    assert outcome.state is State.UNKNOWN
    assert transport.records == []


def test_event_failure_preserves_verified_document_as_durable_only():
    transport = FakeTransport()
    transport.record_write_ok = False
    service = DeliveryService(transport, AUTHORITY)

    outcome = service.send_message(
        "research", "planner", "analyst", "review-map", "Body", "P1",
        message_id="00000000-0000-0000-0000-000000000003",
        timestamp="2026-08-14T00:00:00Z",
    )

    assert outcome.state is State.DURABLE_ONLY
    assert outcome.data["ptr"] in transport.files
    assert outcome.data["inbox_ptr"] in transport.files


def test_failed_recipient_index_emits_no_event():
    transport = FakeTransport()
    transport.fail_write_prefix = "team/research/member/analyst/inbox/"
    service = DeliveryService(transport, AUTHORITY)

    outcome = service.send_message(
        "research", "planner", "analyst", "review-map", "Body", "P1",
        message_id="00000000-0000-0000-0000-000000000003",
        timestamp="2026-08-14T00:00:00Z",
    )

    assert outcome.state is State.UNKNOWN
    assert transport.records == []


def test_success_emits_coord_compatible_pointer_event():
    transport = FakeTransport()
    service = DeliveryService(transport, AUTHORITY)

    outcome = service.send_message(
        "research", "planner", "analyst", "review-map", "Body", "P1",
        message_id="00000000-0000-0000-0000-000000000003",
        timestamp="2026-08-14T00:00:00Z",
    )

    assert outcome.state is State.DATA
    _, _, note, source, tags = transport.records[0]
    assert json.loads(note) == {
        "kind": "directive",
        "pri": "P1",
        "ptr": outcome.data["ptr"],
        "slug": "review-map",
        "to": "analyst",
        "v": 1,
        "workspace": "research",
    }
    assert source == "planner"
    assert tags == (AUTHORITY.base_tag,)
    assert outcome.data["inbox_ptr"] == (
        "team/research/member/analyst/inbox/"
        "00000000-0000-0000-0000-000000000003.json"
    )


def test_retry_reuses_identical_document_and_refuses_collision():
    transport = FakeTransport()
    service = DeliveryService(transport, AUTHORITY)
    kwargs = dict(
        workspace="research",
        sender="planner",
        recipient="analyst",
        slug="review-map",
        body="Body",
        priority="P1",
        message_id="00000000-0000-0000-0000-000000000003",
        timestamp="2026-08-14T00:00:00Z",
    )

    assert service.send_message(**kwargs).state is State.DATA
    assert service.send_message(**kwargs).state is State.DATA
    assert len(transport.files) == 2

    collision = service.send_message(**{**kwargs, "body": "Different"})
    assert collision.state is State.UNKNOWN
    assert len(transport.records) == 2
