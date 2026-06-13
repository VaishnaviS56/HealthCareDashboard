from __future__ import annotations

import argparse
import logging
import pathlib
import sys

from data_quality import assess_data_quality, report_to_dict
from data_retrieval import AVAILABLE_DATASETS, AVAILABLE_SOURCES, retrieve_selected_sources
from data_processing import clean_data

DEFAULT_OUTPUT_FILE = "output/clean_data.csv"


def prepare_clean_dataset(dataset_key: str, output_path: str, sources: list[str] | None = None) -> dict[str, object]:
    if sources is None:
        sources = AVAILABLE_SOURCES

    raw_data = retrieve_selected_sources(dataset_key, sources)
    cleaned_data = clean_data(raw_data)
    report = assess_data_quality(cleaned_data)

    output_file = pathlib.Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cleaned_data.to_csv(output_file, index=False)

    return report_to_dict(report)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a clean public health dataset CSV from selected sources.")
    parser.add_argument("dataset", choices=AVAILABLE_DATASETS, help="Select the dataset to process.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_FILE, help="Destination path for the cleaned CSV file.")
    parser.add_argument(
        "--sources",
        nargs="+",
        default=AVAILABLE_SOURCES,
        help=f"Data sources to include. Available: {', '.join(AVAILABLE_SOURCES)}.",
    )
    return parser.parse_args()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_arguments()

    try:
        report = prepare_clean_dataset(args.dataset, args.output, args.sources)
        logging.info("Clean CSV saved to %s", args.output)
        logging.info("Data quality report: %s", report)
        return 0
    except Exception as exc:
        logging.error("Failed to prepare dataset: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
