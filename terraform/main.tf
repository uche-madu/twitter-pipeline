terraform {
  required_provider {
    google = {
        source = "hashicorp/google"
        version = "4.41.0"
    }
  }
  backend "local" {
    path = "terraform/state/terraform.tfstate"
  }
}
provider "google" {
  credentials = file(var.credentials_file)

  project = var.project_id
  region = var.gcp_region_1
  zone = var.gcp_zone_1
}

module "custom_vpc_network" {
  source  = "terraform-google-modules/network/google//examples/simple_project"
  version = "5.2.0"
  # insert the 2 required variables here
  project_id   = var.project_id
  network_name = "twitter_pipeline_network"
}
