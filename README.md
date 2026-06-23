# SparkEats — Pipeline Analítico de Delivery

Pipeline de dados analítico para uma plataforma de delivery, desenvolvido na disciplina de Engenharia de Dados do curso de Engenharia de Software da UNISATC.

[![Python](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/gerenciador-uv-DE5FE9)](https://docs.astral.sh/uv/)
[![Apache Spark](https://img.shields.io/badge/spark-3.5.1-E25A1C?logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MinIO](https://img.shields.io/badge/minio-object_storage-C72E49?logo=minio&logoColor=white)](https://min.io/)
[![MkDocs](https://img.shields.io/badge/docs-mkdocs-526CFE?logo=materialformkdocs&logoColor=white)](https://theordep.github.io/projeto-ed-final)
[![Apache Airflow](https://img.shields.io/badge/orchestration-apache%20airflow-017CEE?logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![Metabase](https://img.shields.io/badge/dashboard-metabase-509EE3?logo=metabase&logoColor=white)](https://www.metabase.com/)

## Desenho de Arquitetura

```
PostgreSQL (OLTP)
      │
      ▼  Apache Airflow (orquestração)
  Landing Zone (CSV)
      │
      ▼  PySpark
  Bronze (Delta Lake)
      │
      ▼  PySpark
  Silver (Delta Lake — qualidade + LGPD)
      │
      ▼  PySpark + SCD2
  Gold (Delta Lake — modelo dimensional Kimball)
      │
      ▼  export_to_pg
  PostgreSQL · schema analytics
      │
      ▼
  Metabase (Dashboard)
```

> Object Storage: **MinIO** (S3-compatível) — buckets `landing-zone`, `bronze`, `silver`, `gold`

## Pré-requisitos e ferramentas utilizadas

* Linguagem: Python 3.12
* Gerenciador de dependências: uv
* Banco de dados origem: PostgreSQL 16
* Motor de transformação: Apache Spark 3.5.1 (PySpark)
* Object Storage: MinIO (arquitetura Medallion)
* Geração de dados: Faker
* Container: Docker
* Orquestração local: Docker Compose
* Documentação: MkDocs + mkdocs-material
* Orquestração de pipelines: Apache Airflow
* Dashboard BI: Metabase

### Verificar instalações

```bash
java -version
python --version
uv --version
docker --version
docker compose version
```

> ⚠️ O Apache Spark **não é compatível com Java 21+**. Use obrigatoriamente o **JDK 17**.

### Configurar JAVA_HOME (Linux/WSL)

Adicione ao `~/.bashrc` ou `~/.zshrc` e reinicie o terminal:

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
```

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/Theordep/projeto-ed-final.git
cd projeto-ed-final
```

### 2. Subir o ambiente com Docker

```bash
docker compose -f docker/docker-compose.yml up -d
```

> Console MinIO: **http://localhost:9091** — usuário: `minioadmin` / senha: `minioadmin`
>
> Spark Master UI: **http://localhost:8080**
>
> Airflow UI: **http://localhost:8082** — usuário: `admin` / senha: `admin`
>
> Metabase: **http://localhost:3000**
>
> PostgreSQL: `localhost:5433` | MinIO API: `localhost:9090`

### 3. Instalar dependências

```bash
uv sync
```

### 4. Criar o schema no PostgreSQL

```bash
uv run psql -h localhost -p 5433 -U sparkeats -d sparkeats -f sql/ddl_origem_postgresql.sql
```

### 5. Popular o banco com dados sintéticos

```bash
uv run python scripts/seed_database.py
```

## Documentação (MkDocs)

Toda a documentação está em `Docs/`:

```bash
uv run mkdocs build
uv run mkdocs serve
```

Acesse o site em `http://127.0.0.1:8000`.

Para publicar o site estático:

```bash
uv run mkdocs gh-deploy
```

🔗 Documentação publicada: https://theordep.github.io/projeto-ed-final

## Colaboração

1. Abra uma issue para discutir sua feature ou bug.
2. Crie um branch:

```bash
git checkout -b feature/nome-da-sua-feature
```

3. Faça suas alterações e commit seguindo o [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
4. Envie um pull request para `main`.
5. Aguarde revisão e merge.

## Versão

`0.1.0` — versão inicial com ingestão, transformação e carga nas camadas Bronze, Silver e Gold.

## Participantes

* Pedro Ernesto — [@theordep](https://github.com/Theordep)
* Vanessa Ugioni — [@vanessaugioni](https://github.com/vanessaugioni)
* Gabriel Muller — [@GabrielNM12](https://github.com/GabrielNM12)
* Bettina da Silva — [@Berbett](https://github.com/Berbett)
* Carlos Eduardo — [@carloseduardob](https://github.com/carloseduardob)

## Licença

Este projeto está sob a licença MIT — veja o arquivo [LICENSE](LICENSE) para detalhes.

## Referências

* [jlsilva01/projeto-ed-satc](https://github.com/jlsilva01/projeto-ed-satc)
* [Documentação Apache Spark](https://spark.apache.org/docs/latest/)
* [Documentação MinIO](https://min.io/docs/minio/linux/index.html)
* [Documentação PostgreSQL](https://www.postgresql.org/docs/)
* [Documentação uv](https://docs.astral.sh/uv/)
* [Delta Lake](https://docs.delta.io/)
* [Apache Airflow](https://airflow.apache.org/docs/)