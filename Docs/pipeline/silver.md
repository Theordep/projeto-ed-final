# Silver

Terceira camada do Data Lake. Aplica limpeza, tipagem e normalização nos dados do Bronze.

## Responsabilidade

- Leitura das tabelas Delta Lake do bucket `bronze`
- Tratamento de nulos, duplicatas e inconsistências
- Padronização de tipos e formatos
- Gravação no bucket `silver` em **Delta Lake**

## DAG: `dag_silver`

```
bronze/<tabela>/  →  (Spark)  →  silver/<tabela>/
```

## Transformações aplicadas

=== "Pedidos"
    - Conversão de `data_hora_pedido` para timestamp padronizado
    - Cálculo de `tempo_entrega_min` quando nulo
    - Remoção de pedidos com `valor_total <= 0`

=== "Clientes"
    - Normalização de `email` para lowercase
    - Mascaramento parcial de `cpf`
    - Filtro de clientes com `status_ativo = TRUE`

=== "Restaurantes"
    - Normalização de `nome_fantasia`
    - Filtro de restaurantes com `status = 'ATIVO'`

=== "Pagamentos"
    - Validação de `valor_pago` vs `valor_total` do pedido
    - Classificação de `forma_pagamento`

## Qualidade dos dados

!!! tip "Regras de qualidade"
    A camada Silver é o ponto de entrada para análises. Qualquer dado que chegar aqui deve estar:

    - [x] Sem duplicatas por chave primária
    - [x] Com tipos corretos (datas como timestamp, valores como decimal)
    - [x] Sem nulos em colunas obrigatórias
    - [x] Com valores dentro dos domínios esperados