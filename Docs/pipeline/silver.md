# Silver

Terceira camada do Data Lake. Aplica limpeza, tipagem e normalização nos dados do Bronze.

## Responsabilidade

- Leitura das tabelas Delta Lake em `bronze/postgres/<tabela>/`
- Tratamento de nulos, duplicatas e inconsistências
- Padronização de tipos e formatos
- Gravação em `silver/postgres/<tabela>/` com sync para o bucket `silver`

## Tarefa Airflow: `silver`

Executada nas DAGs `sparkeats_pipeline_full` e `sparkeats_pipeline_incremental`, após a bronze.

```
bronze/postgres/<tabela>/  →  (PySpark)  →  silver/postgres/<tabela>/
```

## Transformações aplicadas

=== "Pedidos"
    - Conversão de `data_hora_pedido`, `data_hora_coleta` e `data_hora_entrega` para timestamp
    - Cálculo de `tempo_entrega_min` quando nulo (pedidos ENTREGUE)
    - Remoção de pedidos com `valor_total <= 0`
    - Deduplicação por `id_pedido`

=== "Clientes"
    - Normalização de `email` para lowercase
    - Mascaramento parcial de `cpf` (LGPD)
    - Filtro de clientes com `status_ativo = TRUE`
    - Deduplicação por `id_cliente`

=== "Restaurantes"
    - Normalização de `nome_fantasia` e `status`
    - Filtro de restaurantes com `status = 'ATIVO'`
    - Deduplicação por `id_restaurante`

=== "Endereços"
    - Padronização de `cidade`, `bairro` e `logradouro`
    - Deduplicação por `id_endereco`

=== "Pagamentos"
    - Normalização de `forma_pagamento` e `status_pagamento` (uppercase)
    - Filtro de registros com `valor_pago <= 0`
    - Deduplicação por `id_pagamento`

=== "Demais tabelas"
    - Deduplicação genérica

## Qualidade dos dados

!!! tip "Regras de qualidade"
    A camada Silver é o ponto de entrada para análises. Os dados devem estar:

    - [x] Sem duplicatas por chave primária
    - [x] Com tipos corretos (datas como timestamp, valores como decimal)
    - [x] Com valores dentro dos domínios esperados nas tabelas com regras específicas

## Executar manualmente

```bash
source scripts/wsl-env.sh
uv run python scripts/run_pipeline.py --step silver
```

Ou dispare uma das DAGs no Airflow — a tarefa `silver` roda após a bronze.

!!! note "Modo de escrita"
    Silver sempre usa `overwrite` — reprocessa todas as tabelas a cada execução.
