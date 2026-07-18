module "root" {
  source = "../.."

  aws_region   = var.aws_region
  project_name = var.project_name
  environment  = var.environment
}
