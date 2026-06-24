# Gold — Silver → Modelo Dimensional

A camada **Gold** consolida os dados da Silver em um **Star Schema** pronto para o dashboard.

## Entrada e saída

| Item | Valor |
|------|--------|
| Entrada | Delta Silver (`{DATA_ROOT}/silver/postgres/<tabela>/`) |
| Saída | Delta Gold (`{DATA_ROOT}/gold/`) + sync MinIO bucket `gold` |
| Export | PostgreSQL schema `analytics` (tarefa `export_to_pg`) |

`DATA_ROOT` depende do ambiente:

| Ambiente | `DATA_ROOT` |
|----------|-------------|
| WSL local (`wsl-env.sh`) | `/tmp/sparkeats-data` |
| Container Airflow | `/data/sparkeats` |

## Tarefas Airflow: `gold_full` / `gold_incremental` + `export_to_pg`

| Modo | Tarefa Gold | Comportamento |
|------|-------------|---------------|
| Full | `gold_full` | Reconstrói dimensões e fato (`overwrite`) |
| Incremental | `gold_incremental` | Append em `fato_pedidos` via checkpoint |

Após o gold, `export_to_pg` espelha as tabelas no schema `analytics` para consumo pelo Metabase.

## Tabelas geradas

| Tabela | Tipo | Descrição |
|--------|------|-----------|
| `dim_tempo` | Dimensão | Calendário 2023–2026 |
| `dim_cliente` | Dimensão SCD2 | Cliente + endereço principal |
| `dim_restaurante` | Dimensão SCD2 | Restaurante + categoria + zona |
| `dim_entregador` | Dimensão | Entregador + zona |
| `dim_pagamento` | Dimensão | Forma e status de pagamento |
| `fato_pedidos` | Fato | 1 linha por pedido |
| `checkpoint_fato_pedidos` | Controle | Checkpoint para carga incremental |

Detalhes das colunas: [Modelo dimensional](../modelo/dimensional.md).

## SCD Tipo 2

`dim_cliente` e `dim_restaurante` rastreiam alterações em atributos-chave:

- **Cliente:** `cidade`, `estado`, `bairro`
- **Restaurante:** `taxa_comissao`, `categoria`, `zona`, `cidade`

Nova versão → `dt_inicio` atual, versão anterior → `dt_fim` + `ativo = false`.

## Checkpoint incremental

A `fato_pedidos` suporta carga incremental via `checkpoint_fato_pedidos`:

- Filtra pedidos com `data_hora_pedido` > última data processada
- Desempate por `id_pedido`
- Modo `append` na fato após carga inicial

## Execução

=== "Airflow UI"
    - `sparkeats_pipeline_full` — primeira carga ou reprocessamento completo
    - `sparkeats_pipeline_incremental` — novos pedidos (requer full prévio)

=== "CLI local (WSL)"
    ```bash
    source scripts/wsl-env.sh

    # Carga completa (recomendado na 1ª vez)
    uv run python scripts/run_pipeline.py --step gold

    # Pipeline completo
    uv run python scripts/run_pipeline.py

    # Incremental (landing + gold)
    uv run python scripts/run_pipeline.py --incremental

    # Só gold incremental (Silver já atualizada)
    uv run python scripts/run_pipeline.py --step gold --incremental
    ```

## Validação

```bash
bash scripts/verify-pipeline.sh
```

Console MinIO: http://localhost:9091 → bucket `gold` → `dim_*`, `fato_pedidos`.
