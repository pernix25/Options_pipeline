import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
# from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from pipeline import ETLPipeline

def run_pipeline():
    pipeline = ETLPipeline()
    pipeline.run()

with DAG(
    dag_id="options_pipeline"
    , schedule="0 21 * * 1-5" # Min, Hr, Day, Month, Day of week (0=Sun)
    , start_date=datetime(2026, 9, 1)
    , catchup=False
) as dag:
    
    start_pipeline = PythonOperator(
        task_id = "run_pipeline"
        , python_callable = run_pipeline
    )
