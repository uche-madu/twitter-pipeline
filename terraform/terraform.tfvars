# GCP Settings
#project_id    = "twitter-pipeline-366415" 
#gcp_region_1  = "europe-west4"
#gcp_zone_1    = "europe-west4-a"
gcp_service_list = [
    "storage.googleapis.com",
]

account_id  = "bucket-admin"
description = "Bucket Admin"
roles = [
  "roles/storage.admin",
  "roles/pubsub.admin",
  "roles/dataflow.admin",
  "roles/compute.serviceAgent",
  "roles/bigquery.admin",
]
