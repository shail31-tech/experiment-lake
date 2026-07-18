# ExperimentLake

ExperimentLake is a serverless A/B testing analytics platform built with Terraform, AWS, Python, S3, Lambda, API Gateway, Glue, Athena, and Streamlit.

The project simulates product experimentation events, ingests them through an API, stores raw event logs in a data lake, transforms them into user-level experiment facts, and evaluates variants with statistical A/B testing.

## What This Project Demonstrates

- Infrastructure as code with Terraform modules
- Serverless event ingestion with API Gateway and Lambda
- Raw, processed, curated, and Athena results S3 zones
- Glue Data Catalog tables over partitioned S3 data
- Athena SQL over event-level and curated Parquet data
- Python statistical analysis for conversion lift and p-values
- Streamlit dashboard for top-line and segment-level experiment decisioning
- Cost-aware cloud architecture for a portfolio project

## Architecture

```text
Local Event Generator
  -> API Gateway POST /events
  -> Lambda validation
  -> S3 raw events
  -> Glue raw_events table
  -> Athena CTAS transform
  -> S3 curated Parquet table
  -> Python analysis and Streamlit dashboard
```

See [docs/architecture-diagram.md](docs/architecture-diagram.md) for the Mermaid architecture diagram.

## Experiment

The simulated product is a SaaS onboarding flow.

- Control: existing onboarding
- Treatment 1: simplified onboarding
- Treatment 2: guided checklist onboarding

Primary metric:

- Onboarding activation rate

Secondary metrics:

- Signup completion
- Subscription rate
- Revenue per user

## Current Result

With the generated sample dataset, both treatments improve activation versus control. The guided checklist variant is the strongest recommendation.

```text
control activation rate:          14.97%
guided_checklist activation rate: 20.84%
simplified activation rate:       18.33%

guided_checklist p-value: 0.000009
simplified p-value:       0.009056
sample ratio check:       pass
```

Decision:

```text
Ship guided_checklist as the primary onboarding experience.
```

## Repository Structure

```text
app/
  event_generator/      Local data generation and API sender
  lambda_ingest/        Lambda function for event ingestion
dashboard/             Streamlit dashboard
docs/                  Architecture, cost, experiment, and statistics notes
pipelines/
  transform_events/    Athena CTAS transform into curated facts
  analyze_experiment/  Python statistical analysis
sql/                   Athena SQL templates and smoke tests
terraform/             Terraform root module, environment, and child modules
```

## Prerequisites

- Python 3.10+
- Terraform 1.6+
- AWS CLI configured with credentials
- AWS account permissions for S3, Lambda, API Gateway, IAM, Glue, Athena, and CloudWatch Logs

Check identity:

```bash
aws sts get-caller-identity
```

## Local Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

Or:

```bash
make setup
```

## Run The Project

Generate local sample data:

```bash
make generate-sample
make validate-sample
```

Deploy infrastructure:

```bash
cd terraform/environments/dev
terraform init
terraform validate
terraform plan
terraform apply
```

Send a small batch through the ingestion API:

```bash
cd /Users/shailshah/Desktop/portfolio_projects/experiment-lake
EVENTS_ENDPOINT="$(cd terraform/environments/dev && terraform output -raw events_endpoint)"

python app/event_generator/send_events.py \
  --endpoint-url "$EVENTS_ENDPOINT" \
  --limit 25
```

Create the curated user facts table:

```bash
make create-user-facts
```

Run statistical analysis:

```bash
make analyze-ab-test
```

Start the dashboard:

```bash
make dashboard
```

The dashboard includes top-line variant metrics, control comparisons, activation-rate charts, sample ratio checks, and segment analysis by device type, traffic source, plan type, and country.

## Useful Verification Commands

List Terraform outputs:

```bash
cd terraform/environments/dev
terraform output
```

Check raw events in S3:

```bash
aws s3 ls s3://experimentlake-dev-626635448465-us-east-1-raw/events/ --recursive | tail
```

Check curated Parquet output:

```bash
aws s3 ls s3://experimentlake-dev-626635448465-us-east-1-curated/tables/user_experiment_facts/ --recursive
```

Run lint:

```bash
make lint
```

## Cost Notes

The project uses serverless, usage-based services. At portfolio scale, expected active development cost is usually low, mostly from S3 storage, Athena queries, and small API/Lambda usage.

Avoid leaving unnecessary data around if you are done testing. To remove cloud resources:

```bash
cd terraform/environments/dev
terraform destroy
```

## Notes

The sample data is synthetic by design. Real user-level A/B testing logs are rarely public because they include sensitive product and behavioral data. This project focuses on the realistic analytics platform pattern: exposure logging, event ingestion, raw-to-curated transformation, data quality cleanup, and experiment decisioning.
