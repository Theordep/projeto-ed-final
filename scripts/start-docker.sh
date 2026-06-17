#!/usr/bin/env bash
# Inicia Docker Engine no WSL (sem Docker Desktop).
# Uso: bash scripts/start-docker.sh

set -eu

if pgrep -x dockerd >/dev/null 2>&1; then
  echo "Docker ja esta rodando."
  /usr/bin/docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null | head -6
  exit 0
fi

echo "Iniciando Docker..."
echo "${SUDO_PASS:-}" | sudo -S service docker start
sleep 2
/usr/bin/docker ps --format "table {{.Names}}\t{{.Status}}"
