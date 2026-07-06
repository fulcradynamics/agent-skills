import json
import subprocess

import pandas as pd
import pytest

from fulcra_analytics.client import FulcraClient, FulcraClientError


def completed(stdout: str = "", returncode: int = 0, stderr: str = ""):
    return subprocess.CompletedProcess(args=["fulcra-api"], returncode=returncode, stdout=stdout, stderr=stderr)


def test_builds_uv_tool_command():
    client = FulcraClient()
    assert client.command(["get-records", "StepCount", "1 week"]) == [
        "uv",
        "tool",
        "run",
        "fulcra-api",
        "get-records",
        "StepCount",
        "1 week",
    ]


def test_json_parses_stdout(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return completed(json.dumps({"records": [{"value": 1}]}))

    monkeypatch.setattr(subprocess, "run", fake_run)
    client = FulcraClient(timeout=5)

    assert client.json(["get-records", "StepCount", "1 week"]) == {"records": [{"value": 1}]}
    assert calls[0][0] == ["uv", "tool", "run", "fulcra-api", "get-records", "StepCount", "1 week"]
    assert calls[0][1]["timeout"] == 5


def test_raises_helpful_error_on_nonzero_exit(monkeypatch):
    def fake_run(cmd, **kwargs):
        return completed(returncode=2, stderr="bad auth")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(FulcraClientError, match="bad auth"):
        FulcraClient().json(["user-info"])


def test_get_records_dataframe_uses_loader_normalization(monkeypatch):
    def fake_run(cmd, **kwargs):
        assert cmd[-3:] == ["get-records", "StepCount", "1 week"]
        return completed(json.dumps({"records": [{"startDate": "2026-06-26T00:00:00Z", "metric": {"value": 42}}]}))

    monkeypatch.setattr(subprocess, "run", fake_run)

    df = FulcraClient().get_records_dataframe("StepCount", "1 week")

    assert isinstance(df, pd.DataFrame)
    assert df.loc[0, "metric.value"] == 42
    assert pd.api.types.is_datetime64_any_dtype(df["startDate"])


def test_metric_time_series_dataframe(monkeypatch):
    def fake_run(cmd, **kwargs):
        assert cmd[-3:] == ["metric-time-series", "HeartRate", "1 day"]
        return completed(json.dumps({"data": [{"timestamp": "2026-06-26T00:00:00Z", "value": 70}]}))

    monkeypatch.setattr(subprocess, "run", fake_run)

    df = FulcraClient().metric_time_series_dataframe("HeartRate", "1 day")

    assert list(df["value"]) == [70]


def test_file_download_creates_parent_directory(monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return completed("downloaded")

    monkeypatch.setattr(subprocess, "run", fake_run)
    target = tmp_path / "nested" / "file.json"

    result = FulcraClient().file_download("remote/path.json", target)

    assert result == target
    assert target.parent.exists()
    assert calls[0][-3:] == ["download", "remote/path.json", str(target)]


def test_file_upload_invokes_cli(monkeypatch, tmp_path):
    source = tmp_path / "report.md"
    source.write_text("hello")

    def fake_run(cmd, **kwargs):
        assert cmd[-3:] == ["upload", str(source), "analytics/report.md"]
        return completed("uploaded")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert FulcraClient().file_upload(source, "analytics/report.md") == "uploaded"


def test_file_delete_invokes_cli(monkeypatch):
    def fake_run(cmd, **kwargs):
        assert cmd[-3:] == ["file", "delete", "team/example/inbox/message.md"]
        return completed("deleted")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert FulcraClient().file_delete("team/example/inbox/message.md") == "deleted"


def test_data_updates_invokes_cli_with_period(monkeypatch):
    def fake_run(cmd, **kwargs):
        assert cmd[-2:] == ["data-updates", "1 day"]
        return completed(json.dumps([{"path": "team/example/progress.md"}]))

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert FulcraClient().data_updates("1 day") == [{"path": "team/example/progress.md"}]


def test_timeout_is_wrapped_as_client_error(monkeypatch):
    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(FulcraClientError, match="timed out after 120 seconds"):
        FulcraClient().json(["catalog"])
