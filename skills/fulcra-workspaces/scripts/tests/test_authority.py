import json

from fulcra_workspaces.authority import (
    AUTHORITY_PATH,
    AuthorityStore,
    parse_authority,
)


DATA_TYPE = "MomentAnnotation/00000000-0000-0000-0000-000000000001"
TAG_ID = "00000000-0000-0000-0000-000000000002"


class FakeTransport:
    def __init__(self):
        self.files = {}
        self.created = 0
        self.spec_ok = True
        self.verify_ok = True
        self.tag_ok = True
        self.writes = []

    def read_file(self, path):
        if path not in self.files:
            return None, "absent"
        return self.files[path], "ok"

    def write_file(self, path, content):
        self.files[path] = content
        self.writes.append(path)
        return True

    def create_annotation(self, name):
        self.created += 1
        return DATA_TYPE

    def set_annotation_spec(self, data_type, default_note):
        return self.spec_ok

    def verify_annotation(self, data_type):
        return self.verify_ok

    def create_tag(self, name):
        return TAG_ID if self.tag_ok else None


def test_parse_authority_is_strict():
    raw = json.dumps({
        "schema": "fulcra.workspaces-bus.v1",
        "data_type": DATA_TYPE,
        "api_version": "v1alpha1",
        "protocol": 1,
        "base_tag": TAG_ID,
        "max_window_seconds": 3600,
        "max_records": 500,
    })
    assert parse_authority(raw).data_type == DATA_TYPE
    assert parse_authority(raw.replace('"protocol": 1', '"protocol": 2')) is None
    assert parse_authority("{") is None


def test_setup_creates_verifies_and_readbacks_before_local_cache(tmp_path):
    transport = FakeTransport()
    cache = tmp_path / "authority.json"
    authority = AuthorityStore(transport, cache).setup()

    assert authority.data_type == DATA_TYPE
    assert authority.base_tag == TAG_ID
    assert transport.created == 1
    assert transport.writes == [AUTHORITY_PATH]
    assert parse_authority(cache.read_text()) == authority


def test_second_setup_reuses_durable_account_channel(tmp_path):
    transport = FakeTransport()
    first = AuthorityStore(transport, tmp_path / "one.json").setup()
    second = AuthorityStore(transport, tmp_path / "two.json").setup()

    assert second == first
    assert transport.created == 1


def test_failed_spec_verify_or_tag_never_publishes_authority(tmp_path):
    for attr in ("spec_ok", "verify_ok", "tag_ok"):
        transport = FakeTransport()
        setattr(transport, attr, False)
        assert AuthorityStore(transport, tmp_path / f"{attr}.json").setup() is None
        assert AUTHORITY_PATH not in transport.files
        assert not (tmp_path / f"{attr}.json").exists()


def test_malformed_durable_authority_is_invalid_not_recreated(tmp_path):
    transport = FakeTransport()
    transport.files[AUTHORITY_PATH] = "not-json"

    assert AuthorityStore(transport, tmp_path / "authority.json").setup() is None
    assert transport.created == 0

