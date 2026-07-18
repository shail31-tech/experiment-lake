-- Segment-level A/B testing summary metrics.

SELECT
    device_type,
    traffic_source,
    plan_type,
    country,
    variant,
    count(*) AS users,
    sum(did_activate) AS activations,
    round(avg(CAST(did_activate AS DOUBLE)), 4) AS activation_rate,
    round(sum(revenue), 2) AS total_revenue,
    round(avg(revenue), 2) AS avg_revenue_per_user
FROM user_experiment_facts
GROUP BY
    device_type,
    traffic_source,
    plan_type,
    country,
    variant
ORDER BY
    device_type,
    traffic_source,
    plan_type,
    country,
    variant;
