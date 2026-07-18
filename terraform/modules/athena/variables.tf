variable "name_prefix" {
  description = "Prefix used for resource names."
  type        = string
}

variable "athena_results_bucket_name" {
  description = "S3 bucket for Athena query results."
  type        = string
}