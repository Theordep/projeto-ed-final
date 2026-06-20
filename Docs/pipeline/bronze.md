# Bronze

Segunda camada do Data Lake. Converte os arquivos CSV da landing para **Delta Lake**, preservando a estrutura original da origem.

## Responsabilidade

- Leitura dos CSVs do bucket `landing-zone`
- Conversão para formato **Delta Lake**
- Gravação no bucket `bronze`
- Sem transformações de negócio — apenas mudança de formato

## DAG: `dag_bronze`

```
landing-zone/*.csv  →  (Spark)  →  bronze/<tabela>/
```

## Estrutura no MinIO

```
bronze/
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
    - **Carga incremental** — suporte nativo a merge/upsert

## Executar manualmente

Na Airflow UI, dispare a DAG `dag_bronze` **após** a `dag_landing` ter concluído com sucesso.

!!! warning "Dependência"
    A DAG `dag_bronze` requer que os CSVs da `landing-zone` estejam atualizados. Execute sempre na sequência.