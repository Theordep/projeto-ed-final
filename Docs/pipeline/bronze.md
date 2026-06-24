# Bronze

Segunda camada do Data Lake. Converte os arquivos CSV da landing para **Delta Lake**, preservando a estrutura original da origem.

## Responsabilidade

- Leitura dos CSVs da landing (`landing/postgres/<tabela>/`)
- Conversão para formato **Delta Lake**
- Gravação em `bronze/postgres/<tabela>/` com sync para o bucket `bronze`
- Sem transformações de negócio — apenas mudança de formato e metadados de ingestão

## Tarefa Airflow: `bronze`

Executada nas DAGs `sparkeats_pipeline_full` e `sparkeats_pipeline_incremental`, sempre após a landing.

```
landing/postgres/<tabela>/*.csv  →  (PySpark)  →  bronze/postgres/<tabela>/
```

Metadados adicionados: `_ingested_at`, `_source_table`, `_source_layer`.

## Estrutura no MinIO

```
bronze/
└── postgres/
    ├── restaurantes/
    │   └── _delta_log/
    ├── clientes/
    │   └── _delta_log/
    ├── pedidos/
    │   └── _delta_log/
    └── ...
```

## Por que Delta Lake?

!!! info "Benefícios do Delta Lake"
    - **ACID transactions** — escrita segura mesmo em caso de falha
    - **Time travel** — consulta versões anteriores dos dados
    - **Schema enforcement** — rejeita dados que não respeitam o schema
    - **Suporte a merge/upsert** — base para checkpoints na camada Gold

## Executar manualmente

=== "Airflow UI"
    Dispare `sparkeats_pipeline_full` ou `sparkeats_pipeline_incremental` — a tarefa `bronze` roda automaticamente após a landing.

=== "CLI local (WSL)"
    ```bash
    source scripts/wsl-env.sh
    uv run python scripts/run_pipeline.py --step bronze
    ```

!!! warning "Dependência"
    A tarefa `bronze` requer CSVs na landing. Na prática, execute o pipeline completo ou garanta que a landing já rodou.

!!! note "Modo de escrita"
    Bronze sempre usa `overwrite` — reprocessa todas as tabelas a cada execução.
