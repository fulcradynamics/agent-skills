from pathlib import Path

from fulcra_workspaces.doctor import DoctorService
from fulcra_workspaces.model import Authority, State


AUTHORITY = Authority(
    data_type="MomentAnnotation/00000000-0000-0000-0000-000000000001",
    api_version="v1alpha1",
    protocol=1,
    base_tag="00000000-0000-0000-0000-000000000002",
    max_window_seconds=3600,
    max_records=500,
)


class FakeTransport:
    def __init__(self, listing=([], "ok")):
        self.listing = listing

    def list_dir(self, path):
        return self.listing


def test_doctor_distinguishes_bus_ready_legacy_store_and_unknown(tmp_path):
    ready = DoctorService(FakeTransport(), tmp_path).check(AUTHORITY, workspace="demo")
    assert ready.state is State.DATA

    legacy = DoctorService(
        FakeTransport((["progress.md"], "ok")), tmp_path
    ).check(None, workspace="demo")
    assert legacy.state is State.STORE_ONLY

    unknown = DoctorService(
        FakeTransport((None, "error")), tmp_path
    ).check(None, workspace="demo")
    assert unknown.state is State.UNKNOWN

