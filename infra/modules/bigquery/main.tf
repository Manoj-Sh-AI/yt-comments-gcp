variable "project_id" {}
variable "region" {}

# BigQuery Dataset
resource "google_bigquery_dataset" "yt_dataset" {
  dataset_id = "youtube_comments"
  project    = var.project_id
  location   = var.region
}

# BigQuery Table
resource "google_bigquery_table" "yt_comments_table" {
  dataset_id = google_bigquery_dataset.yt_dataset.dataset_id
  table_id   = "comments"
  project    = var.project_id

  schema = <<EOF
[
  {"name": "comment_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "comment_text", "type": "STRING", "mode": "REQUIRED"},
  {"name": "published_at", "type": "TIMESTAMP", "mode": "REQUIRED"}
]
EOF
}

# BigQuery Table for Sentiment Analysis
resource "google_bigquery_table" "yt_sentiment_table" {
  dataset_id = google_bigquery_dataset.yt_dataset.dataset_id
  table_id   = "sentiment"
  project    = var.project_id

  schema = <<EOF
[
  {"name": "comment_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "comment_text", "type": "STRING", "mode": "REQUIRED"},
  {"name": "sentiment_score", "type": "FLOAT", "mode": "NULLABLE"},
  {"name": "sentiment_magnitude", "type": "FLOAT", "mode": "NULLABLE"}
]
EOF
}