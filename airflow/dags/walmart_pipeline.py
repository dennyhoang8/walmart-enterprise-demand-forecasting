from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "denny",
    "retries": 1,
}


with DAG(
    dag_id="walmart_data_pipeline",
    default_args=default_args,
    description="Walmart retail ETL pipeline",
    start_date=datetime(2026, 8, 1),
    schedule="@daily",
    catchup=False,
    tags=["walmart", "etl"],
) as dag:

    extract_weather = BashOperator(
        task_id="extract_weather",
        bash_command=(
            "python -m etl.extract.extract_weather"
        ),
    )

    extract_fred = BashOperator(
        task_id="extract_fred",
        bash_command=(
            "python -m etl.extract.extract_fred"
        ),
    )

    extract_holidays = BashOperator(
        task_id="extract_holidays",
        bash_command=(
            "python -m etl.extract.extract_holidays"
        ),
    )

    validate_weather = BashOperator(
        task_id="validate_weather",
        bash_command=(
            "python -m etl.quality.validate_weather"
        ),
    )

    validate_economic = BashOperator(
        task_id="validate_economic",
        bash_command=(
            "python -m etl.quality.validate_economic"
        ),
    )

    extract_weather >> validate_weather
    extract_fred >> validate_economic
    extract_holidays