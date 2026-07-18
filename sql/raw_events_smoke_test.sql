-- Basic smoke test for the raw_events Glue table.

SELECT
    experiment_id,
    event_date,
    event_name,
    count(*) AS event_count
FROM raw_events
GROUP BY
    experiment_id,
    event_date,
    event_name
ORDER BY
    event_count DESC;