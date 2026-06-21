# SparkEats

> Pipeline analítico de dados para uma plataforma de delivery — da origem ao dashboard.

---

## O que é o SparkEats?

O **SparkEats** é um projeto acadêmico que simula o pipeline de dados analítico de uma plataforma de delivery (no estilo iFood/Uber Eats). O objetivo é construir toda a jornada do dado: desde a geração sintética no banco de origem até a disponibilização em um modelo dimensional para consumo em dashboard.

!!! info "Disciplina"
    Projeto final da disciplina de **Engenharia de Dados** — curso de Engenharia de Software da **UNISATC**.

---

## Modelo de Operação

O pipeline segue a **Arquitetura Medallion** em quatro camadas, orquestradas pelo Apache Airflow e armazenadas no MinIO:

```
PostgreSQL (OLTP)
      │
      ▼
┌─────────────┐
│ Landing Zone│  ← Extração bruta (CSV)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Bronze    │  ← Dados brutos em Delta Lake
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Silver    │  ← Dados limpos e normalizados
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Gold     │  ← Modelo dimensional (fatos e dimensões)
└──────┬──────┘
       │
       ▼
   Dashboard
```

=== "Landing Zone"
    Dados extraídos diretamente do PostgreSQL no formato **CSV bruto**, sem nenhuma transformação. Serve como ponto de recuperação em caso de falha nas camadas seguintes.

=== "Bronze"
    Dados convertidos para **Delta Lake** mantendo a estrutura original da origem. Nenhuma regra de negócio aplicada — apenas ingestão e persistência confiável.

=== "Silver"
    Dados **limpos, tipados e normalizados**. Deduplicação, tratamento de nulos, padronização de datas e enriquecimento leve. Base para as transformações analíticas.

=== "Gold"
    Dados no **modelo dimensional** (fatos e dimensões) prontos para consumo pelo dashboard. Contém os KPIs e métricas do negócio.

---

## Stack Tecnológica

| Camada | Ferramenta | Função |
|--------|-----------|--------|
| Origem | PostgreSQL 16 | Banco OLTP com dados de delivery |
| Geração | Faker (Python) | Massa de dados sintética realista |
| Orquestração | Apache Airflow | Agendamento e execução do pipeline |
| Processamento | Apache Spark 3.4.1 | Transformação entre camadas |
| Armazenamento | MinIO | Object storage local (Data Lake) |
| Formato | Delta Lake | Armazenamento transacional nas camadas Bronze→Gold |
| Ambiente | Docker + Docker Compose | Containerização de todos os serviços |
| Linguagem | Python 3.12 + uv | Scripts, DAGs e dependências |

---

## Fluxo do Dado

!!! example "Jornada completa"

    1. **Geração** — `seed_database.py` popula o PostgreSQL com dados sintéticos de restaurantes, clientes, entregadores, pedidos, pagamentos e avaliações (últimos 3 anos).
    2. **Extração** — DAG do Airflow lê as tabelas do PostgreSQL e grava CSVs no bucket `landing-zone` do MinIO.
    3. **Bronze** — DAG converte os CSVs para Delta Lake no bucket `bronze`, preservando a estrutura original.
    4. **Silver** — DAG aplica limpeza, tipagem e normalização, gravando no bucket `silver`.
    5. **Gold** — DAG constrói o modelo dimensional no bucket `gold` com fatos e dimensões.
    6. **Dashboard** — Ferramenta consome a camada Gold e exibe os KPIs.

---

## Modelo de Dados (Origem)

O banco PostgreSQL possui **10 tabelas** organizadas em duas categorias:

=== "Dimensões de apoio"
    - `categorias_restaurante`
    - `zonas_entrega`
    - `cupons`

=== "Entidades principais"
    - `restaurantes`
    - `cardapio`
    - `clientes`
    - `enderecos_cliente`
    - `entregadores`

=== "Transações"
    - `pedidos`
    - `itens_pedido`
    - `pagamentos`
    - `avaliacoes`

---

## Serviços e Portas

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| MinIO Console | http://localhost:9091 | `minioadmin` / `minioadmin` |
| MinIO API | http://localhost:9090 | — |
| Spark Master UI | http://localhost:8080 | — |
| Spark Worker UI | http://localhost:8081 | — |
| Airflow UI | http://localhost:8082 | `admin` / `admin` |
| PostgreSQL | `localhost:5433` | `sparkeats` / `sparkeats_dev` |

!!! warning "Portas deslocadas"
    As portas padrão foram alteradas para evitar conflito com outros serviços no Windows/WSL. Consulte o `docker/docker-compose.yml` para detalhes.

---

## Equipe

| Nome | GitHub |
|------|--------|
| Pedro Ernesto | [@theordep](https://github.com/Theordep) |
| Vanessa Ugioni | [@vanessaugioni](https://github.com/vanessaugioni) |
| Gabriel Muller | [@GabrielNM12](https://github.com/GabrielNM12) |
| Bettina da Silva | [@Berbett](https://github.com/Berbett) |
| Carlos Eduardo | [@carloseduardob](https://github.com/carloseduardob) |