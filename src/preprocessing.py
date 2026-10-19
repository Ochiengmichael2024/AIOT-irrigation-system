"""Utilities for preparing raw smart-irrigation sensor data."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def load_raw_data(file_path: str | Path) -> pd.DataFrame:
    """Load a sensor dataset from a CSV file."""
    path = Path(file_path)
    if not path.is_absolute():
        path = RAW_DATA_DIR / path
    if not path.is_file():
        raise FileNotFoundError(f"Raw data file not found: {path}")
    return pd.read_csv(path)


def handle_missing_sensor_data(
    data: pd.DataFrame,
    sensor_columns: list[str] | None = None,
    limit: int = 3,
) -> pd.DataFrame:
    """Interpolate short sensor gaps, then fill remaining numeric sensor gaps."""
    cleaned = data.copy()
    columns = sensor_columns or cleaned.select_dtypes(include="number").columns.tolist()
    missing_columns = set(columns).difference(cleaned.columns)
    if missing_columns:
        raise ValueError(f"Sensor columns are missing from data: {sorted(missing_columns)}")

    if columns:
        cleaned[columns] = cleaned[columns].interpolate(
            method="linear", limit=limit, limit_direction="both"
        )
        cleaned[columns] = cleaned[columns].fillna(cleaned[columns].median())
    return cleaned


def save_processed_data(data: pd.DataFrame, file_name: str) -> Path:
    """Save a processed DataFrame as CSV under data/processed."""
    if Path(file_name).name != file_name or not file_name.lower().endswith(".csv"):
        raise ValueError("file_name must be a CSV filename without directory components")
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DATA_DIR / file_name
    data.to_csv(output_path, index=False)
    return output_path


def preprocess_file(
    file_path: str | Path,
    output_name: str | None = None,
    sensor_columns: list[str] | None = None,
) -> Path:
    """Load, clean, and save one raw sensor CSV."""
    data = load_raw_data(file_path)
    cleaned = handle_missing_sensor_data(data, sensor_columns=sensor_columns)
    destination = output_name or f"{Path(file_path).stem}_processed.csv"
    return save_processed_data(cleaned, destination)
