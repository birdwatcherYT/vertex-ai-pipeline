provider "google" {
  project = var.project_id
  region  = var.region
}

# GCSのバケット作成
resource "google_storage_bucket" "vertex_pipelines_bucket" {
  name     = var.bucket_name
  location = var.region
  project  = var.project_id
}

# artifact registoryにレポジトリを作成
resource "google_artifact_registry_repository" "pipeline_docker" {
  project     = var.project_id
  location    = var.region
  repository_id = "my-pipeline"
  format        = "docker"
}

# パイプラインのサービスアカウント作成
resource "google_service_account" "vertex_pipelines_sa" {
  account_id   = "vertex-pipelines-sa"
  display_name = "Vertex Pipelines Service Account"
  project      = var.project_id
}

# IAM権限設定
resource "google_project_iam_member" "pipeline_vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  =   "serviceAccount:${google_service_account.vertex_pipelines_sa.email}"
}

resource "google_project_iam_member" "pipeline_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  =   "serviceAccount:${google_service_account.vertex_pipelines_sa.email}"
}

resource "google_project_iam_member" "pipeline_service_account_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  =   "serviceAccount:${google_service_account.vertex_pipelines_sa.email}"
}

resource "google_artifact_registry_repository_iam_member" "pipeline_artifact_registry_user" {
  project      = var.project_id
  location    = var.region
  repository   = google_artifact_registry_repository.pipeline_docker.repository_id
  role         = "roles/artifactregistry.reader"
  member       = "serviceAccount:${google_service_account.vertex_pipelines_sa.email}"
}

resource "google_artifact_registry_repository_iam_member" "pipeline_artifact_registry_writer" {
  project      = var.project_id
  location    = var.region
  repository   = google_artifact_registry_repository.pipeline_docker.repository_id
  role         = "roles/artifactregistry.writer"
  member       = "serviceAccount:${google_service_account.vertex_pipelines_sa.email}"
}


## Cloud Build で利用するサービスアカウント(必要があれば)
resource "google_service_account" "cloud_build_sa" {
  account_id   = "cloud-build-sa"
  display_name = "Cloud Build Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "cloud_build_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.cloud_build_sa.email}"
}

resource "google_artifact_registry_repository_iam_member" "cloud_build_artifact_registry_writer" {
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.pipeline_docker.repository_id
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.cloud_build_sa.email}"
}

resource "google_project_iam_member" "cloud_build_sa_cloudbuild" {
  project    = var.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${google_service_account.cloud_build_sa.email}"
}
