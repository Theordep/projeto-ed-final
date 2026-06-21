#!/usr/bin/env bash
# Verifica artefatos do pipeline (Landing → Bronze → Silver). Issue #16
set -eu

DATA_ROOT="${DATA_ROOT:-/tmp/sparkeats-data}"
DOCKER="${DOCKER:-/usr/bin/docker}"

echo "=== DATA_ROOT ==="
echo "$DATA_ROOT"
echo ""

echo "=== Landing (CSV) ==="
find "$DATA_ROOT/landing/postgres" -name "*.csv" 2>/dev/null | head -5 || echo "(nenhum CSV)"
echo ""

echo "=== Bronze (Delta) ==="
find "$DATA_ROOT/bronze/postgres" -name "_delta_log" 2>/dev/null | wc -l | xargs echo "tabelas delta:"
echo ""

echo "=== Silver (Delta) ==="
find "$DATA_ROOT/silver/postgres" -name "_delta_log" 2>/dev/null | wc -l | xargs echo "tabelas delta:"
echo ""

echo "=== MinIO buckets ==="
$DOCKER run --rm --network container:projeto-ed-minio --entrypoint /bin/sh minio/mc -c "
  mc alias set local http://127.0.0.1:9000 minioadmin minioadmin 2>/dev/null &&
  mc ls local/landing-zone/postgres 2>/dev/null | head -3 &&
  mc ls local/bronze/postgres 2>/dev/null | head -3 &&
  mc ls local/silver/postgres 2>/dev/null | head -3
" 2>/dev/null || echo "(MinIO offline ou sem sync)"

echo ""
echo "Console MinIO: http://localhost:9091"
