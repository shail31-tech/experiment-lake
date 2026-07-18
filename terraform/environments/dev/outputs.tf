output "name_prefix" {
  description = "Common resource name prefix."
  value       = module.root.name_prefix
}

output "raw_bucket_name" {
  description = "S3 bucket for raw event data."
  value       = module.root.raw_bucket_name
}

output "processed_bucket_name" {
  description = "S3 bucket for processed data."
  value       = module.root.processed_bucket_name
}

output "curated_bucket_name" {
  description = "S3 bucket for curated analytics-ready data."
  value       = module.root.curated_bucket_name
}

output "athena_results_bucket_name" {
  description = "S3 bucket for Athena query results."
  value       = module.root.athena_results_bucket_name
}

output "ingestion_api_endpoint" {
  description = "Base URL for the event ingestion API."
  value       = module.root.ingestion_api_endpoint
}

output "events_endpoint" {
  description = "Full URL for posting experiment events."
  value       = module.root.events_endpoint
}

output "ingestion_lambda_function_name" {
  description = "Name of the ingestion Lambda function."
  value       = module.root.ingestion_lambda_function_name
}

output "glue_database_name" {
  description = "Glue database name."
  value       = module.root.glue_database_name
}

output "raw_events_table_name" {
  description = "Raw events Glue table name."
  value       = module.root.raw_events_table_name
}

output "athena_workgroup_name" {
  description = "Athena workgroup name."
  value       = module.root.athena_workgroup_name
}