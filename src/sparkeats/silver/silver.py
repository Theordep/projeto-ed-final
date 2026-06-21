"""Bronze Delta → Silver (qualidade e padronização)."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, TimestampType

from sparkeats.config import OLTP_TABLES
from sparkeats.spark_session import create_spark
from sparkeats.storage import layer_uri, sync_to_minio


def _clean_pedidos(df: DataFrame) -> DataFrame:
    df = (
        df.withColumn("status_pedido", F.upper(F.trim(F.col("status_pedido"))))
        .withColumn("data_hora_pedido", F.col("data_hora_pedido").cast(TimestampType()))
        .withColumn("data_hora_coleta", F.col("data_hora_coleta").cast(TimestampType()))
        .withColumn("data_hora_entrega", F.col("data_hora_entrega").cast(TimestampType()))
        .filter(F.col("valor_total").cast(DoubleType()) > 0)
        .dropDuplicates(["id_pedido"])
    )
    return df.withColumn(
        "tempo_entrega_min",
        F.when(
            F.col("tempo_entrega_min").isNull()
            & (F.col("status_pedido") == "ENTREGUE")
            & F.col("data_hora_entrega").isNotNull(),
            (
                (
                    F.unix_timestamp("data_hora_entrega")
                    - F.unix_timestamp("data_hora_pedido")
                )
                / 60
            ).cast(IntegerType()),
        ).otherwise(F.col("tempo_entrega_min").cast(IntegerType())),
    )


def _clean_clientes(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("nome", F.trim(F.col("nome")))
        .withColumn("email", F.lower(F.trim(F.col("email"))))
        .withColumn(
            "cpf",
            F.when(
                F.col("cpf").isNotNull(),
                F.concat(F.lit("***.***.***-"), F.substring(F.col("cpf"), -2, 2)),
            ).otherwise(F.lit(None)),
        )
        .filter(F.col("status_ativo") == True)  # noqa: E712
        .dropDuplicates(["id_cliente"])
    )


def _clean_restaurantes(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("status", F.upper(F.trim(F.col("status"))))
        .withColumn("nome_fantasia", F.trim(F.col("nome_fantasia")))
        .filter(F.col("status") == "ATIVO")
        .dropDuplicates(["id_restaurante"])
    )


def _clean_enderecos(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("cidade", F.initcap(F.trim(F.col("cidade"))))
        .withColumn("bairro", F.initcap(F.trim(F.col("bairro"))))
        .withColumn("logradouro", F.trim(F.col("logradouro")))
        .dropDuplicates(["id_endereco"])
    )


def _clean_pagamentos(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("forma_pagamento", F.upper(F.trim(F.col("forma_pagamento"))))
        .withColumn("status_pagamento", F.upper(F.trim(F.col("status_pagamento"))))
        .filter(F.col("valor_pago").cast(DoubleType()) > 0)
        .dropDuplicates(["id_pagamento"])
    )


def _generic_clean(df: DataFrame) -> DataFrame:
    return df.dropDuplicates()


CLEANERS = {
    "pedidos": _clean_pedidos,
    "clientes": _clean_clientes,
    "restaurantes": _clean_restaurantes,
    "enderecos_cliente": _clean_enderecos,
    "pagamentos": _clean_pagamentos,
}


def run() -> None:
    print("=== Silver: Bronze → Delta (Data Quality) ===")
    spark = create_spark("sparkeats-silver")

    for table in OLTP_TABLES:
        source = layer_uri("bronze", table)
        try:
            df = spark.read.format("delta").load(source)
        except Exception:
            print(f"  [silver] {table}: bronze não encontrado")
            continue

        cleaner = CLEANERS.get(table, _generic_clean)
        silver_df = cleaner(df).withColumn(
            "_silver_processed_at", F.current_timestamp()
        )
        target = layer_uri("silver", table)
        silver_df.write.format("delta").mode("overwrite").save(target)
        print(f"  [silver] {table}: {silver_df.count()} linhas → {target}")

    spark.stop()
    sync_to_minio("silver")
    print("Silver concluída.")


if __name__ == "__main__":
    run()
