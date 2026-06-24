# Guia — MinIO (object storage / Data Lake local)

O **MinIO** é o armazenamento de objetos do projeto **SparkEats**. Ele simula um bucket S3 na nuvem, rodando no Docker — base da arquitetura **medalhão** do trabalho.

Issue: [#3](https://github.com/Theordep/projeto-ed-final/issues/3)

---

## O que é MinIO no nosso contexto?

No trabalho final, os dados passam por camadas:

```text
PostgreSQL (origem)
       │
       ▼
  landing-zone   ← CSV bruto (extração)
       │
       ▼
    bronze         ← Delta Lake (cópia tipada)
       │
       ▼
    silver         ← Delta Lake (limpeza / qualidade)
       │
       ▼
     gold          ← Delta Lake (modelo dimensional)
```

Cada camada é um **bucket** no MinIO. O pipeline lê e grava arquivos nesses buckets via sync a partir do `DATA_ROOT` local.

---

## Arquitetura no Docker

```text
Seu PC (WSL)
  ├── http://localhost:9090  →  API S3 (programas conectam aqui)
  └── http://localhost:9091  →  Console web (navegador)

Rede Docker
  └── projeto-ed-minio  (volume: minio_data)
        ├── landing-zone
        ├── bronze
        ├── silver
        └── gold
```

| Item | Valor |
|------|--------|
| Container | `projeto-ed-minio` |
| Console | http://localhost:9091 |
| API S3 | http://localhost:9090 |
| Usuário | `minioadmin` |
| Senha | `minioadmin` |

Variáveis no `wsl-env.sh`: `MINIO_ENDPOINT`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`.

---

## Por que portas 9090 e 9091?

O MinIO padrão usa **9000** (API) e **9001** (console). No nosso ambiente (WSL + Windows), essas portas podem apontar para **outro** MinIO vazio no Windows.

Por isso o `docker-compose.yml` publica:

| Host | Container |
|------|-----------|
| 9090 | 9000 |
| 9091 | 9001 |

Sempre acesse o console em **9091** neste projeto.

---

## Subir o MinIO

```bash
cd /mnt/c/projeto-ed-final
source scripts/wsl-env.sh
bash scripts/start-docker.sh

dcompose up -d minio
```

O serviço `minio-init` sobe automaticamente, espera o healthcheck e cria os buckets.

Subir MinIO + Postgres juntos:

```bash
dcompose up -d
```

---

## Validar buckets

```bash
bash scripts/verify-minio.sh
```

Saída esperada: container `healthy` e lista com `landing-zone`, `bronze`, `silver`, `gold`.

Recriar buckets manualmente (se necessário):

```bash
bash scripts/create_minio_buckets.sh
```

---

## Console web (navegador)

1. Abra: **http://localhost:9091**
2. Login: `minioadmin` / `minioadmin`
3. Menu **Object Browser**
4. Clique em um bucket (`landing-zone`, `bronze`, etc.)

Por enquanto os buckets podem estar vazios até a primeira execução do pipeline — dispare `sparkeats_pipeline_full` no Airflow ou rode `scripts/run_pipeline.py`.

---

## Buckets medalhão

| Bucket | Camada | Formato esperado (trabalho) |
|--------|--------|----------------------------|
| `landing-zone` | Landing | CSV bruto das tabelas origem |
| `bronze` | Bronze | Delta Lake |
| `silver` | Silver | Delta Lake |
| `gold` | Gold | Delta Lake (dimensional) |

O `minio-init` executa equivalente a:

```bash
mc mb local/landing-zone
mc mb local/bronze
mc mb local/silver
mc mb local/gold
```

(`mc` = MinIO Client — ferramenta de linha de comando S3.)

---

## Comandos úteis

### Status e logs

```bash
dcompose ps
dcompose logs minio
dcompose logs minio-init
docker ps --filter name=projeto-ed-minio
```

### Listar buckets via CLI (dentro da rede do container)

```bash
docker run --rm --network container:projeto-ed-minio --entrypoint /bin/sh minio/mc -c "
  mc alias set local http://127.0.0.1:9000 minioadmin minioadmin &&
  mc ls local
"
```

### Parar só o MinIO

```bash
dcompose stop minio
```

### Apagar dados do MinIO (cuidado)

```bash
dcompose down -v
# remove minio_data — todos os objetos dos buckets
```

---

## Como o pipeline usa o MinIO

Variáveis no ambiente:

```bash
echo $MINIO_ENDPOINT    # http://localhost:9090
```

O pipeline grava primeiro no disco local (`DATA_ROOT`) e espelha no MinIO via `sync_to_minio` (`src/sparkeats/storage.py`):

```text
{DATA_ROOT}/landing/postgres/pedidos/2025/06/24/143022/pedidos.csv
  →  s3://landing-zone/postgres/pedidos/2025/06/24/143022/pedidos.csv
```

| Ambiente | `DATA_ROOT` |
|----------|-------------|
| WSL (`wsl-env.sh`) | `/tmp/sparkeats-data` |
| Airflow (Docker) | `/data/sparkeats` |

---

## Problemas comuns

### Console abre mas buckets vazios / errados

Você pode estar no MinIO da porta **9001** (Windows) em vez do **9091** (projeto). Use sempre:

http://localhost:9091

### `projeto-ed-minio` não sobe

```bash
dcompose logs minio
```

Verifique se a porta 9090 está livre:

```bash
docker ps --format "{{.Names}} {{.Ports}}"
```

### Buckets não existem após `up`

```bash
bash scripts/create_minio_buckets.sh
dcompose logs minio-init
```

### Conflito com projeto EntregaSATC (aprendizado)

Só um stack deve usar 9090/9091:

```bash
# parar o outro projeto
cd /mnt/c/TRABALHO-FINAL-ENGENHARIA-DE-DADOS
docker compose -f docker/docker-compose.yml down

# subir o do grupo
cd /mnt/c/projeto-ed-final
dcompose up -d minio
```

---

## Checklist rápido

- [ ] `source scripts/wsl-env.sh`
- [ ] `dcompose up -d minio`
- [ ] `bash scripts/verify-minio.sh`
- [ ] Console em http://localhost:9091 com 4 buckets visíveis

---

## Ver também

- [Guia Docker](./docker.md) — compose, volumes, `dcompose`
- [PostgreSQL](postgres.md) — origem dos dados que irão para a landing
