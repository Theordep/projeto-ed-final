# MinIO — object storage local

Issue: [#3 Configurar ambiente Docker com MinIO](https://github.com/Theordep/projeto-ed-final/issues/3)

## Arquitetura

```text
WSL host
  ├── localhost:9090  →  MinIO API (S3-compatible)
  └── localhost:9091  →  MinIO Console (UI)

Docker network
  └── projeto-ed-minio (volume minio_data)
        └── buckets: landing-zone | bronze | silver | gold
```

## Por que portas 9090/9091?

No Windows, `localhost:9000` e `9001` podem apontar para **outro** MinIO vazio.
O compose publica o container nas portas **9090/9091** no host para garantir que o console mostre os buckets corretos.

## Fluxo de inicialização

1. `minio` sobe e passa no healthcheck
2. `minio-init` executa `mc mb` para cada bucket medalhão
3. Pipeline (issues futuras) grava objetos via API ou sync

## Comandos úteis

```bash
dcompose ps
dcompose logs minio
dcompose logs minio-init
bash scripts/verify-minio.sh
```

## Próximas issues (dependências)

- **#7** — Postgres origem (dados para landing)
- **#6** — Spark (transformações bronze/silver)
- **#16** — Pipeline Landing → Bronze → Silver
