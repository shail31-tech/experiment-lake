# Architecture Diagram

```mermaid
flowchart LR
    generator["Local event generator"] --> sender["send_events.py"]
    sender --> api["API Gateway POST /events"]
    api --> lambda["Lambda event ingest"]
    lambda --> raw["S3 raw events"]
    raw --> glue["Glue raw_events table"]
    glue --> athena["Athena SQL"]
    athena --> curated["S3 curated Parquet"]
    curated --> facts["user_experiment_facts"]
    facts --> analysis["Python A/B analysis"]
    facts --> dashboard["Streamlit dashboard"]

    terraform["Terraform"] -. provisions .-> api
    terraform -. provisions .-> lambda
    terraform -. provisions .-> raw
    terraform -. provisions .-> glue
    terraform -. provisions .-> athena
    terraform -. provisions .-> curated
```

## Responsibilities

- Terraform provisions cloud infrastructure and IAM.
- API Gateway and Lambda create the event ingestion surface.
- S3 stores raw and curated data lake files.
- Glue describes S3 data to Athena.
- Athena transforms raw JSON events into curated Parquet facts.
- Python and Streamlit turn curated facts into experiment decisions.
