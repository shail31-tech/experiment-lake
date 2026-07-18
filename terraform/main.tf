data "aws_caller_identity" "current" {}

module "data_lake" {
  source = "./modules/data_lake"

  name_prefix = local.name_prefix
  account_id  = data.aws_caller_identity.current.account_id
  aws_region  = var.aws_region
}

module "ingestion_api" {
  source = "./modules/ingestion_api"

  name_prefix       = local.name_prefix
  raw_bucket_name   = module.data_lake.raw_bucket_name
  raw_bucket_arn    = module.data_lake.raw_bucket_arn
  lambda_source_dir = abspath("${path.module}/../app/lambda_ingest")
}

module "glue_catalog" {
  source = "./modules/glue_catalog"

  name_prefix     = local.name_prefix
  raw_bucket_name = module.data_lake.raw_bucket_name
}

module "athena" {
  source = "./modules/athena"

  name_prefix                = local.name_prefix
  athena_results_bucket_name = module.data_lake.athena_results_bucket_name
}