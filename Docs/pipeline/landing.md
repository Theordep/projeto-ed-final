# Landing Zone

Primeira camada do Data Lake. Recebe os dados brutos extraídos diretamente do PostgreSQL, sem nenhuma transformação.

## Responsabilidade

- Extração das 12 tabelas OLTP do PostgreSQL
- Gravação em **CSV** no disco local (`DATA_ROOT/landing`) com sync para o bucket `landing-zone` do MinIO
- Preservação do formato original da origem

## Tarefa Airflow: `landing_full` / `landing_incremental`

Executada dentro das DAGs `sparkeats_pipeline_full` e `sparkeats_pipeline_incremental`.

| Modo | Tarefa | Comportamento |
|------|--------|---------------|
| Full | `landing_full` | Extrai todas as 12 tabelas |
| Incremental | `landing_incremental` | Extrai apenas registros novos das tabelas fato (por PK) |

Tabelas extraídas (definidas em `src/sparkeats/config.py`):

```
categorias_restaurante, zonas_entrega, cupons, restaurantes, cardapio,
clientes, enderecos_cliente, entregadores, pedidos, itens_pedido,
pagamentos, avaliacoes
```

## Estrutura de arquivos

Os CSVs são organizados por tabela e timestamp de execução:

```
landing/postgres/
├── pedidos/
│   └── 2025/06/24/143022/
│       └── pedidos.csv
├── clientes/
│   └── 2025/06/24/143022/
│       └── clientes.csv
└── ...
```

No MinIO (bucket `landing-zone`), a mesma estrutura é espelhada via `sync_to_minio`.

## Executar manualmente

=== "Airflow UI"
    Acesse http://localhost:8082 e dispare:

    - `sparkeats_pipeline_full` — carga completa (recomendado na 1ª vez)
    - `sparkeats_pipeline_incremental` — apenas registros novos nas tabelas fato

=== "CLI local (WSL)"
    ```bash
    source scripts/wsl-env.sh
    uv run python scripts/run_pipeline.py --step landing
    uv run python scripts/run_pipeline.py --step landing --incremental
    ```

=== "Airflow CLI"
    ```bash
    docker exec projeto-ed-airflow-webserver \
      airflow dags trigger sparkeats_pipeline_full
    ```

## Verificar no MinIO

Acesse o console em http://localhost:9091, bucket `landing-zone`, e confirme os diretórios `postgres/<tabela>/`.

!!! note "Modos de carga"
    Na DAG **full**, todas as tabelas são extraídas por completo. Na DAG **incremental**, apenas `pedidos`, `itens_pedido`, `pagamentos` e `avaliacoes` usam filtro por PK; as demais tabelas continuam em carga completa.
