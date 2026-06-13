from __future__ import annotations

import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Generic data cleaning, normalization, and standardization for any CSV dataset."""
    df = df.copy()

    # Normalize column names: lowercase and strip whitespace
    df.columns = [col.strip().lower() for col in df.columns]

    # Handle missing values generically
    df = _fill_missing_values(df)

    # Remove duplicate rows
    df = _remove_duplicate_records(df)

    # Normalize text/string columns
    df = _normalize_text_columns(df)

    # Parse date-like columns
    df = _parse_datetime_columns(df)

    # Convert and standardize numeric columns
    df = _standardize_numeric_columns(df)

    # Remove negative values from numeric columns (data quality)
    df = _remove_invalid_numeric_values(df)

    return df.reset_index(drop=True)


def _fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values based on column type."""
    for column in df.columns:
        if df[column].dtype in ["float64", "int64"]:
            # For numeric: use median
            median = df[column].median(skipna=True)
            df[column] = df[column].fillna(median if pd.notna(median) else 0)
        else:
            # For non-numeric: use "Unknown"
            df[column] = df[column].fillna("Unknown")
    return df


def _normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize string/text columns: strip, lowercase, title case for consistency."""
    for column in df.columns:
        if df[column].dtype == "object":
            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
                .str.lower()
            )
            # Title case for categorical-like columns (heuristic: few unique values)
            if df[column].nunique() < 50 and df[column].nunique() < len(df) * 0.5:
                df[column] = df[column].str.title()
    return df


def _parse_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Detect and parse date-like columns."""
    for column in df.columns:
        if "date" in column.lower() or "time" in column.lower():
            try:
                df[column] = pd.to_datetime(df[column], errors="coerce")
            except Exception:
                pass
    return df


def _standardize_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert all numeric columns to float and ensure consistency."""
    numeric_columns = df.select_dtypes(include=["number"]).columns
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(float)
    return df


def _remove_invalid_numeric_values(df: pd.DataFrame) -> pd.DataFrame:
    """Remove obviously invalid numeric values (negatives where they don't make sense)."""
    numeric_columns = df.select_dtypes(include=["number"]).columns
    for column in numeric_columns:
        # Flag columns that shouldn't have negative values (heuristic: count/quantity columns)
        if any(keyword in column.lower() for keyword in ["count", "total", "population", "cases", "beds", "vaccin", "available"]):
            df.loc[df[column] < 0, column] = 0
    return df


def _remove_duplicate_records(df: pd.DataFrame) -> pd.DataFrame:
    """Remove fully duplicate rows, keeping the last occurrence."""
    df = df.drop_duplicates(keep="last")
    return df
