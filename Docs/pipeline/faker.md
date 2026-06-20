# Geração de dados

O banco PostgreSQL é populado com dados sintéticos gerados pela biblioteca **Faker**, via `scripts/seed_database.py`.

## Executar o seed

```bash
uv run python scripts/seed_database.py
```

## O que é gerado

| Tabela | Volume | Distribuição |
|--------|--------|-------------|
| `restaurantes` | ~500 | — |
| `clientes` | ~5.000 | — |
| `entregadores` | ~300 | — |
| `pedidos` | ~10.000 | Últimos 3 anos |
| `itens_pedido` | ~25.000 | Proporcional aos pedidos |
| `pagamentos` | ~10.000 | 1 por pedido |
| `avaliacoes` | ~8.000 | ~80% dos pedidos |
| `cardapio` | ~2.000 | ~4 itens por restaurante |
| `categorias_restaurante` | ~20 | — |
| `zonas_entrega` | ~50 | — |

!!! info "Distribuição temporal"
    Os pedidos são distribuídos nos últimos 3 anos com sazonalidade realista — mais pedidos nos finais de semana e horários de refeição.

## Regerar os dados

Para limpar e repopular o banco do zero:

```bash
uv run psql -h localhost -p 5433 -U sparkeats -d sparkeats \
  -f sql/ddl_origem_postgresql.sql

uv run python scripts/seed_database.py
```

!!! warning "Atenção"
    Regerar os dados invalida qualquer carga já feita nas camadas Bronze, Silver e Gold. Reexecute todas as DAGs do Airflow após o seed.