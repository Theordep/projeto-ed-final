from __future__ import annotations

from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sparkeats.bronze.bronze import run as bronze_run


def bronze_task() -> None:
    bronze_run()


def create_dag() -> DAG:
    with DAG(
        dag_id='dag_bronze',
        description='Converte CSVs da landing para Delta Lake no bucket bronze',
        schedule_interval=None,
        start_date=days_ago(1),
        catchup=False,
        default_args={
            'owner': 'spark-eats',
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        },
    ) as dag:
        PythonOperator(
            task_id='run_bronze',
            python_callable=bronze_task,
        )
    return dag


dag = create_dag()
