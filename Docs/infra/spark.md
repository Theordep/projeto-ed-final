# Apache Spark no Docker

## Status

- Cluster Apache Spark configurado em `docker/docker-compose.yml`
- Serviços:
  - `spark-master` (Spark Master)
  - `spark-worker` (Spark Worker)

## Como iniciar

```bash
cd c:\Users\gabri\Documents\GitHub\projeto-ed-final
docker compose -f docker/docker-compose.yml up -d
```

## Verificar serviços

```bash
docker compose -f docker/docker-compose.yml ps
```

## Endpoints úteis

- Spark Master UI: `http://localhost:8080`
- Spark Worker UI: `http://localhost:8081`
- Spark Master URL: `spark://spark-master:7077`

## Observações

- O compose atual já inclui MinIO e o cluster Spark standalone.
- Ainda não há notebooks ou jobs DataBricks definidos no repositório.
