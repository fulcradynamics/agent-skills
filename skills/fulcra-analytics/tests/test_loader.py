import json

import pandas as pd

from fulcra_analytics.loader import dataframe_from_payload, load_dataframe, load_records


def test_extracts_records_wrapped_in_records_key(tmp_path):
    path = tmp_path / "records.json"
    path.write_text(json.dumps({"records": [{"id": "a", "value": 1}, {"id": "b", "value": 2}]}))

    df = load_dataframe(path)

    assert list(df["id"]) == ["a", "b"]
    assert list(df["value"]) == [1, 2]


def test_flattens_nested_fulcra_shape_and_coerces_time():
    df = dataframe_from_payload(
        {
            "data": [
                {
                    "id": "sample-1",
                    "startDate": "2026-06-26T10:00:00Z",
                    "metric": {"value": 42, "unit": "count"},
                }
            ]
        }
    )

    assert df.loc[0, "metric.value"] == 42
    assert df.loc[0, "metric.unit"] == "count"
    assert pd.api.types.is_datetime64_any_dtype(df["startDate"])


def test_jsonl_and_csv_load_as_records(tmp_path):
    jsonl = tmp_path / "records.jsonl"
    jsonl.write_text('{"x": 1}\n{"x": 2}\n')
    assert [r["x"] for r in load_records(jsonl)] == [1, 2]

    csv = tmp_path / "records.csv"
    csv.write_text("x,y\n1,a\n2,b\n")
    df = load_dataframe(csv)
    assert list(df["x"]) == ["1", "2"]
    assert list(df["y"]) == ["a", "b"]


def test_dict_of_record_values_keeps_outer_key():
    df = dataframe_from_payload({"abc": {"value": 1}, "def": {"value": 2}})
    assert set(df["record_key"]) == {"abc", "def"}
    assert list(df["value"]) == [1, 2]
