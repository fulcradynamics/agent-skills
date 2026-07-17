---
type: Module Design
title: fulcra_analytics.statistics Implementation Notes
description: Descriptive statistics behavior for DataFrames produced by fulcra_analytics.loader.
---

# fulcra_analytics.statistics Implementation Notes

## Purpose

The `statistics` module computes descriptive summaries over `pandas.DataFrame` objects produced by the loader. It keeps outputs JSON-serializable so they can feed future OKF report generation.

## Public API

- `summarize_dataframe(df, group_by=None, top_n=10, metadata=None)`
- `summarize_column(series, top_n=10)`
- `summarize_numeric(series)`
- `summarize_datetime(series)`
- `summarize_categorical(series, top_n=10)`
- `summarize_boolean(series)`
- `summarize_groups(df, group_by)`
- `summarize_records(records)` for backward compatibility with the original scaffold
- `central_tendency(df, column)`
- `variance_summary(df, column)`
- `period_trend(df, value_column, time_column)`
- `linear_regression(df, target, features)`
- `lasso_feature_selection(df, target, features, alpha=1.0)`

## Summary categories

Columns are classified as:

- `numeric`: count, mean, standard deviation, min, max, sum, and 25/50/75% quantiles.
- `datetime`: count, min, max, and span in seconds.
- `categorical`: count, unique count, and top values.
- `boolean`: true/false counts and true fraction.

String columns are best-effort inferred as numeric or datetime when at least 80% of non-null values can be converted.

## Advanced statistics and ML

The module includes JSON-serializable helpers for Phase 2 analysis:

- `central_tendency` returns count, mean, median, mode, min, and max for a numeric column.
- `variance_summary` returns sample/population variance and standard deviation, range, and IQR.
- `period_trend` fits a simple scikit-learn linear model over elapsed days and reports slope per day, intercept, R², and fitted start/end values.
- `linear_regression` fits a scikit-learn `LinearRegression` model for one target and multiple numeric features.
- `lasso_feature_selection` fits a scaled scikit-learn `Lasso` model and reports features with non-zero coefficients.

These helpers drop incomplete numeric rows before fitting and raise `KeyError` for missing columns or `ValueError` when there is no usable numeric data.

## Grouped summaries

When `group_by` is provided, the module returns per-group row counts and numeric means. Group labels are stringified for JSON compatibility.

## Verification

Tests cover:

- backward-compatible record summaries,
- numeric, datetime, categorical, and boolean DataFrame columns,
- grouped summaries,
- inferred string numeric/datetime columns,
- JSON-friendly `DataFrameSummary.to_dict()` output,
- parsing the generated Fulcra synthetic fixture from `tests/fixtures/`,
- central tendency, variance, period trend, Linear Regression, and Lasso feature selection on that fixture.
