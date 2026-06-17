#!/usr/bin/env bash
# Verifica se MinIO e buckets estao acessiveis.
set -eu

DOCKER="${DOCKER:-/usr/bin/docker}"

echo "=== Containers ==="
$DOCKER ps --filter name=projeto-ed-minio --format "{{.Names}} {{.Status}}"

echo ""
echo "=== Buckets ==="
$DOCKER run --rm --network container:projeto-ed-minio --entrypoint /bin/sh minio/mc -c "
  mc alias set local http://127.0.0.1:9000 minioadmin minioadmin &&
  mc ls local
" 2>/dev/null || bash "$(dirname "$0")/create_minio_buckets.sh"

echo ""
echo "Console: http://localhost:9091 (minioadmin / minioadmin)"
