#!/usr/bin/env bash
# Verifica Postgres SparkEats e contagens mínimas nas tabelas principais.
set -eu

DOCKER="${DOCKER:-/usr/bin/docker}"
DB_USER="${POSTGRES_USER:-sparkeats}"
DB_NAME="${POSTGRES_DB:-sparkeats}"
MIN_COUNT="${MIN_COUNT:-10000}"

echo "=== Container Postgres ==="
$DOCKER ps --filter name=projeto-ed-postgres --format "{{.Names}} {{.Status}}"

echo ""
echo "=== Conexão ==="
$DOCKER exec projeto-ed-postgres pg_isready -U "$DB_USER" -d "$DB_NAME"

echo ""
echo "=== Contagens (tabelas principais) ==="
$DOCKER exec projeto-ed-postgres psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "
SELECT 'clientes' AS t, COUNT(*)::text FROM clientes
UNION ALL SELECT 'enderecos_cliente', COUNT(*)::text FROM enderecos_cliente
UNION ALL SELECT 'cardapio', COUNT(*)::text FROM cardapio
UNION ALL SELECT 'pedidos', COUNT(*)::text FROM pedidos
UNION ALL SELECT 'itens_pedido', COUNT(*)::text FROM itens_pedido
UNION ALL SELECT 'pagamentos', COUNT(*)::text FROM pagamentos
UNION ALL SELECT 'avaliacoes', COUNT(*)::text FROM avaliacoes
ORDER BY 1;
"

echo ""
echo "=== Pedidos por ano ==="
$DOCKER exec projeto-ed-postgres psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT EXTRACT(YEAR FROM data_hora_pedido)::INT AS ano, COUNT(*) AS total
FROM pedidos GROUP BY 1 ORDER BY 1;
"

echo ""
echo "Conexão host: postgresql://${DB_USER}:sparkeats_dev@localhost:5433/${DB_NAME}"
