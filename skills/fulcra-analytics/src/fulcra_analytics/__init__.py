"""Fulcra Analytics scaffold."""

from .loader import load_dataframe, load_records
from .statistics import DataFrameSummary, summarize_dataframe, summarize_records

__all__ = [
    "DataFrameSummary",
    "load_dataframe",
    "load_records",
    "summarize_dataframe",
    "summarize_records",
]
__version__ = "0.1.0"
