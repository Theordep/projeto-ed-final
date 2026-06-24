# Apache Spark no Docker

## Versão

Apache Spark **3.5.1** — imagem `bitnami/spark:3.5.1`.

## Status

- Cluster Apache Spark configurado em `docker/docker-compose.yml`
- Serviços:
  - `spark-master` (Spark Master)
  - `spark-worker` (Spark Worker)

## Como iniciar

```bash
docker compose -f docker/docker-compose.yml up -d spark-master spark-worker
```

## Verificar serviços

```bash
docker compose -f docker/docker-compose.yml ps
```

## Endpoints úteis

- Spark Master UI: `http://localhost:8080`
- Spark Worker UI: `http://localhost:8081`
- Spark Master URL: `spark://spark-master:7077`

## Observações

- O compose atual inclui MinIO e o cluster Spark standalone.
- Os jobs Spark são submetidos pelas DAGs do Airflow via `spark-submit`.
- Dependências Delta Lake e conectores S3/MinIO são carregados automaticamente via JARs configurados no `docker-compose.yml`.

## Referências

- [Apache Spark 3.5.1 Documentation](https://spark.apache.org/docs/3.5.1/)
- [Delta Lake + Spark](https://delta.io/learn/getting-started/)
