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

O SparkEats usa **duas DAGs** que executam todo o pipeline de ponta a ponta em cada execução:

| DAG | Frequência | Descrição |
|-----|-----------|-----------|
| `sparkeats_pipeline_full` | Semanal | Carga completa — reprocessa todos os dados do zero |
| `sparkeats_pipeline_incremental` | Diária | Carga incremental — processa apenas registros novos ou alterados |

## Cadeia interna de cada DAG

Ambas as DAGs percorrem a mesma sequência de tarefas:

```
landing → bronze → silver → gold → export_to_pg
```

| Tarefa | Responsabilidade |
|--------|-----------------|
| `landing` | Extrai tabelas do PostgreSQL e grava CSVs no MinIO (`landing-zone`) |
| `bronze` | Converte CSVs para Delta Lake no bucket `bronze` |
| `silver` | Limpa, tipifica e normaliza os dados para o bucket `silver` |
| `gold` | Constrói o modelo dimensional no bucket `gold` |
| `export_to_pg` | Exporta as tabelas Gold para o schema `analytics` no PostgreSQL (consumido pelo Metabase) |

!!! warning "Dependência de ordem"
    Cada tarefa depende da anterior. A DAG garante a ordem de execução automaticamente.

## Estrutura das DAGs

```
projeto-ed-final/
└── dags/
    ├── sparkeats_pipeline_full.py
    └── sparkeats_pipeline_incremental.py
```

## Verificar logs

Na Airflow UI, acesse **DAGs → [nome da DAG] → Graph → [task] → Logs** para ver o output de cada execução.
