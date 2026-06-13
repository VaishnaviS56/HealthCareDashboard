from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass
class DataQualityReport:
    row_count: int
    missing_values: dict[str, int]
    duplicate_records: int
    invalid_dates: int
    negative_values: dict[str, int]
    warnings: list[str]


def assess_data_quality(df: pd.DataFrame) -> DataQualityReport:
    row_count = len(df)
    missing_values = df.isna().sum().to_dict()
    duplicate_records = int(df.duplicated().sum())
    invalid_dates = int(df["date"].isna().sum()) if "date" in df.columns else 0

    negative_values = {}
    numeric_columns = df.select_dtypes(include=["number"]).columns
    for column in numeric_columns:
        if (df[column] < 0).any():
            negative_values[column] = int((df[column] < 0).sum())

    warnings = []
    if row_count == 0:
        warnings.append("No records were produced after retrieval.")
    incomplete_columns = [col for col, count in missing_values.items() if count > 0]
    if incomplete_columns:
        warnings.append(f"Missing values found in columns: {incomplete_columns}")
    if duplicate_records > 0:
        warnings.append(f"Found {duplicate_records} duplicate rows.")
    if invalid_dates > 0:
        warnings.append(f"Found {invalid_dates} invalid or unparsable date values.")
    if negative_values:
        warnings.append(f"Negative values found in numeric columns: {negative_values}")

    return DataQualityReport(
        row_count=row_count,
        missing_values={k: int(v) for k, v in missing_values.items()},
        duplicate_records=duplicate_records,
        invalid_dates=invalid_dates,
        negative_values=negative_values,
        warnings=warnings,
    )


def report_to_dict(report: DataQualityReport) -> dict[str, object]:
    return {
        "row_count": report.row_count,
        "missing_values": report.missing_values,
        "duplicate_records": report.duplicate_records,
        "invalid_dates": report.invalid_dates,
        "negative_values": report.negative_values,
        "warnings": report.warnings,
    }
