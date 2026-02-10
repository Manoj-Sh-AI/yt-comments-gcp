variable "project_id" {}
variable "region" {}

# YT raw comments bucket
resource "google_storage_bucket" "yt_raw_bucket" {
  name     = "yt-raw-comments-${var.project_id}"
  location = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}

# Cloud Function source bucket
resource "google_storage_bucket" "cf_bucket" {
  name     = "yt-cf-source-${var.project_id}"
  project  = var.project_id
  location = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}

output "cloudfunction_bucket_name" {
  value = google_storage_bucket.cf_bucket.name
}