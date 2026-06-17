# Guia — Faker (geração de dados fictícios)

O **Faker** é a biblioteca Python que usamos para popular o banco **SparkEats** com dados realistas — sem INSERT manual. O professor permite (e recomenda) esse tipo de geração para a massa de dados de origem.

Script do projeto: `scripts/seed_database.py`  
Issue: [#7](https://github.com/Theordep/projeto-ed-final/issues/7)

---

## O que é o Faker?

Biblioteca que gera dados falsos mas **plausíveis**: nomes, e-mails, CPF, endereços, datas, frases, etc.

Site: [https://faker.readthedocs.io/](https://faker.readthedocs.io/)

No repositório:

```toml
# pyproject.toml
dependencies = [
    "faker>=24.0",
    ...
]
```

---

## Por que usamos no trabalho?

| Requisito do PDF | Como o Faker ajuda |
|------------------|-------------------|
| ≥ 10.000 linhas nas tabelas principais | Gera 50k pedidos + derivados em loop |
| Dados dos últimos 3 anos | `date_time_between(2023, 2026)` |
| Não precisa ser INSERT manual | Tudo via script reproduzível |
| Domínio delivery credível | Locale `pt_BR` + menus curados |

---

## Como rodar no SparkEats

```bash
cd /mnt/c/projeto-ed-final
source scripts/wsl-env.sh

dcompose up -d postgres
uv sync
uv run python scripts/seed_database.py
```

O script:

1. Aplica o DDL (`sql/ddl_origem_postgresql.sql`)
2. Faz `TRUNCATE` das tabelas (ambiente dev)
3. Popula na ordem das dependências (FK)
4. Imprime contagens e valida volumes mínimos
5. Encerra com `Seed concluído com sucesso.`

Tempo: **~5–6 min** (50.000 pedidos).

---

## Configuração do Faker no projeto

```python
from faker import Faker
import random

fake = Faker("pt_BR")   # dados brasileiros (CPF, nomes, etc.)
Faker.seed(42)          # reprodutibilidade
random.seed(42)         # sorteios (status, itens, etc.)
```

### Locale `pt_BR`

| Método Faker | Uso no seed |
|--------------|-------------|
| `fake.name()` | Clientes, entregadores |
| `fake.unique.email()` | E-mail único por cliente |
| `fake.unique.cpf()` | CPF sem duplicata |
| `fake.unique.cnpj()` | CNPJ dos restaurantes |
| `fake.phone_number()` | Telefone |
| `fake.company()` | Nome fantasia / razão social |
| `fake.street_name()` | Logradouro |
| `fake.postcode()` | CEP |
| `fake.date_between(...)` | Cadastros, cupons |
| `fake.date_time_between(...)` | Pedidos, `updated_at` |
| `fake.sentence(nb_words=8)` | Comentário de avaliação |

`fake.unique.*` evita violar `UNIQUE` no PostgreSQL (ex.: CPF repetido).

---

## O que é Faker vs o que é fixo no código

Nem tudo vem do Faker — parte é **curadoria** para dados consistentes:

| Fonte | Exemplos |
|-------|----------|
| **Listas fixas** | `CATEGORIAS`, `ZONAS_SC`, `ZONAS_TO` |
| **Templates de cardápio** | `MENU_TEMPLATES` — combos sushi, pizzas, etc. |
| **Faker** | Nomes, documentos, endereços, datas aleatórias |
| **`random`** | Status do pedido, quantidade de itens, cupom sim/não |

### Cardápio curado

Cada restaurante recebe **20 itens** da categoria dele (`MENU_TEMPLATES`). Itens com palavras em `EXCLUDED_KEYWORDS` (porco, fígado, coração…) são filtrados.

### Zonas de entrega

- **15 bairros** de Criciúma (SC)
- **5 cidades** do Tocantins (expansão futura do SparkEats)

---

## Ordem de geração (respeita FK)

```text
categorias → zonas → cupons → restaurantes → cardapio
    → clientes → enderecos → entregadores
        → pedidos → itens_pedido + pagamentos + avaliacoes
            → simulate_cliente_updates (incremental)
```

---

## Volumes gerados

| Constante | Valor |
|-----------|-------|
| `N_CLIENTES` | 10.000 |
| `N_PEDIDOS` | 50.000 |
| `N_RESTAURANTES` | 500 |
| `ITENS_POR_RESTAURANTE` | 20 → 10.000 no cardápio |
| `MIN_LINHAS_PRINCIPAL` | 10.000 (validação) |

Tabelas derivadas dos pedidos:

- `itens_pedido` — ~150.000 (1–5 itens por pedido, qtd 1–3)
- `pagamentos` — 50.000 (1 por pedido)
- `avaliacoes` — ~85% dos pedidos `ENTREGUE`

---

## Regras de negócio simuladas

### Status do pedido

Distribuição em `STATUS_PEDIDO`:

| Status | ~% |
|--------|-----|
| ENTREGUE | 68% |
| CANCELADO | 10% |
| EM_TRANSITO | 12% |
| PREPARANDO | 10% |

### Timestamps do pedido

| Status | `data_hora_coleta` | `data_hora_entrega` |
|--------|--------------------|---------------------|
| PREPARANDO | — | — |
| CANCELADO | — | — |
| EM_TRANSITO | pedido + 15–40 min | — |
| ENTREGUE | pedido + 15–40 min | coleta + 18–75 min |

`tempo_entrega_min` = minutos entre pedido e entrega (só ENTREGUE).

### Pagamentos

- Forma: PIX, CARTAO ou DINHEIRO (aleatório)
- `CANCELADO` → `status_pagamento = ESTORNADO`
- Demais → `APROVADO`

### Cupons

~11% dos pedidos com desconto (5–15% do valor dos itens).

### Avaliações

Só em pedidos **ENTREGUE**; ~85% recebem nota (3,0–5,0) + comentário Faker.

### SCD / carga incremental

| Simulação | % | O que faz |
|-----------|---|-----------|
| Endereço histórico | 20% clientes | 2 endereços; antigo com `status_ativo=false` |
| `updated_at` variado | 15% registros | Data posterior ao `created_at` |
| Update de cliente | 8% clientes | Novo telefone + `updated_at` nos últimos 30 dias |

Isso prepara a demo de **carga incremental** no pipeline.

### Datas dos pedidos

Distribuição **natural** entre `2023-01-01` e `2026-06-10` (sem percentual fixo por ano).

---

## Performance — inserção em lote

50k pedidos exigem batch insert:

| Constante | Valor | Função |
|-----------|-------|--------|
| `PEDIDO_BATCH` | 2.500 | Insere pedidos em blocos |
| `INSERT_BATCH` | 5.000 | Itens, clientes, endereços |

Fluxo por lote de pedidos:

1. `INSERT` pedidos (valores zerados)
2. `SELECT` ids inseridos
3. Monta itens, pagamentos, avaliações em memória
4. `UPDATE` pedidos com totais e timestamps
5. `INSERT` itens / pagamentos / avaliações

---

## Validação automática

Ao final, `validate_minimums()` verifica:

- ≥ 10.000 linhas em: `clientes`, `enderecos_cliente`, `cardapio`, `pedidos`, `itens_pedido`, `pagamentos`, `avaliacoes`
- ≥ 50.000 em `pedidos`

Se falhar, o script termina com código de erro e lista o que ficou abaixo.

---

## Conferir no banco

```bash
dcompose exec postgres psql -U sparkeats -d sparkeats -c "
SELECT 'pedidos' AS t, COUNT(*) FROM pedidos
UNION ALL SELECT 'clientes', COUNT(*) FROM clientes
UNION ALL SELECT 'avaliacoes', COUNT(*) FROM avaliacoes;
"
```

Ou no **DBeaver** — ver [guia PostgreSQL](./postgres.md).

---

## Problemas comuns

### `duplicate key value violates unique constraint "clientes_cpf_key"`

CPF repetido — o projeto usa `fake.unique.cpf()`. Se alterar o seed ou rodar parcialmente, limpe e rode de novo:

```bash
uv run python scripts/seed_database.py
```

### Seed muito lento

Normal para 50k. Acompanhe:

```text
pedidos processados: 25,000/50,000
```

### Dados diferentes a cada execução

Com `Faker.seed(42)` e `random.seed(42)`, a massa é **reproduzível**. Se mudar os seeds, os dados mudam.

### `ModuleNotFoundError: No module named 'faker'`

```bash
uv sync
uv run python scripts/seed_database.py
```

---

## Exemplo mínimo (fora do projeto)

Para entender o Faker isoladamente:

```python
from faker import Faker

fake = Faker("pt_BR")
print(fake.name())
print(fake.cpf())
print(fake.email())
print(fake.date_time_between(start_date="-3y", end_date="now"))
```

---

## Carga incremental (futuro)

O trabalho pede demo inserindo pedidos novos após a carga full. O seed atual já simula **updates** em clientes; um script `seed_incremental.py` (issue futura) pode inserir dezenas de pedidos extras para subir KPIs no dashboard.

---

## Ver também

- [Guia UV](./uv.md) — `uv run python scripts/seed_database.py`
- [Guia PostgreSQL](./postgres.md) — DDL, DBeaver, modelo
- [Guia Docker](./docker.md) — Postgres no container
