from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from ml.pretrained_sentiment import main as run_sentiment

# Default arguments
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 10, 8),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

# Define the DAG
dag = DAG(
    dag_id='yt_comments_pipeline',
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False,
    description='YouTube Comments ETL + Sentiment Analysis'
)

# Step 1: Trigger the ingestion Cloud Function (public HTTPS call)
def trigger_ingest_fn():
    url = "https://us-central1-ambient-elf-487017-d6.cloudfunctions.net/yt-ingestion-fn"
    try:
        response = requests.post(url, json={"trigger": "airflow"})
        response.raise_for_status()
        print(f"✅ Triggered ingestion function successfully: {response.status_code}")
        print(response.text)
    except Exception as e:
        print(f"❌ Failed to trigger ingestion function: {str(e)}")
        raise

trigger_ingest = PythonOperator(
    task_id='trigger_ingest',
    python_callable=trigger_ingest_fn,
    dag=dag
)

# Step 2: Run pretrained sentiment analysis
pretrained_sentiment = PythonOperator(
    task_id='pretrained_sentiment',
    python_callable=run_sentiment,
    dag=dag
)

# Step 3: Define dependencies
trigger_ingest >> pretrained_sentiment