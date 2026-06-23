"""
DAG SparkEats — Carga Completa (Full Load)
==========================================
Executa o pipeline Medallion completo do zero:
  Landing → Bronze → Silver → Gold

Agendamento: semanal (domingos às 02:00)
Trigger manual disponível no Airflow UI.

Uso:
  Airflow UI → DAGs → sparkeats_pipeline_full → Trigger DAG
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

# Garante que o pacote sparkeats esteja no path dentro do container Airflow
_SRC = Path("/opt/airflow/src")
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# ---------------------------------------------------------------------------
# Callables — cada função executa uma camada do pipeline
# ---------------------------------------------------------------------------


def _landing_full(**ctx) -> None:
    """Extrai todas as tabelas OLTP do PostgreSQL → CSV na Landing Zone."""
    from sparkeats.ingestion.landing import run
    run(incremental=False)


def _bronze(**ctx) -> None:
    """Consolida CSVs da Landing → Delta Lake na camada Bronze."""
    from sparkeats.bronze.bronze import run
    run()


def _silver(**ctx) -> None:
    """Aplica regras de qualidade de dados Bronze → Silver."""
    from sparkeats.silver.silver import run
    run()


def _gold_full(**ctx) -> None:
    """Constrói modelo dimensional Kimball com SCD2 Silver → Gold."""
    from sparkeats.gold.gold import run
    run(incremental=False)


# ---------------------------------------------------------------------------
# Definição do DAG
# ---------------------------------------------------------------------------

default_args = {
    "owner": "sparkeats",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="sparkeats_pipeline_full",
    default_args=default_args,
    description="Pipeline SparkEats — Carga Completa (Landing → Bronze → Silver → Gold)",
    schedule_interval="0 2 * * 0",  # domingos às 02:00
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["sparkeats", "medallion", "full-load"],
    doc_md=__doc__,
) as dag:

    landing = PythonOperator(
        task_id="landing_full",
        python_callable=_landing_full,
        doc_md="Extração completa PostgreSQL → CSV (todas as 12 tabelas OLTP).",
    )

    bronze = PythonOperator(
        task_id="bronze",
        python_callable=_bronze,
        doc_md="CSV Landing → Delta Lake Bronze (adiciona metadados de ingestão).",
    )

    silver = PythonOperator(
        task_id="silver",
        python_callable=_silver,
        doc_md="Bronze → Silver: limpeza, dedup, máscaras LGPD, tipos corretos.",
    )

    gold = PythonOperator(
        task_id="gold_full",
        python_callable=_gold_full,
        doc_md=(
            "Silver → Gold: dim_tempo, dim_cliente (SCD2), dim_restaurante (SCD2), "
            "dim_entregador, dim_pagamento, fato_pedidos."
        ),
    )

    # Dependências: pipeline sequencial
    landing >> bronze >> silver >> gold
