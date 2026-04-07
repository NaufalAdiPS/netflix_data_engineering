from pathlib import Path

from pipelines.extract import extract_csv, inspect_raw_data
from pipelines.load import (
    create_schema_if_not_exists,
    get_postgres_engine,
    load_to_postgres,
)
from pipelines.transform import GoldBuilder, SilverTransformer


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

RAW_FILES = {
    "users": RAW_DIR / "users.csv",
    "movies": RAW_DIR / "movies.csv",
    "watch_history": RAW_DIR / "watch_history.csv",
    "reviews": RAW_DIR / "reviews.csv",
    "search_logs": RAW_DIR / "search_logs.csv",
    "recommendation_logs": RAW_DIR / "recommendation_logs.csv",
}


def run_bronze_pipeline():
    engine = get_postgres_engine()
    create_schema_if_not_exists(engine, "bronze")

    for table_name, file_path in RAW_FILES.items():
        df = extract_csv(str(file_path))
        inspect_raw_data(df, table_name)
        load_to_postgres(df, table_name, "bronze", engine, if_exists="replace")

    print("Bronze pipeline completed successfully.")


def run_silver_pipeline():
    engine = get_postgres_engine()
    create_schema_if_not_exists(engine, "silver")

    transformer = SilverTransformer(engine)
    transformer.load_silver()

    print("Silver pipeline completed successfully.")


def run_gold_pipeline():
    engine = get_postgres_engine()
    create_schema_if_not_exists(engine, "gold")

    gold_builder = GoldBuilder(engine)
    gold_builder.build_all()

    print("Gold pipeline completed successfully.")


def run_full_pipeline():
    run_bronze_pipeline()
    run_silver_pipeline()
    run_gold_pipeline()

    print("Full pipeline completed successfully.")


if __name__ == "__main__":
    run_full_pipeline()