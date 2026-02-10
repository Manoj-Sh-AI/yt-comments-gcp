variable "project_id" {}
variable "region" {}

resource "google_pubsub_topic" "yt_comments" {
  name    = "yt-comments-topic"
  project = var.project_id
}

output "yt_comments_name" {
  value = google_pubsub_topic.yt_comments.name
}