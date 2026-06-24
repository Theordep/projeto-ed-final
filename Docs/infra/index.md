# Infraestrutura

O SparkEats roda inteiramente em containers Docker. Todos os serviços são declarados em `docker/docker-compose.yml`.

## Serviços

| Serviço | Imagem | Função |
|---------|--------|--------|
| `postgres` | `postgres:16-alpine` | Banco OLTP (origem) + metadados Airflow |
| `minio` | `minio/minio` | Object storage (Data Lake) |
| `minio-init` | `minio/mc` | Cria os buckets medalhão na subida |
| `spark-master` | `apache/spark:3.5.1` | Coordenador do cluster Spark standalone |
| `spark-worker` | `apache/spark:3.5.1` | Executor do cluster Spark |
| `airflow-init` | `apache/airflow:2.9.3` (custom) | Inicialização do banco e usuário admin |
| `airflow-webserver` | `apache/airflow:2.9.3` (custom) | Interface web (porta 8082) |
| `airflow-scheduler` | `apache/airflow:2.9.3` (custom) | Agendador das DAGs |
| `metabase` | `metabase/metabase:v0.52.7` | Dashboard analítico (porta 3000) |

## Arquitetura de rede

Todos os serviços compartilham a mesma rede Docker interna e se comunicam pelo nome do container. As portas mapeadas para o host são deslocadas para evitar conflitos com instalações locais.

!!! note "Portas deslocadas"
    | Serviço | Porta padrão | Porta no host |
    |---------|-------------|--------------|
    | PostgreSQL | 5432 | **5433** |
    | MinIO API | 9000 | **9090** |
    | MinIO Console | 9001 | **9091** |
    | Airflow UI | 8080 | **8082** |
    | Spark Master UI | 8080 | **8080** |
    | Metabase | 3000 | **3000** |

## Subir e parar o ambiente

```bash
# Subir tudo
docker compose -f docker/docker-compose.yml up -d

# Parar
docker compose -f docker/docker-compose.yml down

# Parar e remover volumes
docker compose -f docker/docker-compose.yml down -v
```

## Documentação por serviço

- [Docker](docker.md) — configuração e troubleshooting
- [PostgreSQL](postgres.md) — banco OLTP e modelo de dados
- [MinIO](minio.md) — buckets e arquitetura Medallion
- [Apache Spark](spark.md) — cluster e configuração
- [Apache Airflow](airflow.md) — orquestração do pipeline
