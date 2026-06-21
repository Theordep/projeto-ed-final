from __future__ import annotations

from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sparkeats.silver.silver import run as silver_run


def silver_task() -> None:
    silver_run()


def create_dag() -> DAG:
    with DAG(
        dag_id='dag_silver',
        description='Limpa e normaliza os dados do bronze para o bucket silver',
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
            task_id='run_silver',
            python_callable=silver_task,
        )
    return dag


dag = create_dag()
