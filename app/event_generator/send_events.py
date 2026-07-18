import argparse
import csv
import json
import ssl
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi


def read_events(path: Path, limit: int | None) -> list[dict]:
    with path.open() as file:
        reader = csv.DictReader(file)
        events = list(reader)

    if limit is not None:
        return events[:limit]

    return events


def post_event(endpoint_url: str, event: dict) -> tuple[int, str]:
    request = Request(
        endpoint_url,
        data=json.dumps(event).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )

    context = ssl.create_default_context(cafile=certifi.where())

    with urlopen(request, timeout=10, context=context) as response:
        return response.status, response.read().decode("utf-8")


def send_events(
    endpoint_url: str,
    events_path: Path,
    limit: int | None,
    sleep_seconds: float,
) -> None:
    events = read_events(events_path, limit)

    accepted = 0
    failed = 0

    for index, event in enumerate(events, start=1):
        try:
            status_code, body = post_event(endpoint_url, event)
        except HTTPError as error:
            failed += 1
            print(f"[{index}] HTTP {error.code}: {error.read().decode('utf-8')}")
            continue
        except URLError as error:
            failed += 1
            print(f"[{index}] Request failed: {error}")
            continue

        if status_code == 202:
            accepted += 1
        else:
            failed += 1
            print(f"[{index}] Unexpected status {status_code}: {body}")

        if index % 100 == 0:
            print(f"Sent {index:,} events... accepted={accepted:,}, failed={failed:,}")

        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    print(f"Finished. accepted={accepted:,}, failed={failed:,}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send generated events to the ingestion API.")
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--events-path", type=Path, default=Path("data/sample/events.csv"))
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    send_events(
        endpoint_url=args.endpoint_url,
        events_path=args.events_path,
        limit=args.limit,
        sleep_seconds=args.sleep_seconds,
    )


if __name__ == "__main__":
    main()
