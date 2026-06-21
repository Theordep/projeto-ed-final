#!/usr/bin/env bash
# Carregar no WSL antes de trabalhar no projeto:
#   source scripts/wsl-env.sh

export PATH="/home/${USER}/.local/bin:/usr/bin:${PATH}"
export PROJECT_ROOT="/mnt/c/projeto-ed-final"
export MINIO_ENDPOINT="http://localhost:9090"
export MINIO_ROOT_USER="${MINIO_ROOT_USER:-minioadmin}"
export MINIO_ROOT_PASSWORD="${MINIO_ROOT_PASSWORD:-minioadmin}"
export MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-$MINIO_ROOT_USER}"
export MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-$MINIO_ROOT_PASSWORD}"
export DATABASE_URL="${DATABASE_URL:-postgresql://sparkeats:sparkeats_dev@localhost:5433/sparkeats}"
export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export POSTGRES_PORT="${POSTGRES_PORT:-5433}"
export POSTGRES_DB="${POSTGRES_DB:-sparkeats}"
export POSTGRES_USER="${POSTGRES_USER:-sparkeats}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-sparkeats_dev}"
# Camadas Delta fora de /mnt/c (evita chmod no Spark)
export DATA_ROOT="${DATA_ROOT:-/tmp/sparkeats-data}"
export SPARK_LOCAL_DIRS="${SPARK_LOCAL_DIRS:-/tmp/spark-local}"
export SPARK_WAREHOUSE="${SPARK_WAREHOUSE:-/tmp/spark-warehouse}"
export SPARK_DRIVER_MEMORY="${SPARK_DRIVER_MEMORY:-2g}"

alias docker='/usr/bin/docker'
# Wrapper em scripts/bin/dcompose funciona mesmo sem alias (scripts, CI)
export PATH="$PROJECT_ROOT/scripts/bin:${PATH}"
alias dcompose='/usr/bin/docker compose -f docker/docker-compose.yml'

cd "$PROJECT_ROOT" 2>/dev/null || true

if ! pgrep -x dockerd >/dev/null 2>&1; then
  bash "$PROJECT_ROOT/scripts/start-docker.sh" 2>/dev/null || true
fi

echo "projeto-ed-final env OK — Postgres: localhost:5433 | MinIO: $MINIO_ENDPOINT | DATA_ROOT: $DATA_ROOT"
