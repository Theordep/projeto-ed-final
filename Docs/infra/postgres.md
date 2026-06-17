# PostgreSQL — Banco origem SparkEats (Issue #7)

Banco relacional OLTP que simula o app **SparkEats** (delivery de alimentos).

## Serviço Docker

| Item | Valor |
|------|--------|
| Imagem | `postgres:16-alpine` |
| Container | `projeto-ed-postgres` |
| Porta host | **5433** |
| Database | `sparkeats` |
| Usuário | `sparkeats` |
| Senha | `sparkeats_dev` |

## Subir apenas o Postgres

```bash
cd /mnt/c/projeto-ed-final
source scripts/wsl-env.sh
dcompose up -d postgres
bash scripts/verify-postgres.sh
```

## DDL e seed

O script `scripts/seed_database.py`:

1. Aplica `sql/ddl_origem_postgresql.sql`
2. Popula as **12 tabelas** com Faker (`pt_BR`)
3. Valida volumes mínimos (≥ 10.000 nas tabelas principais, 50.000 pedidos)

### Pré-requisitos

- [UV](https://docs.astral.sh/uv/) instalado no WSL
- Postgres rodando (`dcompose up -d postgres`)

### Executar

```bash
source scripts/wsl-env.sh
uv sync
uv run python scripts/seed_database.py
```

Variável opcional:

```bash
export DATABASE_URL="postgresql://sparkeats:sparkeats_dev@localhost:5433/sparkeats"
```

## Volumes gerados

| Tabela | Volume alvo |
|--------|-------------|
| `clientes` | 10.000 |
| `enderecos_cliente` | ≥ 12.000 |
| `cardapio` | 10.000 |
| `pedidos` | 50.000 |
| `itens_pedido` | ≥ 150.000 (derivado) |
| `pagamentos` | 50.000 |
| `avaliacoes` | ~85% dos entregues |

Datas dos pedidos: **2023-01-01** até **2026-06-10** (distribuição natural).

## Modelo

- **SCD Tipo 2 (origem):** `data_inicio`, `data_fim`, `status_ativo` em `clientes` e `enderecos_cliente`
- **Incremental:** `created_at` e `updated_at` em todas as tabelas
- **Pedidos:** `data_hora_pedido`, `data_hora_coleta`, `data_hora_entrega`, `status_pedido`

## Consultas úteis

```bash
dcompose exec postgres psql -U sparkeats -d sparkeats -c "SELECT COUNT(*) FROM pedidos;"
dcompose exec postgres psql -U sparkeats -d sparkeats -c \
  "SELECT status_pedido, COUNT(*) FROM pedidos GROUP BY 1;"
```

## KPIs alimentados (dashboard futuro)

| Indicador | Origem |
|-----------|--------|
| Receita total | `pedidos.valor_total` |
| Pedidos entregues | `pedidos.status_pedido = 'ENTREGUE'` |
| Ticket médio | `pedidos.valor_total` |
| Tempo médio entrega | `pedidos.tempo_entrega_min` |
| Qtd itens vendidos | `itens_pedido.quantidade` |
| Nota média | `avaliacoes.nota_geral` |

## Parar / resetar dados

```bash
dcompose down          # mantém volume postgres_data
dcompose down -v       # apaga volumes (postgres + minio)
```
