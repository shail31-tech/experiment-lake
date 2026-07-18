# Statistical Methodology

ExperimentLake evaluates variants against the control group using user-level experiment facts.

## Analysis Unit

The analysis unit is the user, not the event.

Raw event logs can contain many rows per user, duplicates, and late arrivals. The `user_experiment_facts` curated table collapses those events into one row per user per experiment before statistical testing.

## Metrics

Primary metric:

```text
activation_rate = activations / users
```

Secondary metrics:

- subscription rate
- total revenue
- average revenue per user

## Variant Comparison

Each treatment variant is compared with control using a two-proportion z-test on activation rate.

The analysis reports:

- control rate
- treatment rate
- absolute lift
- relative lift
- p-value
- 95% confidence interval for absolute lift
- ship / do-not-ship decision
- segment-level activation differences

## Decision Rule

The current decision rule is:

```text
ship if p_value < 0.05 and absolute_lift > 0
```

This is intentionally simple for portfolio clarity. A production experimentation platform may also include power checks, multiple-testing correction, sequential testing controls, and guardrail metrics.

## Segment Analysis

The dashboard compares treatment lift within user segments such as:

- device type
- traffic source
- plan type
- country

Segment analysis helps explain whether a top-line win is broad-based or concentrated in a specific group. This is useful for rollout decisions, but it should be interpreted carefully because repeated segment slicing increases false-positive risk.

## Sample Ratio Mismatch

The sample ratio check compares observed users by variant with the expected even split. A low p-value can indicate a randomization, logging, or eligibility problem.

Current rule:

```text
pass if p_value >= 0.01
investigate otherwise
```
