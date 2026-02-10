variable "project_id" {}
variable "region" {}

data "google_project" "current" {
  project_id = var.project_id
}

resource "google_service_account" "cf_sa" {
  account_id   = "cloud-fn-sa"
  display_name = "Cloud Functions Service Account"
  project      = var.project_id
}

# Assign all required roles
resource "google_project_iam_member" "cf_sa_bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_bigquery_user" {
  project = var.project_id
  role    = "roles/bigquery.user"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_cloudfunctions_admin" {
  project = var.project_id
  role    = "roles/cloudfunctions.admin"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_cloudfunctions_invoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_composer_worker" {
  project = var.project_id
  role    = "roles/composer.worker"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_dataflow_developer" {
  project = var.project_id
  role    = "roles/dataflow.developer"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_dataflow_worker" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_pubsub_editor" {
  project = var.project_id
  role    = "roles/pubsub.editor"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_service_account_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_composer_admin" {
  project = var.project_id
  role    = "roles/composer.admin"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_container_admin" {
  project = var.project_id
  role    = "roles/container.admin"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_network_admin" {
  project = var.project_id
  role    = "roles/compute.networkAdmin"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "cf_sa_service_account_actor" {
  project = var.project_id
  role    = "roles/iam.serviceAccountActor"
  member  = "serviceAccount:${google_service_account.cf_sa.email}"
}

resource "google_project_iam_member" "composer_service_agent_ext" {
  project = var.project_id
  role    = "roles/composer.ServiceAgentV2Ext"
  member  = "serviceAccount:service-${data.google_project.current.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}

output "cf_sa_email" {
  value = google_service_account.cf_sa.email
}