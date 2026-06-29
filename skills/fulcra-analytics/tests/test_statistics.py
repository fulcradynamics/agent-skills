import pandas as pd

from fulcra_analytics.statistics import (
    infer_column_kind,
    summarize_dataframe,
    summarize_records,
)


def test_summarize_records_basic_numeric_fields():
    result = summarize_records([
        {"steps": 1000, "mood": "4", "note": "walk"},
        {"steps": 2000, "mood": "5", "note": "run"},
        {"steps": None, "mood": "", "note": "rest"},
    ])
    assert result.row_count == 3
    assert result.missing["steps"] == 1
    assert result.numeric["steps"]["mean"] == 1500
    assert result.numeric["mood"]["max"] == 5


def test_summarize_dataframe_numeric_datetime_and_categorical_columns():
    df = pd.DataFrame(
        {
            "startDate": pd.to_datetime(
                ["2026-06-25T00:00:00Z", "2026-06-26T00:00:00Z", None], utc=True
            ),
            "steps": [1000, 3000, None],
            "source": ["watch", "phone", "watch"],
            "active": [True, False, True],
        }
    )

    summary = summarize_dataframe(df, metadata={"data_type": "StepCount"})

    assert summary.row_count == 3
    assert summary.column_count == 4
    assert summary.metadata["data_type"] == "StepCount"
    assert summary.missing["steps"] == 1
    assert summary.numeric["steps"]["mean"] == 2000
    assert summary.numeric["steps"]["quantiles"]["0.5"] == 2000
    assert summary.datetime["startDate"]["span_seconds"] == 86400
    assert summary.categorical["source"]["top_values"] == {"watch": 2, "phone": 1}
    assert summary.boolean["active"]["true"] == 2


def test_summarize_dataframe_with_groups():
    df = pd.DataFrame(
        {
            "source": ["watch", "watch", "phone"],
            "steps": [1000, 3000, 500],
            "distance": [0.5, 1.5, 0.25],
        }
    )

    summary = summarize_dataframe(df, group_by="source")

    assert summary.groups["watch"]["row_count"] == 2
    assert summary.groups["watch"]["numeric_mean"]["steps"] == 2000
    assert summary.groups["phone"]["numeric_mean"]["distance"] == 0.25


def test_infers_stringified_numeric_and_datetime_columns():
    assert infer_column_kind(pd.Series(["1", "2", "", "3"])) == "numeric"
    assert infer_column_kind(pd.Series(["2026-06-25T00:00:00Z", "2026-06-26T00:00:00Z"])) == "datetime"
    assert infer_column_kind(pd.Series(["walk", "run", "walk"])) == "categorical"


def test_dataframe_summary_to_dict_is_json_friendly():
    summary = summarize_dataframe(pd.DataFrame({"when": ["2026-06-26T00:00:00Z"], "value": [1]}))
    payload = summary.to_dict()
    assert payload["row_count"] == 1
    assert payload["numeric"]["value"]["max"] == 1
    assert payload["datetime"]["when"]["min"].startswith("2026-06-26T00:00:00")
