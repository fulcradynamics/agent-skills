import json
import subprocess

from fulcra_workspaces.transport import FulcraTransport


class Runner:
    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def __call__(self, argv, *, timeout, input_text=None):
        self.calls.append((argv, timeout, input_text))
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def cp(rc=0, out="", err=""):
    return subprocess.CompletedProcess([], rc, out, err)


def test_records_parses_one_jsonl_window_and_counts_one_call():
    runner = Runner([cp(out=(
        '{"id":"r1","recorded_at":"2026-08-14T00:00:00Z",'
        '"sources":["sender"],"note":"hello"}\n'
    ))])
    transport = FulcraTransport(runner=runner, timeout=7)

    rows = transport.records(
        "MomentAnnotation/type", "2026-08-14T00:00:00Z",
        "2026-08-14T01:00:00Z", max_records=10,
    )

    assert rows == [{
        "id": "r1",
        "recorded_at": "2026-08-14T00:00:00Z",
        "sources": ["sender"],
        "note": "hello",
    }]
    assert len(runner.calls) == 1
    assert runner.calls[0][0][1:3] == ["get-records", "MomentAnnotation/type"]


def test_records_fails_closed_on_bad_json_missing_timestamp_or_excess_rows():
    bad_json = FulcraTransport(runner=Runner([cp(out="{\n")]))
    assert bad_json.records("T", "S", "U", max_records=2) is None

    missing_time = FulcraTransport(runner=Runner([cp(out='{"id":"r"}\n')]))
    assert missing_time.records("T", "S", "U", max_records=2) is None

    excess = FulcraTransport(runner=Runner([cp(out=(
        '{"recorded_at":"a"}\n{"recorded_at":"b"}\n'
    ))]))
    assert excess.records("T", "S", "U", max_records=1) is None


def test_records_timeout_is_unknown_not_empty():
    runner = Runner([subprocess.TimeoutExpired(["fulcra-api"], 1)])
    transport = FulcraTransport(runner=runner)
    assert transport.records("T", "S", "U", max_records=1) is None


def test_record_write_uses_stdin_and_never_argv_for_payload():
    runner = Runner([cp()])
    transport = FulcraTransport(runner=runner)

    assert transport.record_write(
        "MomentAnnotation/type", "v1alpha1", "secret note", "sender",
        tags=("tag-id",),
    )

    argv, _, input_text = runner.calls[0]
    assert "secret note" not in " ".join(argv)
    assert argv[-4:] == ["--api-version", "v1alpha1", "--source", "sender"]
    assert json.loads(input_text) == {"note": "secret note", "tags": ["tag-id"]}


def test_file_read_classifies_absent_separately_from_error():
    absent = FulcraTransport(runner=Runner([
        cp(rc=1, err="Error: File not found in Fulcra: x")
    ]))
    assert absent.read_file("x") == (None, "absent")

    error = FulcraTransport(runner=Runner([cp(rc=1, err="auth failed")]))
    assert error.read_file("x") == (None, "error")

    ok = FulcraTransport(runner=Runner([cp(out="body")]))
    assert ok.read_file("x") == ("body", "ok")

