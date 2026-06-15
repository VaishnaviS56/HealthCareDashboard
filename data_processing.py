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
    """Fill missing values and handle invalid dates based on column type."""

    for column in df.columns:

        # Detect datetime columns or columns with 'date' in the name
        if "date" in column.lower() or pd.api.types.is_datetime64_any_dtype(df[column]):

            # Convert invalid dates to NaT
            df[column] = pd.to_datetime(df[column], errors="coerce")

            # Fill missing/invalid dates with the most frequent valid date
            if df[column].notna().any():
                most_common_date = df[column].mode()[0]
                df[column] = df[column].fillna(most_common_date)
            else:
                # If all dates are invalid, use a default placeholder
                df[column] = df[column].fillna(pd.Timestamp("1970-01-01"))

        # Numeric columns
        elif pd.api.types.is_numeric_dtype(df[column]):
            median = df[column].median(skipna=True)
            df[column] = df[column].fillna(median if pd.notna(median) else 0)

        # Categorical/Text columns
        else:
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
