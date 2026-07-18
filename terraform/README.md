# Terraform

This directory contains the infrastructure-as-code for ExperimentLake.

## Layout

```text
terraform/
  environments/
    dev/                deployable development environment
  modules/
    data_lake/          S3 buckets and bucket controls
    ingestion_api/      API Gateway, Lambda, and IAM
    glue_catalog/       Glue database and raw events table
    athena/             Athena workgroup
    monitoring/         placeholder for future alarms/dashboards
```

## Deploy

```bash
cd terraform/environments/dev
terraform init
terraform validate
terraform plan
terraform apply
```

## Outputs

Important outputs:

- `raw_bucket_name`
- `curated_bucket_name`
- `athena_results_bucket_name`
- `events_endpoint`
- `glue_database_name`
- `athena_workgroup_name`

## Destroy

```bash
cd terraform/environments/dev
terraform destroy
```

The learning project uses `force_destroy = true` for S3 buckets so teardown is easier. In production, that would usually be disabled.
