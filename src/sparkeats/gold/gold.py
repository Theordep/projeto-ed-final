"""Silver → Gold (modelo dimensional Kimball + SCD2 + checkpoint)."""

from __future__ import annotations

from datetime import date

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F
from pyspark.sql.types import BooleanType, DateType, IntegerType, LongType

from sparkeats.config import (
    CHECKPOINT_DEFAULT_DATE,
    CHECKPOINT_DEFAULT_ID,
    DIAS_PT,
    MESES_PT,
)
from sparkeats.spark_session import create_spark
from sparkeats.storage import gold_uri, layer_uri, sync_to_minio


def _silver(spark: SparkSession, table: str) -> DataFrame:
    return spark.read.format("delta").load(layer_uri("silver", table))


def build_dim_tempo(spark: SparkSession, start: str = "2023-01-01", end: str = "2026-12-31") -> DataFrame:
    dia_map = F.create_map(*[x for kv in DIAS_PT.items() for x in (F.lit(kv[0]), F.lit(kv[1]))])
    df = (
        spark.sql(
            f"SELECT sequence(to_date('{start}'), to_date('{end}'), interval 1 day) as datas"
        )
        .withColumn("data", F.explode("datas"))
        .withColumn("sk_tempo", F.date_format("data", "yyyyMMdd").cast(LongType()))
        .withColumn("ano", F.year("data"))
        .withColumn("mes", F.month("data"))
        .withColumn("dia", F.dayofmonth("data"))
        .withColumn("numero_dia_semana", F.dayofweek("data"))
        .withColumn("dia_semana", dia_map[((F.col("numero_dia_semana") + 5) % 7)])
        .withColumn("trimestre", F.quarter("data"))
        .withColumn(
            "fim_de_semana",
            F.col("numero_dia_semana").isin(1, 7),
        )
    )
    return df.select(
        "sk_tempo",
        "data",
        "ano",
        "mes",
        "dia",
        "dia_semana",
        "trimestre",
        "fim_de_semana",
    )


def build_dim_cliente_source(spark: SparkSession) -> DataFrame:
    clientes = _silver(spark, "clientes").select("id_cliente", "nome")
    enderecos = (
        _silver(spark, "enderecos_cliente")
        .filter(F.col("principal") == True)  # noqa: E712
        .select("id_cliente", "cidade", "estado", "bairro")
    )
    return clientes.join(enderecos, "id_cliente", "left")


def build_dim_restaurante_source(spark: SparkSession) -> DataFrame:
    restaurantes = _silver(spark, "restaurantes")
    categorias = _silver(spark, "categorias_restaurante").select(
        F.col("id_categoria"), F.col("nome").alias("categoria")
    )
    zonas = _silver(spark, "zonas_entrega").select(
        F.col("id_zona"),
        F.col("nome_bairro").alias("zona"),
        "cidade",
    )
    return (
        restaurantes.join(categorias, "id_categoria", "left")
        .join(zonas, "id_zona", "left")
        .select(
            "id_restaurante",
            "nome_fantasia",
            "categoria",
            "zona",
            "cidade",
            F.col("taxa_comissao").cast("double"),
        )
    )


def apply_scd2(
    spark: SparkSession,
    source_df: DataFrame,
    target_path: str,
    sk_name: str,
    key_col: str,
    track_cols: list[str],
) -> None:
    today = date.today()
    staging = (
        source_df.withColumn("dt_inicio", F.lit(today).cast(DateType()))
        .withColumn("dt_fim", F.lit(date(9999, 12, 31)).cast(DateType()))
        .withColumn("ativo", F.lit(True).cast(BooleanType()))
    )

    if not DeltaTable.isDeltaTable(spark, target_path):
        final = staging.withColumn(
            sk_name, F.row_number().over(Window.orderBy(key_col)).cast(LongType())
        )
        final.write.format("delta").mode("overwrite").save(target_path)
        print(f"  [gold] SCD2 inicial: {target_path.split('/')[-1]} ({final.count()} linhas)")
        return

    current = spark.read.format("delta").load(target_path).filter("ativo = true")
    condition = None
    for col_name in track_cols:
        expr = F.col(f"s.{col_name}").eqNullSafe(F.col(f"c.{col_name}")) == False  # noqa: E712
        condition = expr if condition is None else (condition | expr)

    changes = (
        staging.alias("s")
        .join(current.alias("c"), key_col, "inner")
        .filter(condition)
        .select(F.col(f"s.{key_col}").alias(key_col))
        .distinct()
    )
    change_keys = [r[key_col] for r in changes.collect()]

    if change_keys:
        delta = DeltaTable.forPath(spark, target_path)
        for key in change_keys:
            delta.update(
                condition=f"ativo = true AND {key_col} = {key}",
                set={"dt_fim": F.lit(today), "ativo": F.lit(False)},
            )
        max_sk = spark.read.format("delta").load(target_path).agg(F.max(sk_name)).collect()[0][0]
        new_rows = staging.filter(F.col(key_col).isin(change_keys)).withColumn(
            sk_name,
            F.row_number().over(Window.orderBy(key_col)) + F.lit(max_sk or 0),
        )
        new_rows.write.format("delta").mode("append").save(target_path)
        print(f"  [gold] SCD2 alterações: {len(change_keys)} em {target_path.split('/')[-1]}")

    existing_keys = spark.read.format("delta").load(target_path).select(key_col).distinct()
    new_only = staging.join(existing_keys, key_col, "left_anti")
    new_count = new_only.count()
    if new_count > 0:
        max_sk = spark.read.format("delta").load(target_path).agg(F.max(sk_name)).collect()[0][0]
        new_rows = new_only.withColumn(
            sk_name,
            F.row_number().over(Window.orderBy(key_col)) + F.lit(max_sk or 0),
        )
        new_rows.write.format("delta").mode("append").save(target_path)
        print(f"  [gold] SCD2 novos registros: {new_count} em {target_path.split('/')[-1]}")


