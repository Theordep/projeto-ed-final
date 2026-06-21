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

!!! note "Airflow"
    O comando acima já inicia o serviço `airflow` junto com os demais.
    Se quiser iniciar apenas o Airflow depois, use:

    ```bash
    docker compose -f docker/docker-compose.yml up -d airflow
    ```

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

## 6. Executar as DAGs no Airflow

Acesse o Airflow em **http://localhost:8082** (usuário: `admin` / senha: `admin`).

### Opção 1: Pipeline Automático (Recomendado)

Ative a DAG `dag_pipeline_completo`:

1. Procure por `dag_pipeline_completo` na lista de DAGs
2. Clique no toggle para ativar
3. A DAG roda automaticamente todo dia às **00:00 (meia-noite)**
4. Executa em sequência: landing → bronze → silver → gold
5. Cada etapa começa automaticamente quando a anterior termina

### Opção 2: Executar DAGs Individuais Manualmente

Se quiser disparar camadas específicas sem esperar pela próxima meia-noite:

1. `dag_landing` — extrai dados do PostgreSQL
2. `dag_bronze` — converte para Delta Lake
3. `dag_silver` — limpa e normaliza
4. `dag_gold` — cria modelo dimensional

**Importante:** Sempre respeite a ordem (landing → bronze → silver → gold).

## 7. Verificar o ambiente

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