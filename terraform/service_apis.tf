locals {
  all_project_services = concat(var.gcp_service_list, [
    "serviceusage.googleapis.com",
    "iam.googleapis.com",
    "pubsub.googleapis.com",
    "bigquery.googleapis.com",
    "bigquerystorage.googleapis.com",
    "iamcredentials.googleapis.com",
    "storage-api.googleapis.com",
    "storage-component.googleapis.com",
    "storage.googleapis.com",
    
  ])
}

resource "google_project_service" "enabled_apis" {
  project  = var.project_id
  for_each = toset(locals.all_project_services)
  service  = each.key

  disable_on_destroy = false
}
