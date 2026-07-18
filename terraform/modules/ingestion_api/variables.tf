variable "name_prefix" {
  description = "Prefix used for resource names."
  type        = string
}

variable "raw_bucket_name" {
  description = "Name of the raw S3 bucket."
  type        = string
}

variable "raw_bucket_arn" {
  description = "ARN of the raw S3 bucket."
  type        = string
}

variable "lambda_source_dir" {
  description = "Local path to the Lambda source directory."
  type        = string
}