# GCP Project ID 
variable "project_id" {
  type = string
  description = "GCP Project ID"
}

# Region to use for Subnet
variable "gcp_region_1" {
  type = string
  description = "GCP Region"
}

# Zone used for VMs
variable "gcp_zone_1" {
  type = string
  description = "GCP Zone"
}

variable "credentials_file" {}