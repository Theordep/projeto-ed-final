# Geração de dados

O banco PostgreSQL é populado com dados sintéticos gerados pela biblioteca **Faker**, via `scripts/seed_database.py`.

## Executar o seed

```bash
uv run python scripts/seed_database.py
```

O script aplica o DDL, faz `TRUNCATE` das tabelas e popula na ordem das FKs. Tempo estimado: **5–6 minutos** (50.000 pedidos).

## O que é gerado

| Tabela | Volume | Distribuição |
|--------|--------|-------------|
| `categorias_restaurante` | 10 | — |
| `zonas_entrega` | 20 | Criciúma (SC) + Tocantins |
| `cupons` | 50 | — |
| `restaurantes` | 500 | — |
| `cardapio` | 10.000 | 20 itens por restaurante |
| `clientes` | 10.000 | — |
| `enderecos_cliente` | ≥ 10.000 | 1–2 por cliente |
| `entregadores` | 500 | — |
| `pedidos` | 50.000 | 2023-01-01 a 2026-06-10 |
| `itens_pedido` | ~150.000 | 1–5 itens por pedido |
| `pagamentos` | 50.000 | 1 por pedido |
| `avaliacoes` | ~42.500 | ~85% dos pedidos ENTREGUE |

!!! info "Distribuição temporal"
    Os pedidos são distribuídos nos últimos 3 anos com sazonalidade realista — mais pedidos nos finais de semana e horários de refeição.

!!! tip "Guia detalhado"
    Para regras de negócio, constantes do Faker e troubleshooting, veja o [guia completo do Faker](../quickstart/faker.md).

## Regerar os dados

Para limpar e repopular o banco do zero:

```bash
uv run python scripts/seed_database.py
```

O script já aplica o DDL e trunca as tabelas automaticamente.

!!! warning "Atenção"
    Regerar os dados invalida qualquer carga já feita nas camadas Bronze, Silver e Gold. Reexecute `sparkeats_pipeline_full` no Airflow após o seed.
