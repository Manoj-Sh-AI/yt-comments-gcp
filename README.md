# YouTube Comments Analysis Pipeline on GCP

This project implements an end-to-end ETL pipeline on Google Cloud Platform (GCP) to ingest YouTube comments, perform sentiment analysis, and load them into BigQuery for analytics. The pipeline is orchestrated using Apache Airflow.

## Architecture

The pipeline consists of the following components:

1.  **Cloud Function (`yt-ingestion-fn`)**: An HTTP-triggered function that fetches the latest comments from a specified YouTube channel.
2.  **Pub/Sub**: The Cloud Function publishes the fetched comments as messages to a Pub/Sub topic. This decouples the ingestion from the processing steps.
3.  **Cloud Function (`sentiment-analysis-fn`)**: A Pub/Sub-triggered function that consumes messages from the topic. It uses the **Google Cloud Natural Language API** to perform sentiment analysis on each comment.
4.  **BigQuery**: The sentiment function stores the original comment along with its sentiment score and label into a BigQuery table for warehousing and analysis.
5.  **Apache Airflow (Cloud Composer)**: An Airflow DAG orchestrates the entire pipeline, starting with triggering the ingestion function.
6.  **Sentiment Prediction UI**: A simple Flask-based UI, deployable as a Cloud Function, that allows users to test the sentiment analysis model in real-time.

## Features

- Automated, scheduled ingestion of YouTube comments.
- Scalable, event-driven architecture using Pub/Sub.
- Real-time sentiment analysis using Google's pretrained models.
- Centralized data warehousing in BigQuery for easy querying and visualization.
- Orchestration and monitoring with Apache Airflow.
- A utility script to generate fake data for testing and training purposes.

## Setup Instructions

### 1. Prerequisites

- A Google Cloud Project.
- Google Cloud SDK (`gcloud`) installed and authenticated.
- Python 3.8+ and `pip`.
- A YouTube Data API v3 key.
- An active Apache Airflow environment (e.g., Cloud Composer).

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd yt-comments-gcp
```

### 3. Enable GCP APIs

Enable the necessary APIs for your project:

```bash
gcloud services enable \
    cloudfunctions.googleapis.com \
    pubsub.googleapis.com \
    bigquery.googleapis.com \
    language.googleapis.com \
    cloudbuild.googleapis.com \
    composer.googleapis.com
```

### 4. Configure Infrastructure

#### a. BigQuery

Create the BigQuery dataset and table.

```bash
# Create the dataset
bq --location=US mk --dataset ambient-elf-487017-d6:youtube_comments

# Create the table
bq mk --table ambient-elf-487017-d6:youtube_comments.comments_train \
   comment_id:STRING,comment_text:STRING,published_at:TIMESTAMP,sentiment_label:STRING,ingested_at:TIMESTAMP
```

#### b. Pub/Sub

Create a Pub/Sub topic that will receive the raw comments.

```bash
gcloud pubsub topics create yt-comments-topic
```

### 5. Configure and Deploy Cloud Functions

The core logic resides in a Flask application in the `app/` directory.

#### a. Create `config.yaml`

Inside the `/home/shmanoj100/yt-comments-gcp/app` directory, create a `config.yaml` file with the following content.

```yaml
youtube_api_key: "YOUR_YOUTUBE_API_KEY"
pubsub_topic: "yt-comments-topic"
channel_id: "TARGET_YOUTUBE_CHANNEL_ID" # e.g., UC_x5XG1OV2P6uZZ5FSM9Ttw for Google
max_results: 20
```

Replace the placeholder values with your YouTube API key and the target channel ID.

#### b. Deploy the Ingestion Function

Deploy the HTTP-triggered function that starts the ingestion process.

```bash
gcloud functions deploy yt-ingestion-fn \
  --project=ambient-elf-487017-d6 \
  --region=us-central1 \
  --runtime=python39 \
  --source=app \
  --entry-point=main \
  --trigger-http \
  --allow-unauthenticated
```

### 6. Set up Airflow DAG

1.  **Upload the DAG**: Copy the `dags/yt_pipeline_dag.py` file to the `dags` folder in your Cloud Composer environment's GCS bucket.
2.  **Enable the DAG**: Open the Airflow UI for your Composer environment and enable the `yt_comments_pipeline` DAG.

The DAG is scheduled to run hourly, but you can also trigger it manually from the UI to test the pipeline.

### 7. (Optional) Generate Fake Data

A script is provided to populate the BigQuery table with fake data for development or testing.

```bash
# Install dependencies
pip install google-cloud-bigquery faker

# Run the script
python faker_comments_train.py
```