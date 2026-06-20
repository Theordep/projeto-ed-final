# Modelo Dimensional (Gold)

O modelo dimensional da camada Gold segue o padrão **Star Schema**, com uma tabela fato central e dimensões ao redor.

## Diagrama

> Insira aqui o diagrama do modelo dimensional (use [dbdiagram.io](https://dbdiagram.io)).

## Tabela Fato

### `fato_pedidos`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `sk_pedido` | BIGINT PK | Surrogate key |
| `sk_cliente` | BIGINT FK | → `dim_cliente` |
| `sk_restaurante` | BIGINT FK | → `dim_restaurante` |
| `sk_entregador` | BIGINT FK | → `dim_entregador` |
| `sk_tempo` | BIGINT FK | → `dim_tempo` |
| `sk_pagamento` | BIGINT FK | → `dim_pagamento` |
| `id_pedido` | BIGINT | Chave natural |
| `valor_itens` | DECIMAL | Valor dos itens |
| `taxa_entrega` | DECIMAL | Taxa de entrega |
| `desconto` | DECIMAL | Desconto aplicado |
| `valor_total` | DECIMAL | Valor final |
| `tempo_entrega_min` | INT | Duração da entrega |
| `status_pedido` | VARCHAR | Status do pedido |
| `nota_geral` | DECIMAL | Avaliação do pedido |

## Dimensões

=== "dim_cliente"
    | Coluna | Tipo | Descrição |
    |--------|------|-----------|
    | `sk_cliente` | BIGINT PK | Surrogate key |
    | `id_cliente` | INT | Chave natural |
    | `nome` | VARCHAR | Nome do cliente |
    | `cidade` | VARCHAR | Cidade do endereço principal |
    | `estado` | CHAR(2) | UF |
    | `dt_inicio` | DATE | Início da versão (SCD2) |
    | `dt_fim` | DATE | Fim da versão (SCD2) |
    | `ativo` | BOOLEAN | Versão atual |

=== "dim_restaurante"
    | Coluna | Tipo | Descrição |
    |--------|------|-----------|
    | `sk_restaurante` | BIGINT PK | Surrogate key |
    | `id_restaurante` | INT | Chave natural |
    | `nome_fantasia` | VARCHAR | Nome comercial |
    | `categoria` | VARCHAR | Tipo de culinária |
    | `zona` | VARCHAR | Bairro de atuação |
    | `cidade` | VARCHAR | Cidade |
    | `taxa_comissao` | DECIMAL | Comissão |

=== "dim_entregador"
    | Coluna | Tipo | Descrição |
    |--------|------|-----------|
    | `sk_entregador` | BIGINT PK | Surrogate key |
    | `id_entregador` | INT | Chave natural |
    | `nome` | VARCHAR | Nome |
    | `veiculo` | VARCHAR | Tipo de veículo |
    | `zona` | VARCHAR | Zona de atuação |

=== "dim_tempo"
    | Coluna | Tipo | Descrição |
    |--------|------|-----------|
    | `sk_tempo` | BIGINT PK | Surrogate key |
    | `data` | DATE | Data do pedido |
    | `ano` | INT | Ano |
    | `mes` | INT | Mês (1–12) |
    | `dia` | INT | Dia |
    | `dia_semana` | VARCHAR | Nome do dia |
    | `trimestre` | INT | Trimestre |
    | `fim_de_semana` | BOOLEAN | Sábado ou domingo |

=== "dim_pagamento"
    | Coluna | Tipo | Descrição |
    |--------|------|-----------|
    | `sk_pagamento` | BIGINT PK | Surrogate key |
    | `forma_pagamento` | VARCHAR | PIX / CARTAO / DINHEIRO |
    | `status_pagamento` | VARCHAR | APROVADO / PENDENTE / ESTORNADO |

## SCD Tipo 2

As dimensões `dim_cliente` e `dim_restaurante` implementam **Slowly Changing Dimension tipo 2**: alterações geram uma nova linha com `dt_inicio` atualizado, enquanto a versão anterior tem `dt_fim` preenchido e `ativo = FALSE`.