variable "project_id" {}
variable "name" {}
variable "cf_sa_email" {}
variable "region" {}

resource "google_composer_environment" "yt_pipeline" {
  name    = var.name
  project = var.project_id
  region  = "us-central1"

  config {
    # Use Composer 3 + Airflow 2.10.5 (build 15)
    software_config {
      image_version = "composer-3-airflow-2.10.5-build.15"
    }

    environment_size = "ENVIRONMENT_SIZE_SMALL"  # small resources
    resilience_mode  = "STANDARD_RESILIENCE" # standard resilience

    node_config {
      service_account = var.cf_sa_email
      # network/subnetwork default to auto-managed unless you specify custom ones
    }
  }
}