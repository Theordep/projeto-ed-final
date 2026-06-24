# Apache Spark no Docker

## Versão

Apache Spark **3.5.1** — imagem oficial `apache/spark:3.5.1`.

## Cluster standalone

O `docker-compose.yml` inclui um cluster Spark standalone para monitoramento e uso futuro:

| Serviço | Função |
|---------|--------|
| `spark-master` | Coordenador (UI em http://localhost:8080) |
| `spark-worker` | Executor (UI em http://localhost:8081) |

```bash
docker compose -f docker/docker-compose.yml up -d spark-master spark-worker
```

- Spark Master URL: `spark://spark-master:7077`

## Como o pipeline executa Spark

As DAGs do Airflow **não** submetem jobs via `spark-submit` ao cluster. O processamento roda com **PySpark em modo `local[*]`** dentro do container Airflow:

- `SPARK_MASTER=local[*]` (variável no compose)
- JARs do Delta Lake em `/opt/delta-jars` (imagem customizada)
- Dados gravados em `DATA_ROOT` (`/data/sparkeats` no container) e sincronizados com o MinIO

Código: `src/sparkeats/spark_session.py`.

## Verificar serviços

```bash
docker compose -f docker/docker-compose.yml ps
```

## Referências

- [Apache Spark 3.5.1 Documentation](https://spark.apache.org/docs/3.5.1/)
- [Delta Lake + Spark](https://delta.io/learn/getting-started/)
