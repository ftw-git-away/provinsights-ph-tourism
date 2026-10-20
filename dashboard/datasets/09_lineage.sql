-- dataset: ds_lineage
-- display: Data lineage
-- source: tuklas_dev.05_analytics (tourism_activity)
-- used by: Definitions: analytics build id and time
SELECT MAX(_analytics_run_id) AS `Analytics build`, MAX(_processed_at) AS `Built at`
FROM tourism_activity
