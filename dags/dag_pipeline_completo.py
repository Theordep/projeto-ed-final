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
from sparkeats.bronze.bronze import run as bronze_run
from sparkeats.silver.silver import run as silver_run
from sparkeats.gold.gold import run as gold_run


def landing_task() -> None:
    """Extrai tabelas do PostgreSQL para MinIO landing zone"""
    context = get_current_context()
    dag_run = context.get('dag_run')
    incremental = False
    if dag_run and dag_run.conf:
        incremental = dag_run.conf.get('incremental', False)
    landing_run(incremental=incremental)


def bronze_task() -> None:
    """Converte CSVs da landing para Delta Lake no bucket bronze"""
    bronze_run()


def silver_task() -> None:
    """Limpa e normaliza dados do bronze para o bucket silver"""
    silver_run()


def gold_task() -> None:
    """Constrói o modelo dimensional no bucket gold"""
    context = get_current_context()
    dag_run = context.get('dag_run')
    incremental = False
    if dag_run and dag_run.conf:
        incremental = dag_run.conf.get('incremental', False)
    gold_run(incremental=incremental)


def create_dag() -> DAG:
    with DAG(
        dag_id='dag_pipeline_completo',
        description='Pipeline completo: landing → bronze → silver → gold. Executa em sequência automaticamente.',
        schedule_interval='0 0 * * *',
        start_date=days_ago(1),
        catchup=False,
        default_args={
            'owner': 'spark-eats',
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        },
    ) as dag:
        task_landing = PythonOperator(
            task_id='run_landing',
            python_callable=landing_task,
        )
        
        task_bronze = PythonOperator(
            task_id='run_bronze',
            python_callable=bronze_task,
        )
        
        task_silver = PythonOperator(
            task_id='run_silver',
            python_callable=silver_task,
        )
        
        task_gold = PythonOperator(
            task_id='run_gold',
            python_callable=gold_task,
        )
        
        # Define a sequência: cada task depende da anterior
        task_landing >> task_bronze >> task_silver >> task_gold
    
    return dag


dag = create_dag()
