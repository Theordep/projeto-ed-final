"""Configurações centralizadas do pipeline SparkEats."""

from __future__ import annotations

import os
from datetime import date

PROJECT_ROOT = os.getenv("PROJECT_ROOT", "/mnt/c/projeto-ed-final")

os.environ.setdefault("PROJECT_ROOT", PROJECT_ROOT)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9090")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", os.getenv("MINIO_ROOT_USER", "minioadmin"))
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"))

POSTGRES_DB = os.getenv("POSTGRES_DB", "sparkeats")
POSTGRES_USER = os.getenv("POSTGRES_USER", "sparkeats")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "sparkeats_dev")


def _db_host() -> str:
    return os.getenv("POSTGRES_HOST", "localhost")


def _db_port() -> str:
    return os.getenv("POSTGRES_PORT", "5433")


def jdbc_url() -> str:
    host = _db_host()
    port = _db_port()
    return (
        f"jdbc:postgresql://{host}:{port}/{POSTGRES_DB}"
        f"?user={POSTGRES_USER}&password={POSTGRES_PASSWORD}"
    )


def sqlalchemy_url() -> str:
    host = _db_host()
    port = _db_port()
    return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{host}:{port}/{POSTGRES_DB}"


BUCKETS = {
    "landing": "landing-zone",
    "bronze": "bronze",
    "silver": "silver",
    "gold": "gold",
}

OLTP_TABLES = [
    "categorias_restaurante",
    "zonas_entrega",
    "cupons",
    "restaurantes",
    "cardapio",
    "clientes",
    "enderecos_cliente",
    "entregadores",
    "pedidos",
    "itens_pedido",
    "pagamentos",
    "avaliacoes",
]

INCREMENTAL_TABLES = ["pedidos", "itens_pedido", "pagamentos", "avaliacoes"]

SPARK_PACKAGES = (
    "io.delta:delta-spark_2.12:3.2.0,"
    "org.apache.hadoop:hadoop-aws:3.3.4,"
    "com.amazonaws:aws-java-sdk-bundle:1.12.262"
)

MINIO_CONTAINER = os.getenv("MINIO_CONTAINER", "projeto-ed-minio")

CHECKPOINT_DEFAULT_DATE = date(2020, 1, 1)
CHECKPOINT_DEFAULT_ID = 0

MESES_PT = {
    1: "janeiro",
    2: "fevereiro",
    3: "marco",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
}

DIAS_PT = {
    0: "segunda-feira",
    1: "terca-feira",
    2: "quarta-feira",
    3: "quinta-feira",
    4: "sexta-feira",
    5: "sabado",
    6: "domingo",
}
