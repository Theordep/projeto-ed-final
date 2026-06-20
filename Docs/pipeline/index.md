# Pipeline — Visão Geral

O pipeline do SparkEats percorre quatro camadas no MinIO, orquestradas pelo Apache Airflow e processadas pelo Apache Spark.

## Fluxo completo

```
PostgreSQL (OLTP)
       │
       ▼ dag_landing
  landing-zone  ←  CSV bruto
       │
       ▼ dag_bronze
    bronze      ←  Delta Lake (estrutura original)
       │
       ▼ dag_silver
    silver      ←  Delta Lake (limpo e normalizado)
       │
       ▼ dag_gold
      gold       ←  Delta Lake (modelo dimensional)
       │
       ▼
   Dashboard
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
- [Gold](gold.md) — modelo dimensional para o dashboard

!!! tip "Carga incremental"
    A partir da camada Bronze, o pipeline usa **carga incremental** — apenas registros novos ou alterados são processados a cada execução.