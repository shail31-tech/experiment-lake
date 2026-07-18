-- CTAS query for one row per user per experiment.
-- The Python pipeline injects the curated S3 output location.

CREATE TABLE user_experiment_facts
WITH (
    format = 'PARQUET',
    external_location = '${CURATED_LOCATION}',
    write_compression = 'SNAPPY'
) AS
WITH deduped_events AS (
    SELECT
        event_id,
        user_id,
        session_id,
        experiment_id,
        variant,
        event_name,
        CAST(from_iso8601_timestamp(event_timestamp) AS timestamp) AS event_ts,
        device_type,
        country,
        traffic_source,
        plan_type,
        CAST(revenue AS DOUBLE) AS revenue,
        row_number() OVER (
            PARTITION BY event_id
            ORDER BY CAST(from_iso8601_timestamp(event_timestamp) AS timestamp)
        ) AS event_row_number
    FROM raw_events
),

clean_events AS (
    SELECT *
    FROM deduped_events
    WHERE event_row_number = 1
),

user_facts AS (
    SELECT
        user_id,
        experiment_id,
        arbitrary(variant) AS variant,
        arbitrary(device_type) AS device_type,
        arbitrary(country) AS country,
        arbitrary(traffic_source) AS traffic_source,
        arbitrary(plan_type) AS plan_type,

        min(CASE WHEN event_name = 'experiment_exposed' THEN event_ts END) AS first_exposed_at,

        max(CASE WHEN event_name = 'experiment_exposed' THEN 1 ELSE 0 END) AS was_exposed,
        max(CASE WHEN event_name = 'signup_completed' THEN 1 ELSE 0 END) AS did_signup,
        max(CASE WHEN event_name = 'onboarding_completed' THEN 1 ELSE 0 END) AS did_activate,
        max(CASE WHEN event_name = 'subscription_started' THEN 1 ELSE 0 END) AS did_subscribe,

        sum(CASE WHEN event_name = 'subscription_started' THEN revenue ELSE 0 END) AS revenue
    FROM clean_events
    GROUP BY
        user_id,
        experiment_id
)

SELECT *
FROM user_facts
WHERE was_exposed = 1;
