"""Descriptive statistics helpers for normalized Fulcra DataFrames."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any
import warnings

import numpy as np
import pandas as pd

from .schemas import SummaryResult


@dataclass
class ColumnSummary:
    """Serializable descriptive summary for one DataFrame column."""

    name: str
    dtype: str
    non_null: int
    missing: int
    missing_fraction: float
    unique: int
    kind: str
    stats: dict[str, Any] = field(default_factory=dict)


@dataclass
class DataFrameSummary:
    """Serializable descriptive summary for a pandas DataFrame."""

    row_count: int
    column_count: int
    columns: list[str]
    numeric: dict[str, dict[str, Any]] = field(default_factory=dict)
    datetime: dict[str, dict[str, Any]] = field(default_factory=dict)
    categorical: dict[str, dict[str, Any]] = field(default_factory=dict)
    boolean: dict[str, dict[str, Any]] = field(default_factory=dict)
    missing: dict[str, int] = field(default_factory=dict)
    groups: dict[str, dict[str, Any]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable dictionary."""

        return asdict(self)


def _is_missing(value: Any) -> bool:
    return value is None or value == ""


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool) or _is_missing(value):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(numeric):
        return None
    return numeric


def _json_scalar(value: Any) -> Any:
    """Convert pandas/numpy scalars into JSON-friendly Python values."""

    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, np.generic):
        return value.item()
    return value


def _quantiles(series: pd.Series, quantiles: Sequence[float]) -> dict[str, float | None]:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return {str(q): None for q in quantiles}
    result = values.quantile(list(quantiles))
    return {str(q): float(result.loc[q]) for q in quantiles}


def summarize_numeric(series: pd.Series, *, quantiles: Sequence[float] = (0.25, 0.5, 0.75)) -> dict[str, Any]:
    """Summarize a numeric-like pandas Series."""

    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return {"count": 0}

    return {
        "count": int(values.count()),
        "mean": float(values.mean()),
        "std": None if pd.isna(values.std(ddof=1)) else float(values.std(ddof=1)),
        "min": float(values.min()),
        "max": float(values.max()),
        "sum": float(values.sum()),
        "quantiles": _quantiles(values, quantiles),
    }


def summarize_datetime(series: pd.Series) -> dict[str, Any]:
    """Summarize a datetime-like pandas Series."""

    values = pd.to_datetime(series, errors="coerce", utc=True).dropna()
    if values.empty:
        return {"count": 0}

    minimum = values.min()
    maximum = values.max()
    return {
        "count": int(values.count()),
        "min": minimum.isoformat(),
        "max": maximum.isoformat(),
        "span_seconds": float((maximum - minimum).total_seconds()),
    }


def summarize_categorical(series: pd.Series, *, top_n: int = 10) -> dict[str, Any]:
    """Summarize a categorical/object pandas Series."""

    values = series.dropna()
    counts = values.astype("string").value_counts(dropna=True).head(top_n)
    return {
        "count": int(values.count()),
        "unique": int(values.nunique(dropna=True)),
        "top_values": {str(index): int(count) for index, count in counts.items()},
    }


def summarize_boolean(series: pd.Series) -> dict[str, Any]:
    """Summarize a boolean-like pandas Series."""

    values = series.dropna()
    counts = values.astype(bool).value_counts(dropna=True)
    true_count = int(counts.get(True, 0))
    false_count = int(counts.get(False, 0))
    total = true_count + false_count
    return {
        "count": total,
        "true": true_count,
        "false": false_count,
        "true_fraction": None if total == 0 else true_count / total,
    }


def infer_column_kind(series: pd.Series) -> str:
    """Classify a column for summary purposes."""

    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    clean = series.replace("", pd.NA).dropna()
    if clean.empty:
        return "categorical"

    lower_values = set(clean.astype(str).str.lower().unique())
    if lower_values <= {"true", "false", "0", "1"}:
        return "boolean"

    converted_numeric = pd.to_numeric(clean, errors="coerce")
    if converted_numeric.notna().sum() > 0 and converted_numeric.notna().mean() >= 0.8:
        return "numeric"

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        converted_datetime = pd.to_datetime(clean, errors="coerce", utc=True)
    if converted_datetime.notna().sum() > 0 and converted_datetime.notna().mean() >= 0.8:
        return "datetime"

    return "categorical"


def summarize_column(series: pd.Series, *, top_n: int = 10) -> ColumnSummary:
    """Return a descriptive summary for one DataFrame column."""

    missing = int(series.isna().sum())
    row_count = int(len(series))
    kind = infer_column_kind(series)

    if kind == "numeric":
        stats = summarize_numeric(series)
    elif kind == "datetime":
        stats = summarize_datetime(series)
    elif kind == "boolean":
        stats = summarize_boolean(series)
    else:
        stats = summarize_categorical(series, top_n=top_n)

    return ColumnSummary(
        name=str(series.name),
        dtype=str(series.dtype),
        non_null=row_count - missing,
        missing=missing,
        missing_fraction=0.0 if row_count == 0 else missing / row_count,
        unique=int(series.nunique(dropna=True)),
        kind=kind,
        stats=stats,
    )


