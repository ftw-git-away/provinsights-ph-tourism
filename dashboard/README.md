# Dashboard

ProvInsights PH shared AI/BI dashboard:
https://dbc-5e346557-03d4.cloud.databricks.com/dashboardsv3/01f1cc8008c31c93964133b570b193a4/published

The pipeline job refreshes it with the task `refresh_dashboard`, which runs after
`analytics_run_evidence`, so it always shows the latest validated data.

| Setting | Where |
| --- | --- |
| Dashboard ID | `dashboard_id` variable in `databricks.yml` |
| SQL warehouse | `warehouse_id` variable in `databricks.yml` |

## Editing the dashboard

Edit it directly in Databricks and publish. The pipeline only refreshes the data;
it does not change the layout.

If the dashboard is replaced (new ID), update `dashboard_id` in `databricks.yml` in a PR.