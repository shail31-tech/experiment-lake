# SQL

This directory contains Athena SQL for ExperimentLake.

## Files

- `raw_events_smoke_test.sql`: checks that Athena can read raw Glue table data.
- `create_user_experiment_facts.sql`: creates the curated Parquet table using CTAS.
- `user_experiment_facts.sql`: standalone user-level fact query for inspection.
- `experiment_summary.sql`: variant-level summary template.
- `segment_analysis.sql`: segment-level summary template.

## Notes

`create_user_experiment_facts.sql` includes a `${CURATED_LOCATION}` placeholder. The Python transform pipeline replaces that value with the Terraform-managed curated S3 bucket path before submitting the query to Athena.
