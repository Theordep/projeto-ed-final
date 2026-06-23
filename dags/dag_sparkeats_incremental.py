"""
DAG SparkEats — Carga Incremental
==================================
Executa apenas as tabelas de fato (novos registros desde a última execução)
e atualiza o modelo dimensional com os dados incrementais:
  Landing (incremental) → Bronze → Silver → Gold (incremental)

Agendamento: diário às 03:00
Checkpoints persistidos em Delta Lake (Gold) garantem idempotência.

Uso:
  Airflow UI → DAGs → sparkeats_pipeline_incremental → Trigger DAG
  
Pré-requisito:
  Executar sparkeats_pipeline_full ao menos uma vez antes desta DAG.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

_SRC = Path("/opt/airflow/src")
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# ---------------------------------------------------------------------------
# Callables
# ---------------------------------------------------------------------------


def _landing_incremental(**ctx) -> None:
    """Extrai apenas registros novos das tabelas fato (por PK/timestamp)."""
    from sparkeats.ingestion.landing import run
    run(incremental=True)


def _bronze(**ctx) -> None:
    """Reprocessa Landing → Bronze (overwrite total das tabelas afetadas)."""
    from sparkeats.bronze.bronze import run
    run()


def _silver(**ctx) -> None:
    """Reprocessa Bronze → Silver com regras de qualidade."""
    from sparkeats.silver.silver import run
    run()


def _gold_incremental(**ctx) -> None:
    """Append incremental em fato_pedidos usando checkpoint Delta."""
    from sparkeats.gold.gold import run
    run(incremental=True)


# ---------------------------------------------------------------------------
# Definição do DAG
# ---------------------------------------------------------------------------

default_args = {
    "owner": "sparkeats",
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="sparkeats_pipeline_incremental",
    default_args=default_args,
    description="Pipeline SparkEats — Carga Incremental diária (tabelas fato)",
    schedule_interval="0 3 * * *",  # diário às 03:00
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["sparkeats", "medallion", "incremental"],
    doc_md=__doc__,
) as dag:

    landing = PythonOperator(
        task_id="landing_incremental",
        python_callable=_landing_incremental,
        doc_md="Extração incremental: pedidos, itens_pedido, pagamentos, avaliacoes.",
    )

    bronze = PythonOperator(
        task_id="bronze",
        python_callable=_bronze,
        doc_md="Reprocessa Landing → Bronze (formato Delta, overwrite).",
    )

    silver = PythonOperator(
        task_id="silver",
        python_callable=_silver,
        doc_md="Reprocessa Bronze → Silver com qualidade e mascaramento.",
    )

    gold = PythonOperator(
        task_id="gold_incremental",
        python_callable=_gold_incremental,
        doc_md="Append incremental em fato_pedidos usando checkpoint de ID/data.",
    )

    landing >> bronze >> silver >> gold
