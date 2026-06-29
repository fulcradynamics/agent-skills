"""Fulcra Analytics scaffold."""

from .client import FulcraClient, FulcraClientError, default_client
from .loader import load_dataframe, load_records
from .statistics import DataFrameSummary, summarize_dataframe, summarize_records

__all__ = [
    "DataFrameSummary",
    "FulcraClient",
    "FulcraClientError",
    "default_client",
    "load_dataframe",
    "load_records",
    "summarize_dataframe",
    "summarize_records",
]
__version__ = "0.1.0"
