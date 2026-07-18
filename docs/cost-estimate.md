# Cost Estimate

ExperimentLake is designed to stay inexpensive by using serverless and usage-based AWS services.

## Expected Portfolio Cost

For small sample data and occasional testing:

```text
S3 storage:        less than $1/month for small datasets
Lambda:           usually near $0 for small test batches
API Gateway:      usage-based, usually low for test batches
Glue Catalog:     low metadata cost at this scale
Athena:           charged by data scanned
CloudWatch Logs:  low unless large logs are generated
```

Expected active development range:

```text
$4-$28/month
```

Expected idle range:

```text
$0-$5/month
```

## Cost Controls

- Keep generated datasets small during development.
- Use Parquet for curated tables to reduce Athena scan cost.
- Avoid NAT Gateway, Redshift, EC2, and always-on compute.
- Use `terraform destroy` when you are done testing.
- Remove temporary Athena or curated output prefixes if rerunning CTAS often.

## Cleanup

Destroy Terraform-managed resources:

```bash
cd terraform/environments/dev
terraform destroy
```

If needed, remove generated local files:

```bash
rm -f data/sample/events.csv
rm -f data/sample/events.jsonl
rm -f data/sample/experiment_assignments.csv
rm -f data/sample/users.csv
```
