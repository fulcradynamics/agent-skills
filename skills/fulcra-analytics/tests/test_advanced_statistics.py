from pathlib import Path

import pytest

from fulcra_analytics.loader import load_dataframe
from fulcra_analytics.statistics import (
    central_tendency,
    lasso_feature_selection,
    linear_regression,
    period_trend,
    variance_summary,
)

FIXTURE = Path(__file__).parent / "fixtures" / "first_olympiad_ml_stats_synthetic_v1.json"


def test_loads_generated_fulcra_fixture_rows():
    df = load_dataframe(FIXTURE)

    assert len(df) == 75
    assert {"timestamp", "sleep_hours", "focus_minutes", "daily_steps", "weekend"} <= set(df.columns)
    assert df.loc[0, "sleep_hours"] == pytest.approx(7.06)
    assert str(df["timestamp"].dtype).startswith("datetime64")


def test_central_tendency_and_variance_for_fixture_metric():
    df = load_dataframe(FIXTURE)

    tendency = central_tendency(df, "sleep_hours")
    variance = variance_summary(df, "sleep_hours")

    assert tendency["count"] == 75
    assert tendency["mean"] == pytest.approx(7.078, abs=0.01)
    assert tendency["median"] == pytest.approx(6.9, abs=0.01)
    assert variance["variance"] == pytest.approx(0.383, abs=0.01)
    assert variance["std"] == pytest.approx(0.619, abs=0.01)


def test_period_trend_models_metric_over_time():
    df = load_dataframe(FIXTURE)

    trend = period_trend(df, value_column="focus_minutes", time_column="timestamp")

    assert trend["count"] == 75
    assert trend["time_column"] == "timestamp"
    assert trend["value_column"] == "focus_minutes"
    assert trend["slope_per_day"] < 0
    assert trend["start"] == pytest.approx(371.0, abs=1)
    assert trend["end"] == pytest.approx(368.9, abs=1)


def test_linear_regression_predicts_focus_minutes_from_features():
    df = load_dataframe(FIXTURE)

    model = linear_regression(
        df,
        target="focus_minutes",
        features=["sleep_hours", "daily_steps", "weekend"],
    )

    assert model["target"] == "focus_minutes"
    assert model["features"] == ["sleep_hours", "daily_steps", "weekend"]
    assert model["count"] == 75
    assert model["r2"] > 0.45
    assert model["coefficients"]["sleep_hours"] > 0
    assert model["coefficients"]["daily_steps"] > 0
    assert model["predictions"][0] == pytest.approx(df.loc[0, "focus_minutes"], abs=45)


def test_lasso_feature_selection_identifies_useful_predictors():
    df = load_dataframe(FIXTURE)

    model = lasso_feature_selection(
        df,
        target="focus_minutes",
        features=["sleep_hours", "daily_steps", "weekend"],
        alpha=0.01,
    )

    assert model["target"] == "focus_minutes"
    assert model["count"] == 75
    assert model["selected_features"]
    assert "sleep_hours" in model["selected_features"]
    assert model["r2"] > 0.45
