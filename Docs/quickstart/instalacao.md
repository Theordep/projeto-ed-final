# Instalação

Siga os passos abaixo para subir o ambiente completo do SparkEats.

## 1. Clonar o repositório

```bash
git clone https://github.com/Theordep/projeto-ed-final.git
cd projeto-ed-final
```

## 2. Subir os serviços com Docker

```bash
docker compose -f docker/docker-compose.yml up -d
```

Aguarde todos os serviços ficarem saudáveis:

```bash
docker ps
```

!!! info "Serviços disponíveis após o start"

    | Serviço | URL | Credenciais |
    |---------|-----|-------------|
    | MinIO Console | http://localhost:9091 | `minioadmin` / `minioadmin` |
    | Spark Master UI | http://localhost:8080 | — |
    | Spark Worker UI | http://localhost:8081 | — |
    | Airflow UI | http://localhost:8082 | `admin` / `admin` |
    | PostgreSQL | `localhost:5433` | `sparkeats` / `sparkeats_dev` |

## 3. Instalar dependências Python

```bash
uv sync
```

## 4. Criar o schema no PostgreSQL

```bash
uv run psql -h localhost -p 5433 -U sparkeats -d sparkeats \
  -f sql/ddl_origem_postgresql.sql
```

## 5. Popular o banco com dados sintéticos

```bash
uv run python scripts/seed_database.py
```

!!! tip "Quanto tempo leva?"
    O seed gera ~10.000 registros por tabela principal com distribuição dos últimos 3 anos. Espere entre 2 e 5 minutos dependendo da sua máquina.

## 6. Verificar o ambiente

=== "PostgreSQL"
    ```bash
    bash scripts/verify-postgres.sh
    ```

=== "MinIO"
    ```bash
    bash scripts/verify-minio.sh
    ```

## Próximos passos

Com o ambiente pronto, acesse a [visão geral da infraestrutura](../infra/index.md) ou vá direto para a [visão geral do pipeline](../pipeline/index.md).