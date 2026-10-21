# Runbook

How to deploy, run and check the ProvInsights pipeline, and what to do when something fails.

## Deploy

Merging into `main` deploys automatically: the **CD - Deploy ProvInsights PH to Databricks** workflow validates and deploys the bundle. Deploying updates the job but does not run it.

To deploy your branch to your own dev folder for testing:

```bash
databricks bundle validate -t dev -p <profile> --var="alert_email=<your email>"
databricks bundle deploy -t dev -p <profile> --var="alert_email=<your email>"
```

## Run

In Databricks, open **Jobs & Pipelines → ProvInsights PH - End-to-End Pipeline → Run now**, or:

```bash
databricks bundle run -t dev -p <profile> tourism_pipeline --var="alert_email=<your email>"
```

A run writes to the shared `tuklas_dev` catalog, so tell the team first. To test a single task without a full run, add `--only <task_key>` (for example `--only refresh_dashboard`).

## Check a run

1. **Job run page:** every task is green. The last task, `refresh_dashboard`, refreshes the shared dashboard.
2. **Data quality:** no failed `BLOCK` checks for the run.
```sql
   SELECT notebook_name, severity, status, count(*) AS checks
   FROM tuklas_dev.`06_data_quality`.dq_results
   WHERE checked_at >= (SELECT max(checked_at) FROM tuklas_dev.`06_data_quality`.dq_results) - INTERVAL 24 HOURS
   GROUP BY ALL ORDER BY ALL;
```
3. **REVIEW flags:** read `check_id`, `sample_keys` and `notes` for any failed `REVIEW` check and tell the owner of that layer.
4. **Table history:** `DESCRIBE HISTORY` on a Gold or Analytics table shows the run's `jobRunId`.

## When something fails

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| A task fails and the tasks after it show **Upstream failed** | A failed `BLOCK` check or a notebook error | Open the failed task's output, fix the cause in a PR, then run again |
| A task **timed out** | Serverless compute was slow to start | Repair the run (rerun failed tasks only). If it keeps happening, raise that task's `timeout_seconds` in a PR |
| **Repair** says dependencies have changed | The job was redeployed with a different task order since the run | Start a fresh run instead |
| `refresh_dashboard` fails | The job's identity lacks **Can Run** on the dashboard, or `dashboard_id` is wrong | Check sharing on the dashboard and `dashboard_id` in `databricks.yml` ([dashboard/README.md](../dashboard/README.md)). All tables were already written |
| A PR can't merge | A required check failed, the branch is out of date, or a review is missing | Read the failed check's log, click **Update branch**, and ask for a review |
| CI or deploy fails with an authentication error | The Databricks token in the GitHub environment has expired | Create a new token and replace `DATABRICKS_TOKEN` in **Settings → Environments** (`ci-validate` or `development`) |

Failure emails go to `alert_email` (set by `DATABRICKS_ALERT_EMAIL` in the `development` environment).