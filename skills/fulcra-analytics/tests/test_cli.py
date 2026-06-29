import json

import pandas as pd
from typer.testing import CliRunner

from fulcra_analytics import cli


runner = CliRunner()


class FakeClient:
    def get_records_dataframe(self, data_type, time_range):
        assert data_type == "StepCount"
        assert time_range == "1 week"
        return pd.DataFrame(
            {
                "source": ["watch", "watch", "phone"],
                "steps": [1000, 3000, 500],
            }
        )

    def metric_time_series_dataframe(self, data_type, time_range):
        assert data_type == "HeartRate"
        assert time_range == "1 day"
        return pd.DataFrame({"timestamp": pd.to_datetime(["2026-06-26T00:00:00Z"], utc=True), "value": [70]})

    def catalog(self, *, base_types_only=False):
        return [{"id": "StepCount", "base": base_types_only}]

    def user_info(self):
        return {"preferences": {"timezone": "UTC"}}


def test_records_command_outputs_summary(monkeypatch):
    monkeypatch.setattr(cli, "default_client", lambda: FakeClient())

    result = runner.invoke(cli.app, ["records", "StepCount", "1 week", "--group-by", "source"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["metadata"] == {"source": "get-records", "data_type": "StepCount", "time_range": "1 week"}
    assert payload["numeric"]["steps"]["mean"] == 1500
    assert payload["groups"]["watch"]["row_count"] == 2


def test_metrics_command_outputs_summary(monkeypatch):
    monkeypatch.setattr(cli, "default_client", lambda: FakeClient())

    result = runner.invoke(cli.app, ["metrics", "HeartRate", "1 day"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["metadata"]["source"] == "metric-time-series"
    assert payload["numeric"]["value"]["max"] == 70
    assert payload["datetime"]["timestamp"]["count"] == 1


def test_file_command_loads_local_export(tmp_path):
    path = tmp_path / "records.json"
    path.write_text(json.dumps({"records": [{"kind": "a", "value": 1}, {"kind": "a", "value": 3}]}))

    result = runner.invoke(cli.app, ["file", str(path), "--pretty"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["metadata"] == {"source": "file", "path": str(path)}
    assert payload["numeric"]["value"]["mean"] == 2


def test_catalog_and_user_info_commands(monkeypatch):
    monkeypatch.setattr(cli, "default_client", lambda: FakeClient())

    catalog = runner.invoke(cli.app, ["catalog", "--base-types-only"])
    user_info = runner.invoke(cli.app, ["user-info"])

    assert catalog.exit_code == 0
    assert json.loads(catalog.stdout) == [{"id": "StepCount", "base": True}]
    assert user_info.exit_code == 0
    assert json.loads(user_info.stdout)["preferences"]["timezone"] == "UTC"
