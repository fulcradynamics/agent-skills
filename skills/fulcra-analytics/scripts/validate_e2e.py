#!/usr/bin/env python3
"""End-to-end validation for the Fulcra Analytics fixture pipeline.

This script exercises the public package and CLI on the generated First Olympiad
ML/stats fixture:

1. load fixture JSON into a DataFrame,
2. produce descriptive DataFrame summaries,
3. run central tendency and variance helpers,
4. fit period-trend, Linear Regression, and Lasso models,
5. invoke the installed `fulcra-analytics file` CLI and parse its JSON output.

It exits non-zero on validation failure and prints a JSON report on success.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from fulcra_analytics.loader import load_dataframe
from fulcra_analytics.statistics import (
    central_tendency,
    lasso_feature_selection,
    linear_regression,
    period_trend,
    summarize_dataframe,
    variance_summary,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "first_olympiad_ml_stats_synthetic_v1.json"


def require(condition: bool, message: str) -> None:
    """Raise an AssertionError with a readable validation message."""

    if not condition:
        raise AssertionError(message)


def run_cli_fixture_summary() -> dict[str, Any]:
    """Run the package CLI against the fixture and return parsed JSON."""

    result = subprocess.run(
        ["uv", "run", "fulcra-analytics", "file", str(FIXTURE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "fulcra-analytics file command failed: "
            f"stdout={result.stdout[:500]!r} stderr={result.stderr[:500]!r}"
        )
    return json.loads(result.stdout)


def main() -> int:
    """Run the end-to-end validation and print a compact JSON report."""

    df = load_dataframe(FIXTURE)
    require(len(df) == 75, f"expected 75 fixture rows, found {len(df)}")
    required_columns = {"timestamp", "sleep_hours", "focus_minutes", "daily_steps", "weekend"}
    require(required_columns <= set(df.columns), f"missing columns: {required_columns - set(df.columns)}")
    require(str(df["timestamp"].dtype).startswith("datetime64"), "timestamp was not coerced")

    summary = summarize_dataframe(df, metadata={"fixture": str(FIXTURE)})
    require(summary.row_count == 75, "descriptive summary row count mismatch")
    require("focus_minutes" in summary.numeric, "focus_minutes missing from numeric summary")
    require("timestamp" in summary.datetime, "timestamp missing from datetime summary")

    sleep_tendency = central_tendency(df, "sleep_hours")
    sleep_variance = variance_summary(df, "sleep_hours")
    require(7.0 < sleep_tendency["mean"] < 7.2, "sleep mean outside expected range")
    require(sleep_variance["variance"] > 0, "sleep variance should be positive")

    focus_trend = period_trend(df, value_column="focus_minutes", time_column="timestamp")
    require(focus_trend["count"] == 75, "trend row count mismatch")
    require(focus_trend["slope_per_day"] < 0, "expected slight negative focus trend")

    regression = linear_regression(
        df,
        target="focus_minutes",
        features=["sleep_hours", "daily_steps", "weekend"],
    )
    require(regression["count"] == 75, "linear regression row count mismatch")
    require(regression["r2"] > 0.45, "linear regression R² below expected fixture threshold")
    require(regression["coefficients"]["sleep_hours"] > 0, "sleep coefficient should be positive")

    lasso = lasso_feature_selection(
        df,
        target="focus_minutes",
        features=["sleep_hours", "daily_steps", "weekend"],
        alpha=0.01,
    )
    require(lasso["count"] == 75, "lasso row count mismatch")
    require("sleep_hours" in lasso["selected_features"], "lasso did not select sleep_hours")

    cli_summary = run_cli_fixture_summary()
    require(cli_summary["row_count"] == 75, "CLI summary row count mismatch")
    require("focus_minutes" in cli_summary["numeric"], "CLI numeric summary missing focus_minutes")

    report = {
        "status": "pass",
        "fixture": str(FIXTURE.relative_to(ROOT)),
        "rows": int(len(df)),
        "columns": list(map(str, df.columns)),
        "descriptive_summary": {
            "numeric_columns": sorted(summary.numeric),
            "datetime_columns": sorted(summary.datetime),
        },
        "central_tendency": {
            "sleep_hours_mean": sleep_tendency["mean"],
            "sleep_hours_median": sleep_tendency["median"],
        },
        "variance": {
            "sleep_hours_variance": sleep_variance["variance"],
            "sleep_hours_std": sleep_variance["std"],
        },
        "period_trend": {
            "focus_minutes_slope_per_day": focus_trend["slope_per_day"],
            "r2": focus_trend["r2"],
        },
        "linear_regression": {
            "r2": regression["r2"],
            "coefficients": regression["coefficients"],
        },
        "lasso": {
            "r2": lasso["r2"],
            "selected_features": lasso["selected_features"],
        },
        "cli": {
            "row_count": cli_summary["row_count"],
            "numeric_columns": sorted(cli_summary["numeric"]),
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"E2E validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
