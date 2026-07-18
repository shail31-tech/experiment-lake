output "raw_bucket_name" {
  description = "S3 bucket for raw event data."
  value       = aws_s3_bucket.this["raw"].bucket
}

output "raw_bucket_arn" {
  description = "ARN of the raw event data bucket."
  value       = aws_s3_bucket.this["raw"].arn
}

output "processed_bucket_name" {
  description = "S3 bucket for processed data."
  value       = aws_s3_bucket.this["processed"].bucket
}

output "curated_bucket_name" {
  description = "S3 bucket for curated analytics-ready data."
  value       = aws_s3_bucket.this["curated"].bucket
}

output "athena_results_bucket_name" {
  description = "S3 bucket for Athena query results."
  value       = aws_s3_bucket.this["athena_results"].bucket
}