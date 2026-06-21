"""Factory do SparkSession com Delta Lake."""

from __future__ import annotations

import os

from pyspark.sql import SparkSession

from sparkeats.config import MINIO_ACCESS_KEY, MINIO_ENDPOINT, MINIO_SECRET_KEY, SPARK_PACKAGES


def create_spark(app_name: str = "sparkeats") -> SparkSession:
    import pyspark

    spark_home = os.path.join(os.path.dirname(pyspark.__file__))
    os.environ.setdefault("SPARK_HOME", spark_home)
    endpoint = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    warehouse = os.getenv("SPARK_WAREHOUSE", "/tmp/spark-warehouse")
    local_dirs = os.getenv("SPARK_LOCAL_DIRS", "/tmp/spark-local")

    builder = (
        SparkSession.builder.appName(app_name)
        .master(os.getenv("SPARK_MASTER", "local[*]"))
        .config("spark.local.dir", local_dirs)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.warehouse.dir", warehouse)
        .config("spark.hadoop.fs.s3a.endpoint", endpoint)
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY)
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.jars.packages", SPARK_PACKAGES)
        .config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "2g"))
        .config("spark.sql.shuffle.partitions", "8")
    )
    return builder.getOrCreate()
