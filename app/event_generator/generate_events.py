import argparse
import csv
import json
import random
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

EXPERIMENT_ID = "onboarding_v2"
VARIANTS = ["control", "simplified", "guided_checklist"]

DEVICE_TYPES = ["desktop", "mobile", "tablet"]
COUNTRIES = ["US", "CA", "GB", "IN", "DE", "BR"]
TRAFFIC_SOURCES = ["organic", "paid_search", "social", "email", "referral"]
PLAN_TYPES = ["free", "pro", "team"]


@dataclass
class User:
    user_id: str
    created_at: str
    device_type: str
    country: str
    traffic_source: str
    plan_type: str
    is_returning_user: bool


@dataclass
class Assignment:
    user_id: str
    experiment_id: str
    variant: str
    assigned_at: str


@dataclass
class Event:
    event_id: str
    user_id: str
    session_id: str
    experiment_id: str
    variant: str
    event_name: str
    event_timestamp: str
    device_type: str
    country: str
    traffic_source: str
    plan_type: str
    revenue: float
    is_duplicate: bool
    is_late_arriving: bool


def isoformat(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def weighted_choice(options: list[str], weights: list[float]) -> str:
    return random.choices(options, weights=weights, k=1)[0]


def assign_variant(user_id: str) -> str:
    """
    Sticky assignment: the same user_id always maps to the same variant.
    This imitates how real experimentation systems avoid switching users
    between control and treatment.
    """
    bucket = hash(user_id) % 100

    if bucket < 34:
        return "control"
    if bucket < 67:
        return "simplified"
    return "guided_checklist"


def conversion_probability(user: User, variant: str) -> float:
    """
    Simulates the true activation probability.

    The guided checklist performs best on desktop, but not much better on mobile.
    This creates a realistic segment-level result instead of a boring winner.
    """
    base_rate = 0.18

    if user.device_type == "desktop":
        base_rate += 0.05
    elif user.device_type == "mobile":
        base_rate -= 0.03

    if user.traffic_source == "email":
        base_rate += 0.04
    elif user.traffic_source == "paid_search":
        base_rate -= 0.02

    if user.is_returning_user:
        base_rate += 0.03

    if variant == "simplified":
        base_rate += 0.025
    elif variant == "guided_checklist":
        if user.device_type == "desktop":
            base_rate += 0.07
        elif user.device_type == "mobile":
            base_rate += 0.005
        else:
            base_rate += 0.03

    return min(max(base_rate, 0.02), 0.65)


def revenue_amount(user: User, activated: bool) -> float:
    if not activated:
        return 0.0

    plan_base = {
        "free": 0,
        "pro": 29,
        "team": 99,
    }[user.plan_type]

    if plan_base == 0:
        return 0.0

    # Revenue is intentionally noisy and right-skewed.
    multiplier = random.lognormvariate(mu=0.0, sigma=0.35)
    return round(plan_base * multiplier, 2)


def create_event(
    user: User,
    assignment: Assignment,
    session_id: str,
    event_name: str,
    timestamp: datetime,
    revenue: float = 0.0,
    is_duplicate: bool = False,
    is_late_arriving: bool = False,
) -> Event:
    return Event(
        event_id=str(uuid.uuid4()),
        user_id=user.user_id,
        session_id=session_id,
        experiment_id=assignment.experiment_id,
        variant=assignment.variant,
        event_name=event_name,
        event_timestamp=isoformat(timestamp),
        device_type=user.device_type,
        country=user.country,
        traffic_source=user.traffic_source,
        plan_type=user.plan_type,
        revenue=revenue,
        is_duplicate=is_duplicate,
        is_late_arriving=is_late_arriving,
    )


def generate_user(index: int, start_time: datetime) -> User:
    created_at = start_time + timedelta(minutes=random.randint(0, 60 * 24 * 14))

    return User(
        user_id=f"user_{index:06d}",
        created_at=isoformat(created_at),
        device_type=weighted_choice(DEVICE_TYPES, [0.55, 0.38, 0.07]),
        country=weighted_choice(COUNTRIES, [0.55, 0.08, 0.10, 0.12, 0.08, 0.07]),
        traffic_source=weighted_choice(TRAFFIC_SOURCES, [0.38, 0.22, 0.16, 0.14, 0.10]),
        plan_type=weighted_choice(PLAN_TYPES, [0.68, 0.24, 0.08]),
        is_returning_user=random.random() < 0.35,
    )


def generate_events_for_user(user: User, assignment: Assignment) -> list[Event]:
    events = []
    session_id = str(uuid.uuid4())
    assigned_time = datetime.fromisoformat(assignment.assigned_at)

    exposure_time = assigned_time + timedelta(seconds=random.randint(1, 120))

    events.append(
        create_event(
            user=user,
            assignment=assignment,
            session_id=session_id,
            event_name="experiment_exposed",
            timestamp=exposure_time,
        )
    )

    events.append(
        create_event(
            user=user,
            assignment=assignment,
            session_id=session_id,
            event_name="signup_started",
            timestamp=exposure_time + timedelta(seconds=random.randint(10, 90)),
        )
    )

    signup_completed = random.random() < 0.82
    if not signup_completed:
        return events

    events.append(
        create_event(
            user=user,
            assignment=assignment,
            session_id=session_id,
            event_name="signup_completed",
            timestamp=exposure_time + timedelta(minutes=random.randint(1, 5)),
        )
    )

    events.append(
        create_event(
            user=user,
            assignment=assignment,
            session_id=session_id,
            event_name="onboarding_started",
            timestamp=exposure_time + timedelta(minutes=random.randint(3, 8)),
        )
    )

    activated = random.random() < conversion_probability(user, assignment.variant)
    if not activated:
        if random.random() < 0.45:
            events.append(
                create_event(
                    user=user,
                    assignment=assignment,
                    session_id=session_id,
                    event_name="feature_viewed",
                    timestamp=exposure_time + timedelta(minutes=random.randint(8, 25)),
                )
            )
        return events

    events.append(
        create_event(
            user=user,
            assignment=assignment,
            session_id=session_id,
            event_name="onboarding_completed",
            timestamp=exposure_time + timedelta(minutes=random.randint(8, 30)),
        )
    )

    events.append(
        create_event(
            user=user,
            assignment=assignment,
            session_id=session_id,
            event_name="feature_used",
            timestamp=exposure_time + timedelta(minutes=random.randint(12, 45)),
        )
    )

    revenue = revenue_amount(user, activated=True)
    if revenue > 0:
        events.append(
            create_event(
                user=user,
                assignment=assignment,
                session_id=session_id,
                event_name="subscription_started",
                timestamp=exposure_time + timedelta(minutes=random.randint(20, 90)),
                revenue=revenue,
            )
        )

    return events


def inject_messy_events(events: list[Event]) -> list[Event]:
    messy_events = list(events)

    duplicate_candidates = random.sample(events, k=max(1, int(len(events) * 0.01)))
    for event in duplicate_candidates:
        duplicate = Event(**asdict(event))
        duplicate.event_id = str(uuid.uuid4())
        duplicate.is_duplicate = True
        messy_events.append(duplicate)

    late_candidates = random.sample(events, k=max(1, int(len(events) * 0.01)))
    for event in late_candidates:
        late_event = Event(**asdict(event))
        original_time = datetime.fromisoformat(late_event.event_timestamp)
        late_event.event_id = str(uuid.uuid4())
        late_event.event_timestamp = isoformat(original_time - timedelta(days=random.randint(1, 3)))
        late_event.is_late_arriving = True
        messy_events.append(late_event)

    random.shuffle(messy_events)
    return messy_events


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as file:
        for row in rows:
            file.write(json.dumps(row) + "\n")


def generate_dataset(num_users: int, output_dir: Path, seed: int) -> None:
    random.seed(seed)

    start_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    users: list[User] = []
    assignments: list[Assignment] = []
    events: list[Event] = []

    for index in range(1, num_users + 1):
        user = generate_user(index, start_time)
        variant = assign_variant(user.user_id)

        assignment_time = datetime.fromisoformat(user.created_at) + timedelta(
            seconds=random.randint(5, 300)
        )

        assignment = Assignment(
            user_id=user.user_id,
            experiment_id=EXPERIMENT_ID,
            variant=variant,
            assigned_at=isoformat(assignment_time),
        )

        users.append(user)
        assignments.append(assignment)
        events.extend(generate_events_for_user(user, assignment))

    messy_events = inject_messy_events(events)

    write_csv(output_dir / "users.csv", [asdict(user) for user in users])
    write_csv(output_dir / "experiment_assignments.csv", [asdict(item) for item in assignments])
    write_csv(output_dir / "events.csv", [asdict(event) for event in messy_events])
    write_jsonl(output_dir / "events.jsonl", [asdict(event) for event in messy_events])

    print(f"Generated {len(users):,} users")
    print(f"Generated {len(assignments):,} experiment assignments")
    print(f"Generated {len(messy_events):,} events")
    print(f"Wrote files to {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate local A/B testing event data.")
    parser.add_argument("--num-users", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("data/sample"))

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_dataset(
        num_users=args.num_users,
        output_dir=args.output_dir,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()