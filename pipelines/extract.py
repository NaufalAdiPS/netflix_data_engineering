import logging
from pathlib import Path

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_csv(file_path: str) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    logging.info("Reading file from: %s", file_path)
    df = pd.read_csv(file_path)
    logging.info("Successfully read file: %s | rows=%s | cols=%s", file_path, len(df), len(df.columns))

    return df


def inspect_raw_data(df: pd.DataFrame, table_name: str) -> None:
    logging.info("Inspecting raw data for table: %s", table_name)
    logging.info("Shape: %s", df.shape)
    logging.info("Columns: %s", list(df.columns))
    logging.info("Head:\n%s", df.head(3))