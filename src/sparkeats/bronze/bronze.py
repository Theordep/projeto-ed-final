"""Landing CSV → Bronze Delta Lake."""

from __future__ import annotations

from datetime import datetime, timezone

from pyspark.sql import functions as F

from sparkeats.config import OLTP_TABLES
from sparkeats.spark_session import create_spark
from sparkeats.storage import landing_csv_glob, layer_uri, sync_to_minio


def run() -> None:
    print("=== Bronze: Landing CSV → Delta ===")
    spark = create_spark("sparkeats-bronze")
    ingested_at = datetime.now(timezone.utc)

    for table in OLTP_TABLES:
        landing_glob = landing_csv_glob(table)
        try:
            df = (
                spark.read.option("header", True)
                .option("inferSchema", True)
                .csv(landing_glob)
            )
        except Exception as exc:
            print(f"  [bronze] {table}: sem dados ({exc})")
            continue

        if df.rdd.isEmpty():
            print(f"  [bronze] {table}: vazio")
            continue

        bronze_df = (
            df.withColumn("_ingested_at", F.lit(ingested_at))
            .withColumn("_source_table", F.lit(table))
            .withColumn("_source_layer", F.lit("landing"))
        )
        target = layer_uri("bronze", table)
        bronze_df.write.format("delta").mode("overwrite").save(target)
        print(f"  [bronze] {table}: {bronze_df.count()} linhas → {target}")

    spark.stop()
    sync_to_minio("bronze")
    print("Bronze concluída.")


if __name__ == "__main__":
    run()
