#!/usr/bin/env bash
# Recria/valida buckets medalhao no MinIO (util apos docker compose up).
set -eu

DOCKER="${DOCKER:-/usr/bin/docker}"
USER="${MINIO_ROOT_USER:-minioadmin}"
PASS="${MINIO_ROOT_PASSWORD:-minioadmin}"
ALIAS="projeto-ed"

NETWORK=$($DOCKER inspect projeto-ed-minio --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}' 2>/dev/null || true)
ENDPOINT="http://minio:9000"
NET_ARG=""

if [ -z "$NETWORK" ]; then
  ENDPOINT="http://127.0.0.1:9090"
else
  NET_ARG="--network $NETWORK"
fi

$DOCKER run --rm $NET_ARG --entrypoint /bin/sh minio/mc -c "
  mc alias set $ALIAS $ENDPOINT $USER $PASS &&
  mc mb -p $ALIAS/landing-zone 2>/dev/null || true &&
  mc mb -p $ALIAS/bronze 2>/dev/null || true &&
  mc mb -p $ALIAS/silver 2>/dev/null || true &&
  mc mb -p $ALIAS/gold 2>/dev/null || true &&
  mc ls $ALIAS
"

echo "Buckets MinIO OK."
