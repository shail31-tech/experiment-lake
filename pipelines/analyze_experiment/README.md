# Analyze Experiment

This pipeline queries the curated `user_experiment_facts` table and runs statistical A/B testing.

## Metrics

- users
- activations
- subscriptions
- revenue
- activation rate
- subscription rate
- average revenue per user

## Statistical Outputs

- absolute lift
- relative lift
- p-value
- 95% confidence interval
- sample ratio mismatch check
- ship / do-not-ship decision

## Run

From the project root:

```bash
make analyze-ab-test
```
