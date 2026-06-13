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


def _load_input_dataset(input_dir: str) -> pd.DataFrame:
    """Load all CSV files from the input directory."""
    input_path = pathlib.Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist.")

    csv_files = sorted(input_path.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in '{input_dir}'.")

    frames = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            df["source_file"] = csv_file.name
            frames.append(df)
            logging.info("Loaded CSV: %s", csv_file.name)
        except Exception as e:
            logging.warning("Failed to load %s: %s", csv_file.name, e)
            continue

    if not frames:
        raise ValueError(f"No CSV files could be loaded from '{input_dir}'.")

    return pd.concat(frames, ignore_index=True, sort=False)


def prepare_clean_dataset(
    dataset_key: str,
    preprocessed_dir: str,
    outputs_dir: str,
    csv_filename: str = DEFAULT_CSV_FILENAME,
    report_filename: str = DEFAULT_REPORT_FILENAME,
    input_dir: str = DEFAULT_INPUT_DIR,
) -> dict[str, object]:
    raw_data = _load_input_dataset(input_dir)
    cleaned_data = clean_data(raw_data)
    report = assess_data_quality(cleaned_data)

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
        "report.json",
        "input",
    )
    logging.info("Data quality summary: %s rows processed", report.get("row_count"))
    return report


if __name__ == "__main__":
    preprocess("input/cleaned_regional_cases.csv")
    # raise SystemExit(cli())
