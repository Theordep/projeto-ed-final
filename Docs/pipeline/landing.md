# Landing Zone

Primeira camada do Data Lake. Recebe os dados brutos extraídos diretamente do PostgreSQL, sem nenhuma transformação.

## Responsabilidade

- Extração completa das tabelas do PostgreSQL
- Gravação em **CSV** no bucket `landing-zone` do MinIO
- Preservação do formato original da origem

## DAG: `dag_landing`

A DAG extrai cada tabela do PostgreSQL e grava um arquivo CSV correspondente no MinIO.

```
landing-zone/
├── restaurantes.csv
├── clientes.csv
├── entregadores.csv
├── pedidos.csv
├── itens_pedido.csv
├── pagamentos.csv
├── avaliacoes.csv
├── cardapio.csv
├── categorias_restaurante.csv
└── zonas_entrega.csv
```

## Executar manualmente

Na Airflow UI (http://localhost:8082), ative e dispare a DAG `dag_landing`.

Ou via CLI:

```bash
docker exec -it <container-airflow> airflow dags trigger dag_landing
```

## Verificar no MinIO

Acesse o console em http://localhost:9091, bucket `landing-zone`, e confirme que os arquivos foram criados.

!!! note "Carga full"
    A landing sempre faz **carga completa** (full load) — sobrescreve os arquivos a cada execução. As camadas subsequentes são responsáveis pela incremental.