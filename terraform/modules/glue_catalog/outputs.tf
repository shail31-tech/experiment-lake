output "database_name" {
  description = "Glue database name."
  value       = aws_glue_catalog_database.this.name
}

output "raw_events_table_name" {
  description = "Raw events Glue table name."
  value       = aws_glue_catalog_table.raw_events.name
}