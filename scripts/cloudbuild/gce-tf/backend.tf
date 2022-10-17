terraform {
  backend "gcs" {
    bucket = "sasuke-tf"
    prefix = "main"
  }
}
