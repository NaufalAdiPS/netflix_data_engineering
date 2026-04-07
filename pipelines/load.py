import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_postgres_engine():
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB")

    if not all([user, password, host, port, db]):
        raise ValueError("PostgreSQL environment variables are incomplete.")

    conn_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(conn_string)


def create_schema_if_not_exists(engine, schema_name: str) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name};"))
    logging.info("Schema checked/created: %s", schema_name)


def load_to_postgres(
    df: pd.DataFrame,
    table_name: str,
    schema_name: str,
    engine,
    if_exists: str = "replace"
) -> None:
    logging.info("Loading data into %s.%s", schema_name, table_name)

    df.to_sql(
        name=table_name,
        con=engine,
        schema=schema_name,
        if_exists=if_exists,
        index=False
    )

    logging.info("Load complete: %s.%s | rows=%s", schema_name, table_name, len(df))