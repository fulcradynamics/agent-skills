"""Fulcra Analytics scaffold."""

from .client import FulcraClient, FulcraClientError, default_client
from .loader import load_dataframe, load_records
from .statistics import (
    DataFrameSummary,
    central_tendency,
    lasso_feature_selection,
    linear_regression,
    period_trend,
    summarize_dataframe,
    summarize_records,
    variance_summary,
)

__all__ = [
    "DataFrameSummary",
    "FulcraClient",
    "FulcraClientError",
    "central_tendency",
    "default_client",
    "lasso_feature_selection",
    "linear_regression",
    "load_dataframe",
    "load_records",
    "period_trend",
    "summarize_dataframe",
    "summarize_records",
    "variance_summary",
]
__version__ = "0.1.0"
