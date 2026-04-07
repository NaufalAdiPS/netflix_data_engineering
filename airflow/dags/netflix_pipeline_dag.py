from datetime import datetime, timedelta
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator

from pipelines.pipeline import (
    run_bronze_pipeline,
    run_silver_pipeline,
    run_gold_pipeline,
)


def bronze_callable():
    try:
        logging.info("Starting bronze pipeline...")
        run_bronze_pipeline()
        logging.info("Bronze pipeline completed successfully.")
    except Exception:
        logging.error("Error in bronze pipeline", exc_info=True)
        raise


def silver_callable():
    try:
        logging.info("Starting silver pipeline...")
        run_silver_pipeline()
        logging.info("Silver pipeline completed successfully.")
    except Exception:
        logging.error("Error in silver pipeline", exc_info=True)
        raise


def gold_callable():
    try:
        logging.info("Starting gold pipeline...")
        run_gold_pipeline()
        logging.info("Gold pipeline completed successfully.")
    except Exception:
        logging.error("Error in gold pipeline", exc_info=True)
        raise


default_args = {
    "owner": "data-engineering-team",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="netflix_batch_etl_pipeline",
    description="Batch ETL pipeline for Netflix medallion architecture",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
    tags=["batch", "etl", "netflix", "postgres", "medallion"],
) as dag:

    bronze_task = PythonOperator(
        task_id="bronze_task",
        python_callable=bronze_callable,
    )

    silver_task = PythonOperator(
        task_id="silver_task",
        python_callable=silver_callable,
    )

    gold_task = PythonOperator(
        task_id="gold_task",
        python_callable=gold_callable,
    )

    bronze_task >> silver_task >> gold_task