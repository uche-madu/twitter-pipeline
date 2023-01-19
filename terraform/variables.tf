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

variable "gcp_service_list" {
  type        = list(string)
  description = "The list of apis necessary for the project"
  default     = []
}

variable "account_id" {
  description = "The service account ID. Changing this forces a new service account to be created."
}

variable "description" {
  description = "The display name for the service account. Can be updated without creating a new resource."
  default     = "managed-by-terraform"
}

variable "roles" {
  type        = list(string)
  description = "The roles that will be granted to the service account."
  default     = []
}
