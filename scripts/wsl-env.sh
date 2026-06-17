#!/usr/bin/env bash
# Carregar no WSL antes de trabalhar no projeto:
#   source scripts/wsl-env.sh

export PATH="/home/${USER}/.local/bin:/usr/bin:${PATH}"
export PROJECT_ROOT="/mnt/c/projeto-ed-final"
export MINIO_ENDPOINT="http://localhost:9090"
export MINIO_ROOT_USER="${MINIO_ROOT_USER:-minioadmin}"
export MINIO_ROOT_PASSWORD="${MINIO_ROOT_PASSWORD:-minioadmin}"
export DATABASE_URL="${DATABASE_URL:-postgresql://sparkeats:sparkeats_dev@localhost:5433/sparkeats}"
export POSTGRES_DB="${POSTGRES_DB:-sparkeats}"
export POSTGRES_USER="${POSTGRES_USER:-sparkeats}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-sparkeats_dev}"

alias docker='/usr/bin/docker'
alias dcompose='/usr/bin/docker compose -f docker/docker-compose.yml'

cd "$PROJECT_ROOT" 2>/dev/null || true

if ! pgrep -x dockerd >/dev/null 2>&1; then
  bash "$PROJECT_ROOT/scripts/start-docker.sh" 2>/dev/null || true
fi

echo "projeto-ed-final env OK — Postgres: localhost:5433 | MinIO API: $MINIO_ENDPOINT | Console: http://localhost:9091"
