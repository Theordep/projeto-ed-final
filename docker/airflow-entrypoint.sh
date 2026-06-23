#!/usr/bin/env bash
# Entrypoint do airflow-init: migra o schema e cria o usuário admin.
# O banco 'airflow' já é criado pelo serviço postgres-airflow-setup.
set -e

echo "[airflow-init] Migrando schema do Airflow..."
airflow db migrate

echo "[airflow-init] Criando usuário admin..."
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname SparkEats \
    --role Admin \
    --email admin@sparkeats.local \
    2>/dev/null && echo "[airflow-init] Usuário admin criado." \
    || echo "[airflow-init] Usuário admin já existe."

echo "[airflow-init] Concluído."
