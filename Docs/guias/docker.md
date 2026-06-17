# Guia — Docker no WSL (projeto-ed-final)

O **Docker** roda os serviços de infraestrutura do **SparkEats** em containers isolados: PostgreSQL, MinIO e (no futuro) Airflow, Metabase, etc.

Neste projeto usamos **Docker Engine no WSL2** — **sem** Docker Desktop.

Documentação técnica resumida: [Docs/infra/](../infra/)

---

## O que o Docker faz no nosso projeto?

```text
docker/docker-compose.yml
        │
        ├── postgres  →  banco origem SparkEats (porta 5433)
        └── minio     →  Data Lake local / API S3 (portas 9090/9091)
              └── minio-init  →  cria buckets medalhão na subida
```

| Container | Função no pipeline |
|-----------|-------------------|
| `projeto-ed-postgres` | Dados OLTP (origem) — issue #7 |
| `projeto-ed-minio` | Object storage — camadas landing/bronze/silver/gold — issue #3 |
| `projeto-ed-minio-init` | Job único: cria buckets e encerra |

---

## Pré-requisitos

- **WSL2** com Ubuntu
- **Docker Engine** instalado no WSL (não no Windows)
- Portas livres no host: **5433**, **9090**, **9091**

---

## Configuração do ambiente (sempre primeiro)

O script `scripts/wsl-env.sh` prepara variáveis, alias e tenta subir o Docker:

```bash
cd /mnt/c/projeto-ed-final
source scripts/wsl-env.sh
```

O que ele define:

| Item | Valor |
|------|--------|
| `PROJECT_ROOT` | `/mnt/c/projeto-ed-final` |
| `DATABASE_URL` | Postgres SparkEats na 5433 |
| `MINIO_ENDPOINT` | `http://localhost:9090` |
| Alias `docker` | `/usr/bin/docker` (evita conflito com Git Bash) |
| Alias `dcompose` | `docker compose -f docker/docker-compose.yml` |

---

## Iniciar o Docker Engine

Se o WSL acabou de abrir, o daemon pode estar parado:

```bash
bash scripts/start-docker.sh
```

Saída esperada: lista de containers ou mensagem `Docker ja esta rodando.`

Iniciar manualmente (alternativa):

```bash
sudo service docker start
docker ps
```

---

## Comandos essenciais (`dcompose`)

Sempre com o ambiente carregado (`source scripts/wsl-env.sh`).

### Subir tudo

```bash
dcompose up -d
```

O `-d` roda em **background** (detached).

### Subir só um serviço

```bash
dcompose up -d postgres    # só banco
dcompose up -d minio       # só MinIO (+ minio-init automático)
```

### Ver status

```bash
dcompose ps
docker ps
```

### Ver logs

```bash
dcompose logs postgres
dcompose logs minio
dcompose logs minio-init
dcompose logs -f minio       # seguir em tempo real
```

### Parar

```bash
dcompose stop                # para containers, mantém volumes
dcompose down                # remove containers, mantém volumes
dcompose down -v             # remove containers E volumes (apaga dados!)
```

Cuidado com `down -v`: **apaga** o banco populado e os arquivos do MinIO.

### Reiniciar um serviço

```bash
dcompose restart postgres
dcompose restart minio
```

### Executar comando dentro do container

```bash
dcompose exec postgres psql -U sparkeats -d sparkeats -c "SELECT 1;"
```

---

## Fluxo completo — infra SparkEats

```bash
cd /mnt/c/projeto-ed-final
source scripts/wsl-env.sh
bash scripts/start-docker.sh

dcompose up -d

bash scripts/verify-minio.sh
bash scripts/verify-postgres.sh
```

Se o Postgres ainda não tiver dados:

```bash
uv sync
uv run python scripts/seed_database.py
```

---

## Arquivo `docker-compose.yml`

Local: `docker/docker-compose.yml`

Conceitos importantes:

| Conceito | No nosso projeto |
|----------|------------------|
| **service** | `postgres`, `minio`, `minio-init` |
| **image** | Imagem Docker Hub (`postgres:16-alpine`, `minio/minio:...`) |
| **ports** | `HOST:CONTAINER` — ex.: `5433:5432` |
| **volumes** | `postgres_data`, `minio_data` — persistem dados entre `down`/`up` |
| **healthcheck** | Compose espera serviço saudável antes do `minio-init` |
| **depends_on** | `minio-init` só roda após MinIO healthy |

### Por que portas diferentes do padrão?

| Serviço | Porta host | Motivo |
|---------|------------|--------|
| Postgres | **5433** | `5432` no Windows pode ser outro Postgres |
| MinIO API | **9090** | `9000` pode ser outro MinIO no Windows |
| MinIO Console | **9091** | `9001` idem |

---

## Volumes Docker

```bash
docker volume ls | grep docker_
```

| Volume | Conteúdo |
|--------|----------|
| `docker_postgres_data` | Dados do banco `sparkeats` |
| `docker_minio_data` | Objetos dos buckets |

Listar detalhes:

```bash
docker volume inspect docker_postgres_data
```

---

## Problemas comuns

### `Cannot connect to the Docker daemon`

```bash
sudo service docker start
# ou
bash scripts/start-docker.sh
```

### `docker: command not found` ou comando estranho no Git Bash

Use o WSL e carregue o ambiente:

```bash
source scripts/wsl-env.sh
docker ps    # usa /usr/bin/docker
```

### Porta já em uso

```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

Outro projeto (ex.: EntregaSATC) pode estar na 5433 ou 9090. Pare o outro stack:

```bash
cd /mnt/c/TRABALHO-FINAL-ENGENHARIA-DE-DADOS
docker compose -f docker/docker-compose.yml down
```

### Container `unhealthy`

```bash
dcompose logs postgres
dcompose logs minio
```

Postgres: espere alguns segundos após `up`. MinIO: precisa de `curl` na imagem para o healthcheck.

### Credenciais erradas no Postgres após trocar compose

O volume antigo guarda usuário/senha da primeira subida. Para recriar limpo:

```bash
dcompose down -v postgres
dcompose up -d postgres
uv run python scripts/seed_database.py
```

---

## Relação com outras issues

| Issue | Uso do Docker |
|-------|----------------|
| #3 MinIO | `minio` + `minio-init` |
| #7 Postgres | `postgres` |
| #6 Spark | processamento (futuro) |
| #16 Pipeline | extração → buckets |
| Airflow / Metabase | serviços futuros no compose |

---

## Referência rápida

| Ação | Comando |
|------|---------|
| Ambiente | `source scripts/wsl-env.sh` |
| Subir tudo | `dcompose up -d` |
| Status | `dcompose ps` |
| Logs | `dcompose logs <serviço>` |
| Parar | `dcompose down` |
| Apagar dados | `dcompose down -v` |
| Shell no Postgres | `dcompose exec postgres psql -U sparkeats -d sparkeats` |

---

## Próximo passo

- [Guia MinIO](./minio.md) — buckets e console web
- [Guia PostgreSQL](./postgres.md) — banco, seed e DBeaver
