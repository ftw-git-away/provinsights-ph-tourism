# Dashboard

AI/BI dashboard for ProvInsights PH, deployed by the bundle and refreshed by the pipeline.

| File | Purpose |
| --- | --- |
| `provinsights.lvdash.json` | Dashboard definition (datasets, pages, widgets) |
| `../resources/dashboards/provinsights.dashboard.yml` | Bundle resource: name, warehouse, file path |

The job task `refresh_dashboard` runs after `analytics_run_evidence`, so the dashboard
always shows the latest validated data. Queries run on the SQL warehouse set in the
`warehouse_id` variable in `databricks.yml`.

## Changing the dashboard

The JSON file in this folder is the source of truth: every deploy overwrites the
deployed dashboard with it. To change the dashboard:

1. Edit the draft in Databricks.
2. Pull the changes into the repo on a new branch:

```bash
   databricks bundle generate dashboard --resource provinsights --force
```

3. Open a PR. After it merges, the deploy workflow publishes the update.
