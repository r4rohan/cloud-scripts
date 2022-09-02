output "bucket_name" {
  description = "Outputs the finally constructed bucket name. Will be necessary for external resources (eg: ServiceAccounts) to be granted permissions to read/write to."
  value       = google_storage_bucket.gcs_bucket.*
}
