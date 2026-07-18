# Lambda Ingest

This Lambda receives A/B testing events from API Gateway, validates required fields, and writes each event to the raw S3 bucket.

## Required Fields

- `event_id`
- `user_id`
- `session_id`
- `experiment_id`
- `variant`
- `event_name`
- `event_timestamp`

## S3 Layout

Events are stored as individual JSON files:

```text
events/experiment_id=<experiment_id>/event_date=<event_date>/ingest_date=<ingest_date>/<event_id>.json
```

The partition-style path lets Glue and Athena query by experiment and event date.
