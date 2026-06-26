"""Fulcra Analytics scaffold."""

from .loader import load_dataframe, load_records
from .statistics import summarize_records

__all__ = ["load_dataframe", "load_records", "summarize_records"]
__version__ = "0.1.0"
