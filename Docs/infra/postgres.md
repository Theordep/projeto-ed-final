# Guia — PostgreSQL SparkEats (banco origem)

O **PostgreSQL** simula o banco transacional (OLTP) do app **SparkEats** — de onde o pipeline extrai dados para o Data Lake.

Issue: [#7](https://github.com/Theordep/projeto-ed-final/issues/7)

---

## Papel no pipeline

```text
PostgreSQL (sparkeats)     →     Landing (CSV)     →     Bronze → Silver → Gold
   12 tabelas OLTP              bucket MinIO              Delta Lake
   50.000 pedidos
```

É a **fonte de verdade** operacional: clientes, restaurantes, pedidos, pagamentos, avaliações.

---

## Conexão

| Campo | Valor |
|-------|--------|
| Host | `localhost` |
| Porta | **5433** |
| Database | `sparkeats` |
| Usuário | `sparkeats` |
| Senha | `sparkeats_dev` |

URL completa:

```text
postgresql://sparkeats:sparkeats_dev@localhost:5433/sparkeats
```

Já exportada no `wsl-env.sh` como `DATABASE_URL`.

### Por que porta 5433?

A porta **5432** no Windows costuma ser outro PostgreSQL (local ou Docker antigo). O compose mapeia `5433` (host) → `5432` (dentro do container).

---

## Subir o banco

```bash
cd /mnt/c/projeto-ed-final
source scripts/wsl-env.sh
bash scripts/start-docker.sh

dcompose up -d postgres
bash scripts/verify-postgres.sh
```

Container esperado: `projeto-ed-postgres` com status **healthy**.

---

## Estrutura do banco (12 tabelas)

### Dimensões e apoio

| Tabela | Registros (seed) |
|--------|------------------|
| `categorias_restaurante` | 10 |
| `zonas_entrega` | 20 (Criciúma + expansão TO) |
| `cupons` | 50 |
| `restaurantes` | 500 |
| `cardapio` | 10.000 |
| `clientes` | 10.000 |
| `enderecos_cliente` | ≥ 12.000 |
| `entregadores` | 500 |

### Transações (alto volume)

| Tabela | Registros (seed) |
|--------|------------------|
| `pedidos` | **50.000** |
| `itens_pedido` | ~150.000 |
| `pagamentos` | 50.000 |
| `avaliacoes` | ~29.000 |

DDL completo: `sql/ddl_origem_postgresql.sql`

---

## Popular com dados (seed Faker)

Pré-requisito: [uv instalado](../quickstart/prerequisitos.md).

```bash
cd /mnt/c/projeto-ed-final
source scripts/wsl-env.sh

uv sync
uv run python scripts/seed_database.py
```

O script:

1. Aplica o DDL (`sql/ddl_origem_postgresql.sql`)
2. Limpa tabelas (`TRUNCATE` — só em dev)
3. Gera dados com **Faker** (`pt_BR`)
4. Valida ≥ 10.000 linhas nas tabelas principais
5. Imprime contagem por tabela e pedidos por ano

Tempo estimado: **~5–6 minutos** (50k pedidos).

### Reset completo (banco zerado)

```bash
dcompose down -v postgres
dcompose up -d postgres
uv run python scripts/seed_database.py
```

---

## Consultas no terminal

```bash
# Total de pedidos
dcompose exec postgres psql -U sparkeats -d sparkeats -c "SELECT COUNT(*) FROM pedidos;"

# Por status
dcompose exec postgres psql -U sparkeats -d sparkeats -c \
  "SELECT status_pedido, COUNT(*) FROM pedidos GROUP BY 1 ORDER BY 2 DESC;"

# Por ano
dcompose exec postgres psql -U sparkeats -d sparkeats -c \
  "SELECT EXTRACT(YEAR FROM data_hora_pedido)::INT AS ano, COUNT(*) FROM pedidos GROUP BY 1 ORDER BY 1;"

# Amostra de pedidos entregues
dcompose exec postgres psql -U sparkeats -d sparkeats -c \
  "SELECT id_pedido, data_hora_pedido, valor_total, tempo_entrega_min FROM pedidos WHERE status_pedido = 'ENTREGUE' LIMIT 5;"
```

---

## DBeaver (Windows)

1. **Database** → **New Database Connection** → **PostgreSQL**
2. Preencha:

| Campo | Valor |
|-------|--------|
| Host | `localhost` |
| Port | `5433` |
| Database | `sparkeats` |
| Username | `sparkeats` |
| Password | `sparkeats_dev` |

3. **Test Connection** → **Finish**
4. Navegue: `sparkeats` → **Schemas** → **public** → **Tables**

### Consultas úteis no DBeaver

```sql
SELECT COUNT(*) FROM pedidos;
SELECT COUNT(*) FROM clientes;
SELECT * FROM cardapio WHERE nome_item ILIKE '%sushi%' LIMIT 20;
SELECT p.id_pedido, p.valor_total, a.nota_geral
FROM pedidos p
LEFT JOIN avaliacoes a ON a.id_pedido = p.id_pedido
WHERE p.status_pedido = 'ENTREGUE'
LIMIT 20;
```

---

## Colunas importantes (pipeline e dashboard)

### SCD Tipo 2 (dimensões)

Em `clientes` e `enderecos_cliente`:

- `data_inicio`, `data_fim`, `status_ativo`

~20% dos clientes têm histórico de endereço (endereço antigo inativo + novo ativo).

### Carga incremental

Em **todas** as tabelas:

- `created_at`, `updated_at`

O pipeline incremental na landing filtra tabelas fato por **PK** (`id_pedido`, etc.) usando checkpoint em arquivo. O campo `updated_at` existe nas tabelas e é usado pelo seed para simular alterações (SCD2 na Gold).

### Pedidos (fato central)

| Coluna | Uso |
|--------|-----|
| `data_hora_pedido` | Particionamento / filtro temporal |
| `data_hora_coleta` | Motoboy retirou no restaurante |
| `data_hora_entrega` | Entrega ao cliente |
| `status_pedido` | ENTREGUE, CANCELADO, EM_TRANSITO, PREPARANDO |
| `valor_total` | KPI receita / ticket médio |
| `tempo_entrega_min` | KPI tempo médio de entrega |

### Avaliações e itens

| Tabela | Métrica futura |
|--------|----------------|
| `itens_pedido.quantidade` | Qtd itens vendidos |
| `avaliacoes.nota_geral` | Nota média no dashboard |

---

## KPIs do dashboard (referência)

| Tipo | Indicador | Fonte |
|------|-----------|--------|
| KPI | Receita total | `pedidos.valor_total` (não cancelados) |
| KPI | Pedidos entregues | `status_pedido = 'ENTREGUE'` |
| KPI | Ticket médio | `AVG(valor_total)` |
| KPI | Tempo médio entrega | `tempo_entrega_min` |
| Métrica | Qtd itens vendidos | `SUM(itens_pedido.quantidade)` |
| Métrica | Nota média | `AVG(avaliacoes.nota_geral)` |

---

## Problemas comuns

### `password authentication failed for user "sparkeats"`

O volume Docker foi criado com **outro** usuário (ex.: projeto EntregaSATC). Recrie o volume:

```bash
dcompose down -v postgres
dcompose up -d postgres
uv run python scripts/seed_database.py
```

### DBeaver não conecta

- Confirme porta **5433** (não 5432)
- Container rodando: `docker ps --filter name=projeto-ed-postgres`
- Teste no WSL: `bash scripts/verify-postgres.sh`

### `relation "pedidos" does not exist`

Rode o seed — ele aplica o DDL:

```bash
uv run python scripts/seed_database.py
```

### Seed lento ou travado

Normal para 50k pedidos. Acompanhe a saída:

```text
pedidos processados: 25,000/50,000
```

### Conflito de porta 5433

Outro container usando a porta:

```bash
docker ps --format "{{.Names}} {{.Ports}}" | grep 5433
```

Pare o stack concorrente antes de subir o `projeto-ed-final`.

---

## Fluxo completo (checklist)

- [ ] `source scripts/wsl-env.sh`
- [ ] `dcompose up -d postgres`
- [ ] `uv sync && uv run python scripts/seed_database.py`
- [ ] `bash scripts/verify-postgres.sh`
- [ ] DBeaver conectado — 50.000 em `pedidos`

---

## Ver também

- [Pré-requisitos](../quickstart/prerequisitos.md) — uv e ferramentas
- [Guia Docker](./docker.md) — compose e volumes
- [Guia MinIO](./minio.md) — destino dos dados após extração
