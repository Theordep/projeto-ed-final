"""Gold → PostgreSQL schema `analytics` (consumo pelo Metabase).

Lê cada tabela da camada Gold (Delta Lake) via PySpark,
converte para pandas e grava no schema `analytics` do PostgreSQL.
O Metabase se conecta a esse schema para alimentar o dashboard.
"""

from __future__ import annotations

from sparkeats.config import sqlalchemy_url
from sparkeats.spark_session import create_spark
from sparkeats.storage import gold_uri

# (tabela, filtro_spark_ou_None)
_GOLD_TABLES: list[tuple[str, str | None]] = [
    ("dim_tempo", None),
    ("dim_cliente", "ativo = true"),
    ("dim_restaurante", "ativo = true"),
    ("dim_entregador", None),
    ("dim_pagamento", None),
    ("fato_pedidos", None),
]


def _ensure_schema(conn_str: str) -> None:
    """Cria o schema analytics no PostgreSQL se ainda não existir."""
    import psycopg2
    from urllib.parse import urlparse

    parsed = urlparse(conn_str)
    with psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        dbname=parsed.path.lstrip("/"),
    ) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS analytics;")


def run() -> None:
    """Exporta tabelas Gold para PostgreSQL schema analytics."""
    print("=== Export Gold → PostgreSQL (analytics) ===")

    conn_str = sqlalchemy_url()
    _ensure_schema(conn_str)

    spark = create_spark("sparkeats-export-pg")

    from sqlalchemy import create_engine

    engine = create_engine(conn_str)

    for table, flt in _GOLD_TABLES:
        try:
            df = spark.read.format("delta").load(gold_uri(table))
            if flt:
                df = df.filter(flt)
            pdf = df.toPandas()
            pdf.to_sql(
                table,
                engine,
                schema="analytics",
                if_exists="replace",
                index=False,
                method="multi",
                chunksize=1000,
            )
            print(f"  [export] analytics.{table}: {len(pdf)} linhas")
        except Exception as exc:
            print(f"  [export] analytics.{table}: ERRO — {exc}")

    spark.stop()
    print("Export concluído.")


if __name__ == "__main__":
    run()
