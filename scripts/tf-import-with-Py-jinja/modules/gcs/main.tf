resource "google_storage_bucket" "gcs_bucket" {
  name          = var.name
  location      = var.location
  force_destroy = var.force_destroy
  versioning = {
    enabled = var.version
  }
  storage_class               = var.storage_class
  uniform_bucket_level_access = var.uniform_bucket_level_access
}
