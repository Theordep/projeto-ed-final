"""Factory do SparkSession com Delta Lake.

Carrega os JARs do delta-spark diretamente do pacote pip instalado via
spark.jars (caminhos absolutos) — sem Maven, sem Ivy, sem internet.
O pipeline escreve no filesystem local e sincroniza com MinIO via cliente Python.
"""

from __future__ import annotations

import os

from pyspark.sql import SparkSession


_DELTA_JARS = (
    "/opt/delta-jars/delta-spark_2.12-3.2.0.jar"
    ",/opt/delta-jars/delta-storage-3.2.0.jar"
)


def _delta_jars() -> str:
    """Retorna os JARs do Delta Lake (embutidos na imagem Docker em /opt/delta-jars).
    Fallback para o diretório 'jars' do pacote pip se não estiver no container.
    """
    if os.path.exists("/opt/delta-jars/delta-spark_2.12-3.2.0.jar"):
        return _DELTA_JARS
    # Fallback: tenta o diretório bundled do pacote pip (alguns builds incluem)
    import delta
    jars_dir = os.path.join(os.path.dirname(delta.__file__), "jars")
    if os.path.isdir(jars_dir):
        jars = [os.path.join(jars_dir, f) for f in os.listdir(jars_dir) if f.endswith(".jar")]
        if jars:
            return ",".join(jars)
    raise FileNotFoundError(
        "JARs do Delta Lake não encontrados. "
        "Rebuilde a imagem Docker: docker compose build airflow-scheduler airflow-webserver"
    )


def create_spark(app_name: str = "sparkeats") -> SparkSession:
    import pyspark

    spark_home = os.path.dirname(pyspark.__file__)
    os.environ.setdefault("SPARK_HOME", spark_home)
    warehouse = os.getenv("SPARK_WAREHOUSE", "/tmp/spark-warehouse")
    local_dirs = os.getenv("SPARK_LOCAL_DIRS", "/tmp/spark-local")

    return (
        SparkSession.builder.appName(app_name)
        .master(os.getenv("SPARK_MASTER", "local[*]"))
        # Vincula ao loopback para evitar problemas de rede em containers Docker
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.local.dir", local_dirs)
        .config("spark.sql.warehouse.dir", warehouse)
        .config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "2g"))
        .config("spark.sql.shuffle.partitions", "8")
        # JARs do Delta Lake — lidos do pacote pip (sem download Maven/Ivy)
        .config("spark.jars", _delta_jars())
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .getOrCreate()
    )
