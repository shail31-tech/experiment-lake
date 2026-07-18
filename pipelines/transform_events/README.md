# Transform Events

This pipeline creates the curated `user_experiment_facts` table from raw Athena events.

## What It Does

- Drops any existing `user_experiment_facts` table
- Cleans the curated S3 output prefix
- Runs an Athena CTAS query
- Writes Parquet data to the curated bucket

## Run

From the project root:

```bash
make create-user-facts
```

The output location is:

```text
s3://<curated-bucket>/tables/user_experiment_facts/
```

## Why This Exists

Raw event data is too granular for A/B testing. The curated table creates one row per user per experiment with activation, subscription, revenue, and segmentation fields.