def summarize_groups(
    df: pd.DataFrame,
    group_by: str | Sequence[str] | None,
    *,
    numeric_columns: Sequence[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Compute grouped row counts and numeric means.

    Group keys are stringified so the result is JSON serializable.
    """

    if group_by is None or df.empty:
        return {}

    keys = [group_by] if isinstance(group_by, str) else list(group_by)
    missing_keys = [key for key in keys if key not in df.columns]
    if missing_keys:
        raise KeyError(f"group_by column(s) not found: {missing_keys}")

    if numeric_columns is None:
        numeric_columns = [str(c) for c in df.select_dtypes(include="number").columns if c not in keys]

    grouped = df.groupby(keys, dropna=False)
    result: dict[str, dict[str, Any]] = {}
    for key, group in grouped:
        label = " | ".join(map(str, key if isinstance(key, tuple) else (key,)))
        summary: dict[str, Any] = {"row_count": int(len(group))}
        if numeric_columns:
            means = group[list(numeric_columns)].mean(numeric_only=True)
            summary["numeric_mean"] = {str(col): _json_scalar(value) for col, value in means.items()}
        result[label] = summary
    return result


def summarize_dataframe(
    df: pd.DataFrame,
    *,
    group_by: str | Sequence[str] | None = None,
    top_n: int = 10,
    metadata: Mapping[str, Any] | None = None,
) -> DataFrameSummary:
    """Compute descriptive summaries for a DataFrame produced by the loader."""

    columns = [str(column) for column in df.columns]
    column_summaries = [summarize_column(df[column], top_n=top_n) for column in df.columns]

    numeric: dict[str, dict[str, Any]] = {}
    datetime: dict[str, dict[str, Any]] = {}
    categorical: dict[str, dict[str, Any]] = {}
    boolean: dict[str, dict[str, Any]] = {}
    missing: dict[str, int] = {}

    for column in column_summaries:
        missing[column.name] = column.missing
        payload = {
            "dtype": column.dtype,
            "non_null": column.non_null,
            "missing": column.missing,
            "missing_fraction": column.missing_fraction,
            "unique": column.unique,
            **column.stats,
        }
        if column.kind == "numeric":
            numeric[column.name] = payload
        elif column.kind == "datetime":
            datetime[column.name] = payload
        elif column.kind == "boolean":
            boolean[column.name] = payload
        else:
            categorical[column.name] = payload

    return DataFrameSummary(
        row_count=int(len(df)),
        column_count=int(len(df.columns)),
        columns=columns,
        numeric=numeric,
        datetime=datetime,
        categorical=categorical,
        boolean=boolean,
        missing=missing,
        groups=summarize_groups(df, group_by),
        metadata=dict(metadata or {}),
    )


def summarize_records(records: list[dict[str, Any]]) -> SummaryResult:
    """Compute backward-compatible lightweight summaries for record dictionaries."""

    fields = sorted({key for record in records for key in record.keys()})
    missing = {field: 0 for field in fields}
    numeric_values: dict[str, list[float]] = {field: [] for field in fields}

    for record in records:
        for field_name in fields:
            value = record.get(field_name)
            if _is_missing(value):
                missing[field_name] += 1
            numeric = _as_float(value)
            if numeric is not None:
                numeric_values[field_name].append(numeric)

    numeric: dict[str, dict[str, float]] = {}
    for field_name, values in numeric_values.items():
        if not values:
            continue
        array = np.array(values, dtype=float)
        numeric[field_name] = {
            "count": float(len(values)),
            "min": float(array.min()),
            "max": float(array.max()),
            "mean": float(array.mean()),
        }

    return SummaryResult(row_count=len(records), fields=fields, numeric=numeric, missing=missing)


def _numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        raise KeyError(f"column not found: {column}")
    values = pd.to_numeric(df[column], errors="coerce").dropna()
    if values.empty:
        raise ValueError(f"column has no numeric values: {column}")
    return values.astype(float)


def central_tendency(df: pd.DataFrame, column: str) -> dict[str, Any]:
    """Return central tendency statistics for a numeric DataFrame column."""

    values = _numeric_series(df, column)
    return {
        "column": column,
        "count": int(values.count()),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "mode": [float(value) for value in values.mode().tolist()],
        "min": float(values.min()),
        "max": float(values.max()),
    }


def variance_summary(df: pd.DataFrame, column: str) -> dict[str, Any]:
    """Return variance and spread statistics for a numeric DataFrame column."""

    values = _numeric_series(df, column)
    q1 = float(values.quantile(0.25))
    q3 = float(values.quantile(0.75))
    return {
        "column": column,
        "count": int(values.count()),
        "variance": None if len(values) < 2 else float(values.var(ddof=1)),
        "std": None if len(values) < 2 else float(values.std(ddof=1)),
        "population_variance": float(values.var(ddof=0)),
        "population_std": float(values.std(ddof=0)),
        "range": float(values.max() - values.min()),
        "iqr": q3 - q1,
    }


def _model_frame(df: pd.DataFrame, *, target: str, features: Sequence[str]) -> pd.DataFrame:
    columns = [*features, target]
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise KeyError(f"column(s) not found: {missing}")
    model_df = df[columns].apply(pd.to_numeric, errors="coerce").dropna()
    if model_df.empty:
        raise ValueError("no complete numeric rows available for model fitting")
    return model_df


def period_trend(
    df: pd.DataFrame,
    *,
    value_column: str,
    time_column: str,
) -> dict[str, Any]:
    """Fit a simple linear trend for a value over time.

    The returned slope is expressed in value units per day.
    """

    if time_column not in df.columns:
        raise KeyError(f"column not found: {time_column}")
    if value_column not in df.columns:
        raise KeyError(f"column not found: {value_column}")

    model_df = pd.DataFrame(
        {
            time_column: pd.to_datetime(df[time_column], errors="coerce", utc=True),
            value_column: pd.to_numeric(df[value_column], errors="coerce"),
        }
    ).dropna()
    if len(model_df) < 2:
        raise ValueError("period_trend requires at least two complete observations")

    elapsed_days = (
        (model_df[time_column] - model_df[time_column].min()).dt.total_seconds() / 86400.0
    ).to_numpy().reshape(-1, 1)
    y = model_df[value_column].to_numpy(dtype=float)

    from sklearn.linear_model import LinearRegression

    regressor = LinearRegression().fit(elapsed_days, y)
    predictions = regressor.predict(elapsed_days)
    return {
        "time_column": time_column,
        "value_column": value_column,
        "count": int(len(model_df)),
        "slope_per_day": float(regressor.coef_[0]),
        "intercept": float(regressor.intercept_),
        "r2": float(regressor.score(elapsed_days, y)),
        "start": float(predictions[0]),
        "end": float(predictions[-1]),
        "start_time": model_df[time_column].iloc[0].isoformat(),
        "end_time": model_df[time_column].iloc[-1].isoformat(),
    }


def linear_regression(
    df: pd.DataFrame,
    *,
    target: str,
    features: Sequence[str],
) -> dict[str, Any]:
    """Fit a scikit-learn LinearRegression model and return JSON-safe diagnostics."""

    if not features:
        raise ValueError("linear_regression requires at least one feature")
    model_df = _model_frame(df, target=target, features=features)
    x = model_df[list(features)].to_numpy(dtype=float)
    y = model_df[target].to_numpy(dtype=float)

    from sklearn.linear_model import LinearRegression

    regressor = LinearRegression().fit(x, y)
    predictions = regressor.predict(x)
    return {
        "target": target,
        "features": list(features),
        "count": int(len(model_df)),
        "intercept": float(regressor.intercept_),
        "coefficients": {
            feature: float(coefficient) for feature, coefficient in zip(features, regressor.coef_)
        },
        "r2": float(regressor.score(x, y)),
        "predictions": [float(value) for value in predictions.tolist()],
    }


def lasso_feature_selection(
    df: pd.DataFrame,
    *,
    target: str,
    features: Sequence[str],
    alpha: float = 1.0,
    max_iter: int = 10000,
) -> dict[str, Any]:
    """Fit a scikit-learn Lasso model and report non-zero selected features."""

    if not features:
        raise ValueError("lasso_feature_selection requires at least one feature")
    model_df = _model_frame(df, target=target, features=features)
    x = model_df[list(features)].to_numpy(dtype=float)
    y = model_df[target].to_numpy(dtype=float)

    from sklearn.linear_model import Lasso
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    pipeline = make_pipeline(StandardScaler(), Lasso(alpha=alpha, max_iter=max_iter))
    pipeline.fit(x, y)
    regressor = pipeline.named_steps["lasso"]
    coefficients = {
        feature: float(coefficient) for feature, coefficient in zip(features, regressor.coef_)
    }
    predictions = pipeline.predict(x)
    selected = [feature for feature, coefficient in coefficients.items() if abs(coefficient) > 1e-9]
    return {
        "target": target,
        "features": list(features),
        "count": int(len(model_df)),
        "alpha": float(alpha),
        "intercept": float(regressor.intercept_),
        "coefficients": coefficients,
        "selected_features": selected,
        "r2": float(pipeline.score(x, y)),
        "predictions": [float(value) for value in predictions.tolist()],
    }
