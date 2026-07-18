# Event Generator

This module generates local A/B testing event data for ExperimentLake.

The generator simulates a SaaS onboarding experiment with three variants:

- `control`: existing onboarding
- `simplified`: shorter onboarding flow
- `guided_checklist`: guided checklist onboarding

## Output Files

Generated files are written to `data/sample` by default:

- `users.csv`
- `experiment_assignments.csv`
- `events.csv`
- `events.jsonl`

These generated files are ignored by git.

## Concepts Modeled

- Sticky user-level variant assignment
- Exposure events
- Signup and onboarding funnel events
- Segment effects by device and traffic source
- Revenue skew
- Duplicate events
- Late-arriving events

## Generate Data

From the project root:

```bash
make generate-sample
make validate-sample
```

Or directly:

```bash
python app/event_generator/generate_events.py --num-users 5000
python app/event_generator/validate_events.py
```

## Send Events To API

After the ingestion API is deployed, get the endpoint:

```bash
cd terraform/environments/dev
terraform output -raw events_endpoint
```

Send a small test batch from the project root:

```bash
EVENTS_ENDPOINT="$(cd terraform/environments/dev && terraform output -raw events_endpoint)"

python app/event_generator/send_events.py \
  --endpoint-url "$EVENTS_ENDPOINT" \
  --limit 25
```
