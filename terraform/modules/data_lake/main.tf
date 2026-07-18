locals {
  bucket_prefix = lower("${var.name_prefix}-${var.account_id}-${var.aws_region}")

  buckets = {
    raw = {
      name        = "${local.bucket_prefix}-raw"
      description = "Raw event data"
    }

    processed = {
      name        = "${local.bucket_prefix}-processed"
      description = "Processed data"
    }

    curated = {
      name        = "${local.bucket_prefix}-curated"
      description = "Curated analytics-ready data"
    }

    athena_results = {
      name        = "${local.bucket_prefix}-athena-results"
      description = "Athena query results"
    }
  }
}

resource "aws_s3_bucket" "this" {
  for_each = local.buckets

  bucket        = each.value.name
  force_destroy = true

  tags = {
    Name        = each.value.name
    DataLayer   = each.key
    Description = each.value.description
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  for_each = aws_s3_bucket.this

  bucket = each.value.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  for_each = aws_s3_bucket.this

  bucket = each.value.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "this" {
  for_each = aws_s3_bucket.this

  bucket = each.value.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "this" {
  for_each = aws_s3_bucket.this

  bucket = each.value.id

  rule {
    id     = "cleanup-incomplete-multipart-uploads"
    status = "Enabled"

    filter {}

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  rule {
    id     = "expire-old-noncurrent-versions"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}