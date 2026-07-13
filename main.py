from __future__ import annotations

import argparse
import json
import logging
import pathlib

import pandas as pd

from data_quality import assess_data_quality, report_to_dict
from data_processing import clean_data

DEFAULT_INPUT_DIR = "input"
DEFAULT_PREPROCESSED_DIR = "preprocessed"
DEFAULT_OUTPUTS_DIR = "outputs"
DEFAULT_CSV_FILENAME = "clean_data.csv"
DEFAULT_REPORT_FILENAME = "data_quality_report.json"


def _load_input_dataset(input_path: str) -> pd.DataFrame:
    """Load only the explicitly provided CSV file."""
    csv_file = pathlib.Path(input_path)
    if not csv_file.exists() or not csv_file.is_file():
        raise FileNotFoundError(f"CSV file '{input_path}' does not exist.")
    if csv_file.suffix.lower() != ".csv":
        raise ValueError(f"Input file '{input_path}' is not a CSV file.")

    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        raise ValueError(f"Failed to load CSV file '{input_path}': {e}") from e

    df["source_file"] = csv_file.name
    logging.info("Loaded CSV: %s", csv_file.name)
    return df


def prepare_clean_dataset(
    dataset_key: str,
    preprocessed_dir: str,
    outputs_dir: str,
    csv_filename: str = DEFAULT_CSV_FILENAME,
    report_filename: str = DEFAULT_REPORT_FILENAME,
    input_path: str = DEFAULT_INPUT_DIR,
) -> dict[str, object]:
    raw_data = _load_input_dataset(dataset_key)
    cleaned_data = clean_data(raw_data)
    report = assess_data_quality(raw_data)

    preprocessed_path = pathlib.Path(preprocessed_dir)
    preprocessed_path.mkdir(parents=True, exist_ok=True)

    csv_file = preprocessed_path / csv_filename
    cleaned_data.to_csv(csv_file, index=False)

    outputs_path = pathlib.Path(outputs_dir)
    outputs_path.mkdir(parents=True, exist_ok=True)

    report_file = outputs_path / report_filename
    report_file.write_text(json.dumps(report_to_dict(report), indent=2), encoding="utf-8")

    return report_to_dict(report)

def preprocess(dataset) -> dict[str, object]:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    report = prepare_clean_dataset(
        dataset,
        "preprocessed",
        "outputs",
        "preprocessed_data.csv",
        "quality_report.json",
        "input",
    )
    logging.info("Data quality summary: %s rows processed", report.get("row_count"))
    return report