def build_dim_entregador(spark: SparkSession) -> DataFrame:
    entregadores = _silver(spark, "entregadores")
    zonas = _silver(spark, "zonas_entrega").select(
        F.col("id_zona"), F.col("nome_bairro").alias("zona")
    )
    return (
        entregadores.join(zonas, "id_zona", "left")
        .select(
            F.col("id_entregador"),
            "nome",
            "veiculo",
            "zona",
        )
        .withColumn(
            "sk_entregador",
            F.row_number().over(Window.orderBy("id_entregador")).cast(LongType()),
        )
    )


def build_dim_pagamento(spark: SparkSession) -> DataFrame:
    pagamentos = _silver(spark, "pagamentos").select("forma_pagamento", "status_pagamento").distinct()
    return pagamentos.withColumn(
        "sk_pagamento",
        F.row_number().over(Window.orderBy("forma_pagamento", "status_pagamento")).cast(LongType()),
    )


def read_fato_checkpoint(spark: SparkSession) -> tuple[date, int]:
    path = gold_uri("checkpoint_fato_pedidos")
    if not DeltaTable.isDeltaTable(spark, path):
        return CHECKPOINT_DEFAULT_DATE, CHECKPOINT_DEFAULT_ID
    row = spark.read.format("delta").load(path).collect()[0]
    return row["ultima_data_processada"], int(row["ultimo_id_processado"])


def write_fato_checkpoint(spark: SparkSession, ultima_data: date, ultimo_id: int) -> None:
    path = gold_uri("checkpoint_fato_pedidos")
    df = spark.createDataFrame(
        [("fato_pedidos", ultima_data, ultimo_id)],
        "nome_processo string, ultima_data_processada date, ultimo_id_processado long",
    ).withColumn("atualizado_em", F.current_timestamp())
    df.write.format("delta").mode("overwrite").save(path)


def _assign_sk_pedido(spark: SparkSession, fato: DataFrame, target: str, incremental: bool) -> DataFrame:
    if incremental and DeltaTable.isDeltaTable(spark, target):
        max_sk = spark.read.format("delta").load(target).agg(F.max("sk_pedido")).collect()[0][0] or 0
        return fato.withColumn(
            "sk_pedido",
            (F.row_number().over(Window.orderBy("id_pedido")) + F.lit(max_sk)).cast(LongType()),
        )
    return fato.withColumn(
        "sk_pedido",
        F.row_number().over(Window.orderBy("id_pedido")).cast(LongType()),
    )


