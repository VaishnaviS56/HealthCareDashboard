from __future__ import annotations

import pandas as pd

AVAILABLE_SOURCES = ["source_a", "source_b", "source_c"]
AVAILABLE_DATASETS = ["regional_cases", "vaccination_progress", "hospital_capacity"]


def retrieve_selected_sources(dataset_key: str, sources: list[str]) -> pd.DataFrame:
    """Retrieve synthetic data for the selected dataset key from the selected sources."""
    dataset_key = dataset_key.lower().strip()
    if dataset_key not in AVAILABLE_DATASETS:
        raise ValueError(f"Dataset '{dataset_key}' is not available. Choose from {AVAILABLE_DATASETS}.")

    frames = []
    for source in sources:
        source_key = source.lower().strip()
        if source_key not in AVAILABLE_SOURCES:
            raise ValueError(f"Source '{source}' is not available. Choose from {AVAILABLE_SOURCES}.")
        frames.append(fetch_data_from_source(source_key, dataset_key))

    if not frames:
        raise ValueError("At least one valid source must be provided.")

    return pd.concat(frames, ignore_index=True, sort=False)


def fetch_data_from_source(source_name: str, dataset_key: str) -> pd.DataFrame:
    """Simulate a data retrieval operation from a source."""
    if dataset_key == "regional_cases":
        return _generate_regional_cases(source_name)
    if dataset_key == "vaccination_progress":
        return _generate_vaccination_progress(source_name)
    if dataset_key == "hospital_capacity":
        return _generate_hospital_capacity(source_name)
    raise ValueError(f"Unsupported dataset key '{dataset_key}'.")


def _generate_regional_cases(source_name: str) -> pd.DataFrame:
    if source_name == "source_a":
        return pd.DataFrame([
            {"region_name": "North City", "date_reported": "2026-06-10", "new_cases": 45, "population": 150000, "source": "Source A"},
            {"region_name": "south city ", "date_reported": "2026-06-10", "new_cases": 30, "population": 120000, "source": "Source A"},
            {"region_name": "East-town", "date_reported": "2026/06/10", "new_cases": None, "population": 90000, "source": "Source A"},
            {"region_name": "West Village", "date_reported": "10-06-2026", "new_cases": 12, "population": None, "source": "Source A"},
        ])
    if source_name == "source_b":
        return pd.DataFrame([
            {"region": "North City", "date": "2026-06-10", "cases": 44, "population": 150000, "source": "Source B"},
            {"region": "Old Town", "date": "2026-06-10", "cases": 8, "population": 54000, "source": "Source B"},
            {"region": "east town", "date": "2026-06-09", "cases": 15, "population": 90000, "source": "Source B"},
            {"region": "South City", "date": "2026-06-09", "cases": -1, "population": 120000, "source": "Source B"},
        ])
    return pd.DataFrame()


def _generate_vaccination_progress(source_name: str) -> pd.DataFrame:
    if source_name == "source_a":
        return pd.DataFrame([
            {"region_name": "North City", "date_reported": "2026-06-10", "people_vaccinated": 112000, "people_fully_vaccinated": 84000, "source": "Source A"},
            {"region_name": "South City", "date_reported": "2026-06-10", "people_vaccinated": None, "people_fully_vaccinated": 52000, "source": "Source A"},
            {"region_name": "East Town", "date_reported": "2026-06-10", "people_vaccinated": 78000, "people_fully_vaccinated": 56000, "source": "Source A"},
        ])
    if source_name == "source_b":
        return pd.DataFrame([
            {"region": "North City", "date": "2026-06-10", "vaccinated": 111000, "fully_vaccinated": 84000, "source": "Source B"},
            {"region": "Old Town", "date": "2026-06-10", "vaccinated": 42000, "fully_vaccinated": 32000, "source": "Source B"},
            {"region": "South City", "date": "2026-06-10", "vaccinated": 76000, "fully_vaccinated": None, "source": "Source B"},
        ])
    return pd.DataFrame()


def _generate_hospital_capacity(source_name: str) -> pd.DataFrame:
    if source_name == "source_a":
        return pd.DataFrame([
            {"region_name": "North City", "date_reported": "2026-06-10", "beds_available": 27, "beds_total": 120, "source": "Source A"},
            {"region_name": "South City", "date_reported": "2026-06-10", "beds_available": 19, "beds_total": 100, "source": "Source A"},
            {"region_name": "East Town", "date_reported": "2026-06-10", "beds_available": None, "beds_total": 90, "source": "Source A"},
        ])
    if source_name == "source_b":
        return pd.DataFrame([
            {"region": "North City", "date": "2026-06-10", "available_beds": 26, "total_beds": 120, "source": "Source B"},
            {"region": "Old Town", "date": "2026-06-10", "available_beds": 12, "total_beds": 60, "source": "Source B"},
            {"region": "South City", "date": "2026-06-10", "available_beds": 18, "total_beds": None, "source": "Source B"},
        ])
    return pd.DataFrame()
