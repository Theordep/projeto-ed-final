from __future__ import annotations

from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator, get_current_context
from airflow.utils.dates import days_ago

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sparkeats.ingestion.landing import run as landing_run


def landing_task() -> None:
    context = get_current_context()
    dag_run = context.get('dag_run')
    incremental = False
    if dag_run and dag_run.conf:
        incremental = dag_run.conf.get('incremental', False)
    landing_run(incremental=incremental)


def create_dag() -> DAG:
    with DAG(
        dag_id='dag_landing',
        description='Extrai tabelas do PostgreSQL e grava CSVs no MinIO (landing-zone)',
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
            task_id='run_landing',
            python_callable=landing_task,
        )
    return dag


dag = create_dag()
