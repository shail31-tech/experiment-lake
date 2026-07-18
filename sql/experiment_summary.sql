-- Variant-level A/B testing summary metrics.

WITH user_experiment_facts AS (
    -- Paste the query from user_experiment_facts.sql here, excluding the final semicolon.
    SELECT *
    FROM raw_events
)

SELECT
    experiment_id,
    variant,
    count(*) AS users,
    sum(was_exposed) AS exposed_users,
    sum(did_signup) AS signups,
    sum(did_activate) AS activations,
    sum(did_subscribe) AS subscriptions,
    round(avg(CAST(did_activate AS DOUBLE)), 4) AS activation_rate,
    round(avg(CAST(did_subscribe AS DOUBLE)), 4) AS subscription_rate,
    round(sum(revenue), 2) AS total_revenue,
    round(avg(revenue), 2) AS avg_revenue_per_user
FROM user_experiment_facts
GROUP BY
    experiment_id,
    variant
ORDER BY
    experiment_id,
    variant;