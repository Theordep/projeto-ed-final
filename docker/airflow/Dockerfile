FROM apache/airflow:3.2.2-python3.12

USER airflow

ARG AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW_HOME=${AIRFLOW_HOME}

RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres==5.4.0 \
    apache-airflow-providers-amazon==5.0.0 \
    apache-airflow-providers-docker==3.1.0 \
    pyspark==3.5.1 \
    delta-spark==3.2.0 \
    minio>=7.2

COPY . /opt/airflow/project
RUN pip install --no-cache-dir -e /opt/airflow/project
