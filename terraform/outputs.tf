output "name_prefix" {
  description = "Common name prefix for resources."
  value       = local.name_prefix
}

output "raw_bucket_name" {
  description = "S3 bucket for raw event data."
  value       = module.data_lake.raw_bucket_name
}

output "processed_bucket_name" {
  description = "S3 bucket for processed data."
  value       = module.data_lake.processed_bucket_name
}

output "curated_bucket_name" {
  description = "S3 bucket for curated analytics-ready data."
  value       = module.data_lake.curated_bucket_name
}

output "athena_results_bucket_name" {
  description = "S3 bucket for Athena query results."
  value       = module.data_lake.athena_results_bucket_name
}

output "ingestion_api_endpoint" {
  description = "Base URL for the event ingestion API."
  value       = module.ingestion_api.api_endpoint
}

output "events_endpoint" {
  description = "Full URL for posting experiment events."
  value       = module.ingestion_api.events_endpoint
}

output "ingestion_lambda_function_name" {
  description = "Name of the ingestion Lambda function."
  value       = module.ingestion_api.lambda_function_name
}

output "glue_database_name" {
  description = "Glue database name."
  value       = module.glue_catalog.database_name
}

output "raw_events_table_name" {
  description = "Raw events Glue table name."
  value       = module.glue_catalog.raw_events_table_name
}

output "athena_workgroup_name" {
  description = "Athena workgroup name."
  value       = module.athena.workgroup_name
}