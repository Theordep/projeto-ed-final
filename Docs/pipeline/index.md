# Pipeline — Visão Geral

O pipeline do SparkEats percorre quatro camadas no MinIO, orquestradas pelo Apache Airflow e processadas pelo PySpark.

## Fluxo completo

```
PostgreSQL (OLTP)
       │
       ▼ landing
  landing-zone  ←  CSV bruto
       │
       ▼ bronze
    bronze      ←  Delta Lake (estrutura original)
       │
       ▼ silver
    silver      ←  Delta Lake (limpo e normalizado)
       │
       ▼ gold
      gold       ←  Delta Lake (modelo dimensional)
       │
       ▼ export_to_pg
  PostgreSQL (schema analytics)
       │
       ▼
   Metabase
```

## Orquestração (Airflow)

O pipeline **não** usa DAGs separadas por camada. Duas DAGs executam toda a cadeia de ponta a ponta:

| DAG | Frequência | Descrição |
|-----|-----------|-----------|
| `sparkeats_pipeline_full` | Semanal (domingos 02:00) | Carga completa — reprocessa todos os dados |
| `sparkeats_pipeline_incremental` | Diária (03:00) | Carga incremental nas tabelas fato |

Cadeia interna de cada DAG:

```
landing → bronze → silver → gold → export_to_pg
```

## Camadas

| Camada | Bucket | Formato | Transformação |
|--------|--------|---------|---------------|
| Landing Zone | `landing-zone` | CSV | Nenhuma — cópia bruta |
| Bronze | `bronze` | Delta Lake | Conversão de formato |
| Silver | `silver` | Delta Lake | Limpeza e normalização |
| Gold | `gold` | Delta Lake | Modelo dimensional |

## Responsabilidades por etapa

- [Geração de dados](faker.md) — como os dados sintéticos são criados no PostgreSQL
- [Landing Zone](landing.md) — extração do PostgreSQL para o MinIO
- [Bronze](bronze.md) — primeira persistência em Delta Lake
- [Silver](silver.md) — tratamento e qualidade dos dados
- [Gold](gold.md) — modelo dimensional e export para o Metabase

!!! tip "Carga incremental"
    A carga incremental ocorre em dois pontos:

    - **Landing** — nas tabelas fato (`pedidos`, `itens_pedido`, `pagamentos`, `avaliacoes`), filtrando por PK > último checkpoint
    - **Gold** — em `fato_pedidos`, via `checkpoint_fato_pedidos` (data + `id_pedido`)

    Bronze e Silver sempre fazem **overwrite** completo das tabelas processadas.
