"""Shared utilities for data hygiene and safe filenames."""
from __future__ import annotations

import re
import pandas as pd


def ensure_columns(df: pd.DataFrame, required: dict) -> dict:
    """
    Ensure a DataFrame has all required columns with sensible defaults.

    Args:
        df: input DataFrame (not modified in-place).
        required: mapping of column -> default value.

    Returns:
        dict with repair details: added_columns, coerced_columns, filled_values.
    """
    df = df.copy()
    added = []
    coerced = []
    filled = {}

    for col, default in required.items():
        if col not in df.columns:
            if default is None:
                # Use pandas NA to avoid fillna(None) errors
                df[col] = pd.Series([pd.NA] * len(df), dtype="object")
            else:
                df[col] = default
            added.append(col)
            filled[col] = len(df) if len(df) else 0
            continue

        series = df[col]

        # Numeric coercion when default is numeric
        if isinstance(default, (int, float)):
            coerced_series = pd.to_numeric(series, errors="coerce")
            if not coerced_series.equals(series):
                coerced.append(col)
            series = coerced_series

        # Fill invalid/NaN with default
        if isinstance(default, bool):
            # Normalize truthy strings/numbers to bool
            series = series.apply(_to_bool)
        filled_count = int(series.isna().sum())
        if filled_count:
            filled[col] = filled_count
        if default is None:
            # Leave as-is when default is None to avoid ValueError in fillna
            df[col] = series
        else:
            df[col] = series.fillna(default)

    return {
        "added_columns": added,
        "coerced_columns": coerced,
        "filled_values": filled,
    }, df


def _to_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value == 1
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def sanitize_filename(name: str) -> str:
    """
    Sanitize user/content-derived strings for safe filenames on Windows.
    """
    if name is None:
        return ""
    cleaned = str(name).strip()
    cleaned = re.sub(r'[\\/:\*\?"<>|]', "", cleaned)
    cleaned = cleaned.replace(" ", "_")
    return cleaned or "file"


__all__ = ["ensure_columns", "sanitize_filename"]
