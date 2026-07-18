import base64
import json
import os
import uuid
from datetime import datetime, timezone

import boto3

s3 = boto3.client("s3")

REQUIRED_FIELDS = {
    "event_id",
    "user_id",
    "session_id",
    "experiment_id",
    "variant",
    "event_name",
    "event_timestamp",
}


def response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body),
    }


def parse_body(event: dict) -> dict:
    body = event.get("body")

    if body is None:
        raise ValueError("Missing request body")

    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    return json.loads(body)


def validate_payload(payload: dict) -> None:
    missing_fields = REQUIRED_FIELDS - set(payload)

    if missing_fields:
        raise ValueError(f"Missing required fields: {sorted(missing_fields)}")


def event_date_from_timestamp(event_timestamp: str) -> str:
    return event_timestamp[:10]


def handler(event, context):
    raw_bucket = os.environ["RAW_BUCKET"]

    try:
        payload = parse_body(event)
        validate_payload(payload)
    except (json.JSONDecodeError, ValueError) as error:
        return response(400, {"message": "Invalid event payload", "error": str(error)})

    ingest_time = datetime.now(timezone.utc)
    experiment_id = payload["experiment_id"]
    event_date = event_date_from_timestamp(payload["event_timestamp"])
    event_id = payload.get("event_id", str(uuid.uuid4()))

    object_key = (
        f"events/"
        f"experiment_id={experiment_id}/"
        f"event_date={event_date}/"
        f"ingest_date={ingest_time.date().isoformat()}/"
        f"{event_id}.json"
    )

    payload["_ingested_at"] = ingest_time.isoformat()

    s3.put_object(
        Bucket=raw_bucket,
        Key=object_key,
        Body=json.dumps(payload) + "\n",
        ContentType="application/json",
    )

    return response(
        202,
        {
            "message": "Event accepted",
            "bucket": raw_bucket,
            "key": object_key,
        },
    )