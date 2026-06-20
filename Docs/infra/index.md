# Infraestrutura

O SparkEats roda inteiramente em containers Docker. Todos os serviços são declarados em `docker/docker-compose.yml`.

## Serviços

| Serviço | Imagem | Função |
|---------|--------|--------|
| `postgres` | `postgres:16-alpine` | Banco de dados OLTP (origem) |
| `minio` | `minio/minio` | Object storage (Data Lake) |
| `minio-init` | `minio/mc` | Cria os buckets automaticamente |
| `spark-master` | `bitnami/spark:3.4.1` | Coordenador do cluster Spark |
| `spark-worker` | `bitnami/spark:3.4.1` | Executor do cluster Spark |
| `airflow` | `apache/airflow` | Orquestrador do pipeline |

## Arquitetura de rede

Todos os serviços compartilham a mesma rede Docker interna e se comunicam pelo nome do container. As portas mapeadas para o host são deslocadas para evitar conflitos com instalações locais.

!!! note "Portas deslocadas"
    | Serviço | Porta padrão | Porta no host |
    |---------|-------------|--------------|
    | PostgreSQL | 5432 | **5433** |
    | MinIO API | 9000 | **9090** |
    | MinIO Console | 9001 | **9091** |

## Subir e parar o ambiente

```bash
# Subir
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