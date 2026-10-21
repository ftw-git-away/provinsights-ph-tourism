# Dashboard

ProvInsights PH shared AI/BI dashboard (PROVINSIGHTS DASHBOARD):
https://dbc-5e346557-03d4.cloud.databricks.com/dashboardsv3/01f1cce3ab3a196c90b5fdc0a8a478a6/published

The pipeline job refreshes it with the task `refresh_dashboard`, which runs after
`analytics_run_evidence`, so it always shows the latest validated data.

| Setting | Where |
| --- | --- |
| Dashboard ID | `dashboard_id` variable in `databricks.yml` |
| SQL warehouse | `warehouse_id` variable in `databricks.yml` |

## Who runs the refresh

The job runs as the identity that deploys it: the owner of the deploy token used by
`deploy.yml`. That identity needs at least **Can Run** on the dashboard, or the
`refresh_dashboard` task fails.

## If the refresh fails

A failed `refresh_dashboard` marks the whole job run as failed and sends the failure email,
even though every table was already written. Check which task failed before assuming the
data build failed.

## Editing the dashboard

Edit it in place in Databricks and publish. Don't re-import it: every import creates a new
dashboard with a new ID. The pipeline only refreshes the data; it does not change the layout.

If the dashboard is ever replaced (new ID), update `dashboard_id` in `databricks.yml` in a PR.