from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {"retries": 2, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="longevity_pipeline",
    start_date=datetime(2026, 10, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
) as dag:

    extract = BashOperator(
        task_id="extract",
        bash_command="cd /opt/airflow && python src/extract.py",
    )
    load_raw = BashOperator(
        task_id="load_raw",
        bash_command="cd /opt/airflow && python src/load_raw.py",
    )
    load_warehouse = BashOperator(
        task_id="load_warehouse",
        bash_command="cd /opt/airflow && python src/load_warehouse.py",
    )

    extract >> load_raw >> load_warehouse