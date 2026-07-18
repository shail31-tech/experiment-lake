import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED_EVENT_COLUMNS = {
    "event_id",
    "user_id",
    "session_id",
    "experiment_id",
    "variant",
    "event_name",
    "event_timestamp",
    "device_type",
    "country",
    "traffic_source",
    "plan_type",
    "revenue",
    "is_duplicate",
    "is_late_arriving",
}


def read_csv(path: Path) -> list[dict]:
    with path.open() as file:
        return list(csv.DictReader(file))


def validate_required_columns(events: list[dict]) -> list[str]:
    if not events:
        return ["events.csv has no rows"]

    actual_columns = set(events[0].keys())
    missing_columns = REQUIRED_EVENT_COLUMNS - actual_columns

    if missing_columns:
        return [f"events.csv is missing columns: {sorted(missing_columns)}"]

    return []


def validate_variant_stickiness(events: list[dict]) -> list[str]:
    variants_by_user = defaultdict(set)

    for event in events:
        variants_by_user[event["user_id"]].add(event["variant"])

    users_with_multiple_variants = {
        user_id: variants
        for user_id, variants in variants_by_user.items()
        if len(variants) > 1
    }

    if users_with_multiple_variants:
        return [
            "Some users were assigned multiple variants: "
            f"{list(users_with_multiple_variants.items())[:5]}"
        ]

    return []


def summarize_events(events: list[dict]) -> None:
    event_counts = Counter(event["event_name"] for event in events)
    variant_counts = Counter(
        event["variant"] for event in events if event["event_name"] == "experiment_exposed"
    )
    duplicate_count = sum(event["is_duplicate"] == "True" for event in events)
    late_count = sum(event["is_late_arriving"] == "True" for event in events)

    print("Event counts:")
    for event_name, count in event_counts.most_common():
        print(f"  {event_name}: {count:,}")

    print("\nExposure counts by variant:")
    for variant, count in sorted(variant_counts.items()):
        print(f"  {variant}: {count:,}")

    print(f"\nDuplicate event rows: {duplicate_count:,}")
    print(f"Late-arriving event rows: {late_count:,}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated A/B testing events.")
    parser.add_argument("--events-path", type=Path, default=Path("data/sample/events.csv"))

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    events = read_csv(args.events_path)

    errors = []
    errors.extend(validate_required_columns(events))
    errors.extend(validate_variant_stickiness(events))

    summarize_events(events)

    if errors:
        print("\nValidation failed:")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("\nValidation passed.")


if __name__ == "__main__":
    main()