def build_fato_pedidos(spark: SparkSession, incremental: bool) -> DataFrame:
    pedidos = _silver(spark, "pedidos")
    if incremental:
        ultima_data, ultimo_id = read_fato_checkpoint(spark)
        pedidos = pedidos.filter(
            (F.col("data_hora_pedido").cast("date") > F.lit(ultima_data))
            | (
                (F.col("data_hora_pedido").cast("date") == F.lit(ultima_data))
                & (F.col("id_pedido") > ultimo_id)
            )
        )

    avaliacoes = _silver(spark, "avaliacoes").select("id_pedido", "nota_geral")
    pagamentos = _silver(spark, "pagamentos").select(
        "id_pedido", "forma_pagamento", "status_pagamento"
    )

    dim_tempo = spark.read.format("delta").load(gold_uri("dim_tempo"))
    dim_cliente = (
        spark.read.format("delta")
        .load(gold_uri("dim_cliente"))
        .filter("ativo = true")
        .select(F.col("id_cliente"), F.col("sk_cliente"))
    )
    dim_restaurante = (
        spark.read.format("delta")
        .load(gold_uri("dim_restaurante"))
        .filter("ativo = true")
        .select(F.col("id_restaurante"), F.col("sk_restaurante"))
    )
    dim_entregador = spark.read.format("delta").load(gold_uri("dim_entregador"))
    dim_pagamento = spark.read.format("delta").load(gold_uri("dim_pagamento"))

    fato = (
        pedidos.alias("p")
        .join(avaliacoes.alias("a"), "id_pedido", "left")
        .join(pagamentos.alias("pg"), "id_pedido", "left")
        .join(
            dim_tempo.alias("t"),
            F.date_format("p.data_hora_pedido", "yyyyMMdd").cast(LongType()) == F.col("t.sk_tempo"),
            "left",
        )
        .join(dim_cliente.alias("c"), F.col("p.id_cliente") == F.col("c.id_cliente"), "left")
        .join(
            dim_restaurante.alias("r"),
            F.col("p.id_restaurante") == F.col("r.id_restaurante"),
            "left",
        )
        .join(
            dim_entregador.alias("e"),
            F.col("p.id_entregador") == F.col("e.id_entregador"),
            "left",
        )
        .join(
            dim_pagamento.alias("dp"),
            (F.col("pg.forma_pagamento") == F.col("dp.forma_pagamento"))
            & (F.col("pg.status_pagamento") == F.col("dp.status_pagamento")),
            "left",
        )
        .select(
            F.col("p.id_pedido"),
            F.col("t.sk_tempo"),
            F.col("c.sk_cliente"),
            F.col("r.sk_restaurante"),
            F.col("e.sk_entregador"),
            F.col("dp.sk_pagamento"),
            F.col("p.valor_itens").cast("double"),
            F.col("p.taxa_entrega").cast("double"),
            F.col("p.desconto").cast("double"),
            F.col("p.valor_total").cast("double"),
            F.col("p.tempo_entrega_min").cast(IntegerType()),
            F.col("p.status_pedido"),
            F.col("a.nota_geral").cast("double"),
            F.col("p.data_hora_pedido"),
        )
    )

    target = gold_uri("fato_pedidos")
    if fato.count() > 0:
        max_row = fato.agg(
            F.max(F.col("data_hora_pedido").cast("date")).alias("max_data"),
            F.max("id_pedido").alias("max_id"),
        ).collect()[0]
        write_fato_checkpoint(spark, max_row["max_data"], int(max_row["max_id"] or 0))

    return _assign_sk_pedido(spark, fato.drop("data_hora_pedido"), target, incremental)


def run(incremental: bool = False) -> None:
    print("=== Gold: Silver → Dimensional (Kimball) ===")
    spark = create_spark("sparkeats-gold")

    dim_tempo = build_dim_tempo(spark)
    dim_tempo.write.format("delta").mode("overwrite").save(gold_uri("dim_tempo"))
    print(f"  [gold] dim_tempo: {dim_tempo.count()} linhas")

    apply_scd2(
        spark,
        build_dim_cliente_source(spark),
        gold_uri("dim_cliente"),
        "sk_cliente",
        "id_cliente",
        ["cidade", "estado", "bairro"],
    )
    apply_scd2(
        spark,
        build_dim_restaurante_source(spark),
        gold_uri("dim_restaurante"),
        "sk_restaurante",
        "id_restaurante",
        ["taxa_comissao", "categoria", "zona", "cidade"],
    )

    dim_entregador = build_dim_entregador(spark)
    dim_entregador.write.format("delta").mode("overwrite").save(gold_uri("dim_entregador"))
    print(f"  [gold] dim_entregador: {dim_entregador.count()} linhas")

    dim_pagamento = build_dim_pagamento(spark)
    dim_pagamento.write.format("delta").mode("overwrite").save(gold_uri("dim_pagamento"))
    print(f"  [gold] dim_pagamento: {dim_pagamento.count()} linhas")

    fato = build_fato_pedidos(spark, incremental=incremental)
    target = gold_uri("fato_pedidos")
    mode = "append" if incremental else "overwrite"
    cnt = fato.count()
    if cnt > 0:
        fato.write.format("delta").mode(mode).save(target)
        print(f"  [gold] fato_pedidos: {cnt} linhas ({mode})")
    else:
        print("  [gold] fato_pedidos: nenhum registro novo")

    spark.stop()
    sync_to_minio("gold")
    print("Gold concluída.")


if __name__ == "__main__":
    import sys

    run(incremental="--incremental" in sys.argv)
