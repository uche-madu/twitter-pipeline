terraform {
  required_provider {
    google = {
        source = "hashicorp/google"
        version = "4.41.0"
    }
  }
}
provider "google" {
  project = var.project_id
  region = var.gcp_region_1
  zone = var.gcp_zone_1
}
resource "google_compute_network" "name" {
  
}