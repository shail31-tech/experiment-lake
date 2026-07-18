# Experiment Design

The project simulates a SaaS onboarding experiment.

## Variants

- `control`: existing onboarding experience
- `simplified`: shorter onboarding flow
- `guided_checklist`: guided checklist onboarding flow

## Primary Metric

Activation rate:

```text
activated users / exposed users
```

In this project, activation is represented by the `onboarding_completed` event.

## Secondary Metrics

- Signup completion rate
- Subscription rate
- Total revenue
- Average revenue per user

## Guardrail Metrics

Future project extensions can add:

- Error rate
- Dropoff rate
- Support contact rate
- Refund or cancellation rate
- Page latency

## Simulated Behavior

The event generator intentionally creates a non-uniform but plausible experiment:

- Desktop users respond especially well to `guided_checklist`.
- Mobile users have lower baseline conversion.
- Email traffic tends to convert better than paid search.
- Returning users have slightly higher activation.
- Revenue is noisy and right-skewed.

The generator also injects messy data:

- Duplicate event rows
- Late-arriving event rows

This makes the downstream data engineering more realistic.
