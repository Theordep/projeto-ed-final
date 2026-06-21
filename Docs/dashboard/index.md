# Dashboard — KPIs e métricas

O dashboard consome os dados da camada Gold e apresenta os indicadores de performance da plataforma SparkEats.

## KPIs

| # | KPI | Cálculo | Origem |
|---|-----|---------|--------|
| 1 | **Ticket médio** | `SUM(valor_total) / COUNT(pedidos)` | `fato_pedidos` |
| 2 | **Taxa de cancelamento** | `COUNT(status='CANCELADO') / COUNT(*)` | `fato_pedidos` |
| 3 | **Tempo médio de entrega** | `AVG(tempo_entrega_min)` | `fato_pedidos` |
| 4 | **Avaliação média** | `AVG(nota_geral)` | `fato_pedidos` |

## Métricas

| # | Métrica | Descrição |
|---|---------|-----------|
| 1 | **Pedidos por período** | Volume de pedidos agregado por dia / semana / mês |
| 2 | **Receita por zona** | Faturamento total por zona de entrega |

## Filtros disponíveis

- Período (data início / data fim)
- Restaurante
- Zona de entrega
- Forma de pagamento
- Status do pedido

## Ferramenta de visualização

> Adicione aqui a ferramenta utilizada (ex: Power BI, Metabase, Superset, Streamlit) e o link de acesso ao dashboard.

!!! info "Fonte dos dados"
    O dashboard lê diretamente da camada `gold` no MinIO via Spark, ou de um banco relacional com os dados virtualizados.