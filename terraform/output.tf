output "project_number" {
  value = data.google_project.project.number
}

output "project_id" {
  value = data.google_project.project.id
}

output "private_key" {
  value     = google_service_account_key.sa_key.private_key
  sensitive = true
}

output "decoded_private_key" {
  value     = base64decode(google_service_account_key.sa_key.private_key)
  sensitive = true
}

output "sa_email" {
  value       = google_service_account.sa.email
  description = "The e-mail address of the service account."
}
output "sa_name" {
  value       = google_service_account.sa.name
  description = "The fully-qualified name of the service account."
}

output "sa_unique_id" {
  value       = google_service_account.sa.unique_id
  description = "The unique id of the service account."
}

