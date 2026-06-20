# Apache Airflow

Ferramenta de orquestração responsável por agendar e executar todas as etapas do pipeline SparkEats.

## Acesso

| Interface | URL | Credenciais |
|-----------|-----|-------------|
| Airflow UI | http://localhost:8082 | `admin` / `admin` |

## Subir o serviço

```bash
docker compose -f docker/docker-compose.yml up -d airflow
```

## DAGs do pipeline

Cada camada da arquitetura Medallion possui uma DAG dedicada:

| DAG | Responsabilidade |
|-----|-----------------|
| `dag_landing` | Extrai tabelas do PostgreSQL e grava CSVs no MinIO (`landing-zone`) |
| `dag_bronze` | Converte CSVs da landing para Delta Lake no bucket `bronze` |
| `dag_silver` | Limpa e normaliza os dados do bronze para o bucket `silver` |
| `dag_gold` | Constrói o modelo dimensional no bucket `gold` |

## Ordem de execução

```
dag_landing → dag_bronze → dag_silver → dag_gold
```

!!! warning "Execute na ordem"
    Cada DAG depende da camada anterior. Executar `dag_silver` sem `dag_bronze` completo causará falha.

## Estrutura das DAGs

```
projeto-ed-final/
└── dags/
    ├── dag_landing.py
    ├── dag_bronze.py
    ├── dag_silver.py
    └── dag_gold.py
```

## Verificar logs

Na Airflow UI, acesse **DAGs → [nome da DAG] → Graph → [task] → Logs** para ver o output de cada execução.
