resource "google_service_account" "loki" {
  project      = "rohan-orbit"
  account_id   = "god-loki"
  display_name = "Loki Service Account"
}

resource "google_compute_instance" "loki" {
  project      = "rohan-orbit"
  name         = "loki"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  tags = ["temp"]

  boot_disk {
    initialize_params {
      size  = 30
      type  = "pd-standard"
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    subnetwork = "projects/rohan-orbit/regions/us-central1/subnetworks/thanos-in-usa"
  }

  service_account {
    email  = google_service_account.loki.email
    scopes = ["cloud-platform"]
  }
}
