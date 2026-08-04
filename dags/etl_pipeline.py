from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


def _call(module_path, func_name="main"):
    import importlib

    mod = importlib.import_module(module_path)
    getattr(mod, func_name)()


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="etl_pipeline",
    default_args=default_args,
    description="ETL Pipeline — MIMII Pump Industrial Sound Classification",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["projeto-final", "etl", "mimii"],
) as dag:

    t1 = PythonOperator(
        task_id="download_dataset",
        python_callable=lambda: _call("ingestion.download_dataset"),
    )

    t2 = PythonOperator(
        task_id="load_to_s3",
        python_callable=lambda: _call("ingestion.load_raw_to_s3"),
    )

    t3 = PythonOperator(
        task_id="process_structured",
        python_callable=lambda: _call("processing.process_structured"),
    )

    t4 = PythonOperator(
        task_id="extract_audio_features",
        python_callable=lambda: _call("processing.extract_audio_features"),
    )

    t5 = PythonOperator(
        task_id="merge_features",
        python_callable=lambda: _call("processing.merge_features"),
    )

    t5b = PythonOperator(
        task_id="load_to_postgres",
        python_callable=lambda: _call("processing.load_to_postgres"),
    )

    t6 = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/project/dbt_project && dbt run --profiles-dir .",
    )

    t7 = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/project/dbt_project && dbt test --profiles-dir .",
    )

    t8 = PythonOperator(
        task_id="ml_train_evaluate",
        python_callable=lambda: _call("ml.evaluate"),
    )

    t1 >> t2 >> t3 >> t4 >> t5 >> t5b >> t6 >> t7 >> t8
