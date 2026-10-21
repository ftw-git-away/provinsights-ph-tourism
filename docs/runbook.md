# ProvInsights Runbook

**Audience:** whoever runs and monitors the pipeline day to day. It covers running the job, checking a run, fixing failures and rolling back. One-time setup is in [setup and handoff](setup-and-handoff.md), and changes to the pipeline are in [making changes](making-changes.md). For how the pieces fit together, see [architecture.md](architecture.md).

## Contents

- [Before you start](#before-you-start)
1. [Run the full pipeline](#1-run-the-full-pipeline)
2. [Run part of the pipeline](#2-run-part-of-the-pipeline)
3. [Check that a run succeeded](#3-check-that-a-run-succeeded)
4. [When something fails](#4-when-something-fails)
5. [Roll back a table](#5-roll-back-a-table)

---

## Before you start

**Important:** every run writes to the shared catalog `tuklas_dev` and, at the end, refreshes the shared dashboard. Tell the team in the group chat before you start a run, and don't start one while another is running. The job allows only one run at a time, but a notebook run by hand is not blocked.

### Folders and schemas

Notebook folders and the schemas they write to have different numbers. The schema names did not change when the folders were renamed.

| Notebook folder | Writes to schema(s) |
| --- | --- |
| `notebooks/01_ingestion_bronze` | `01_ingestion` (run metadata), `02_bronze` (source data as printed) |
| `notebooks/02_silver` | `03_silver` |
| `notebooks/03_gold` | `04_gold` |
| `notebooks/04_analytics` | `05_analytics` |
| `notebooks/99_maintenance` | One-off notebooks run by hand, not part of the job |

Data-quality results from every layer go to `06_data_quality.dq_results`.

## 1. Run the full pipeline

The job **ProvInsights PH - End-to-End Pipeline** runs 19 tasks in order: ingestion, Silver, Gold, Analytics (build, validation and run evidence), then `refresh_dashboard`. The whole job has a three-hour timeout. Task order and settings are in [`resources/README.md`](../resources/README.md).

Pick one of these three ways.

### Option A: from GitHub (no local setup)

1. Go to **Actions → CD - Deploy ProvInsights PH to Databricks → Run workflow**.
2. Choose branch `main` and tick **run_pipeline**.
3. The workflow validates and deploys the bundle, then starts the job. Follow the run from the link in the workflow log, or in Databricks under **Jobs & Pipelines**.

A normal merge to `main` deploys the job but **does not run it**. Only a manual run with **run_pipeline** ticked starts it.

### Option B: from your computer

```bash
# 1. check the bundle
databricks bundle validate -t dev -p <profile> --var="alert_email=<your email>"

# 2. deploy your branch to your own dev folder
databricks bundle deploy -t dev -p <profile> --var="alert_email=<your email>"

# 3. run the job (writes to tuklas_dev and refreshes the shared dashboard; tell the team first)
databricks bundle run -t dev -p <profile> tourism_pipeline --var="alert_email=<your email>"
```

In the `dev` target the job shows up as `[dev <your user>] ProvInsights PH - End-to-End Pipeline`, so your deployment doesn't replace a teammate's. It still writes to the same `tuklas_dev` tables and refreshes the same shared dashboard, because `dashboard_id` points to it.

### Option C: from the Databricks UI

Open **Jobs & Pipelines**, find the job, and click **Run now**. This runs whatever was last deployed, not your local changes.

## 2. Run part of the pipeline

### Rerun after a failure

In Databricks, open the failed run and click **Repair run**. It reruns the failed task and everything after it, and skips the tasks that already succeeded. Fix the cause first (section 4).

### Run one notebook by hand

You can open any notebook and run it top to bottom. Follow these rules:

- Run the layer's setup notebook first if the schema or run log might not exist (`00_ingestion_setup`, `00_silver_setup`, `00_gold_setup`). Setup notebooks are safe to rerun.
- Respect the order. A notebook reads the tables from the layer before it, so rebuilding Silver means rebuilding Gold and Analytics after it.
- `01_build_analytics` takes about 15 minutes. If you start it with `dbutils.notebook.run`, give it a timeout of at least 1800 seconds; 600 is too short.

| If you changed or reloaded… | Rerun, in this order |
| --- | --- |
| One source in Bronze | Its Silver notebook → all three Gold notebooks → `01_build_analytics` → `02_analytics_validation` |
| `geo_*` or a crosswalk seed | `01_silver_geography` → every other Silver notebook → Gold → Analytics |
| A Gold notebook | The remaining Gold notebooks → Analytics |
| Analytics logic only | `01_build_analytics` → `02_analytics_validation` |

- Always run `02_analytics_validation` after `01_build_analytics`. If the build stops partway, some Analytics tables carry the new run ID and others the old one, and validation fails its lineage check until a full build finishes.
- Run evidence notebooks (`04_gold_run_evidence`, `03_analytics_run_evidence`) are read-only and can be run any time.
- A notebook run by hand does not refresh the dashboard. Refresh it from the dashboard in Databricks, or wait for the next job run.

## 3. Check that a run succeeded

### Quick checklist

- [ ] The job run is green, with every task **Succeeded**, including `refresh_dashboard`.
- [ ] No run log has `FAILED` for this run (query below).
- [ ] Any REVIEW flag is one you expected (see the [known exceptions register](data-quality-rules.md#7-known-exceptions-register)).
- [ ] Gold row counts are 100, 6 and 600.
- [ ] `01_build_analytics` wrote 5 tables and 958 rows, and `02_analytics_validation` finished with no BLOCK failure.
- [ ] The dashboard shows the new data (the refresh time on the dashboard is after the run).

### Run status by layer

Each layer logs one row per notebook run. In `analytics_run_log`, column 3 is the start time.

```sql
SELECT * FROM tuklas_dev.`01_ingestion`.ingestion_run_log  ORDER BY started_at DESC LIMIT 10;
SELECT * FROM tuklas_dev.`03_silver`.silver_run_log        ORDER BY started_at DESC LIMIT 10;
SELECT * FROM tuklas_dev.`04_gold`.gold_run_log            ORDER BY started_at DESC LIMIT 10;
SELECT * FROM tuklas_dev.`05_analytics`.analytics_run_log  ORDER BY 3 DESC LIMIT 10;
```

| Status | Meaning | Action |
| --- | --- | --- |
| `SUCCESS` | All checks passed and tables were written | None |
| `SUCCESS_WITH_REVIEW` | Tables were written, but a REVIEW check flagged something | Look at the flagged checks (next query) |
| `PARTIAL_SUCCESS` (ingestion) | Some files loaded, some didn't | Check `ingestion_errors` |
| `FAILED` | A BLOCK check failed or an error was raised; the table that failed its checks was **not** replaced | Section 6 |
| `STARTED` with no end time | The notebook stopped without finishing, for example a timeout or a cancelled run | Rerun it |

### Failed checks from the latest runs

Every check has a documented ID (`DQ-COM`, `DQ-DOT`, `DQ-PSA`, `DQ-POP`, `DQ-GLD`, `DQ-ANL`). The `notes` column keeps the check's original name.

```sql
SELECT notebook_name, check_id, severity, status, failed_rows, expected, observed, sample_keys, notes
FROM tuklas_dev.`06_data_quality`.dq_results
WHERE status = 'FAIL'
  AND checked_at >= current_timestamp() - INTERVAL 1 DAY
ORDER BY severity, notebook_name, check_id;
```

### Row counts

```sql
SELECT 'dim_province' AS t, COUNT(*) AS n FROM tuklas_dev.`04_gold`.dim_province        -- expect 100
UNION ALL SELECT 'dim_year', COUNT(*)     FROM tuklas_dev.`04_gold`.dim_year            -- expect 6
UNION ALL SELECT 'fact',     COUNT(*)     FROM tuklas_dev.`04_gold`.fact_province_year; -- expect 600
```

### Full evidence

The job runs `04_gold_run_evidence` and `03_analytics_run_evidence` on every run. They summarize the latest runs, every check and the caveats. To update [gold-run-evidence.md](gold-run-evidence.md) and [analytics-run-evidence.md](analytics-run-evidence.md) after a run that changes results, open the notebook output, copy the markdown printed by the last cell, and open a PR. Update the run IDs and Gold versions in the doc, and say which screenshots come from an earlier run.

## 4. When something fails

Start with the failed task's output in the job run. The last cell usually names the check or error. Then find the matching row below.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| A Silver, Gold or Analytics task fails with a BLOCK check | The data breaks a correctness rule: duplicate key, unmapped label, totals that don't reconcile, a value changed between layers | Run the failed-checks query. `sample_keys` shows the rows. Fix the cause (usually a seed or an upstream table), then **Repair run**. Never weaken a BLOCK check to get past it. Downgrading one needs a decision-log entry. |
| Run is `SUCCESS_WITH_REVIEW` | Something unusual, such as a large year-over-year jump | If it's in the known exceptions register, nothing to do. If it's new, raise it with the team and record the outcome in the [decision log](project-decision-log.md). |
| An Analytics notebook stops with "No DQ-ANL ID for check ..." | A new or renamed check has no documented ID | Add it to `DQ_ID_BUILD` (build) or match a prefix in `DQ_ID_RULES` (validation), and list it in [data-quality-rules.md](data-quality-rules.md) section 6.7. Tables from earlier phases of that run may already be replaced, so rerun the build in full. |
| `01_silver_geography` fails on crosswalk coverage | A DOT or PSA label isn't in the seed, usually a new year or a renamed place | Add the label to the right seed CSV in `resources/seeds/` through a PR ([making changes](making-changes.md#update-a-crosswalk-seed)), then rerun from Silver. |
| Ingestion task `FAILED` or `PARTIAL_SUCCESS` | A file is missing, renamed, or not shared with the connection | Check `ingestion_errors` and `file_manifest` for the file. Confirm it's in the Drive folder and that `SOURCE_FILES` matches its name and ID. |
| `file_manifest` notes say the source fingerprint changed | The source file in Drive was replaced | Confirm the change was intended. A new file can change every number downstream, so rerun the whole pipeline and compare the run evidence. |
| Folder listing returns nothing or a permission error | No access to `capstone_gdrive` or the folder | Ask a workspace admin to grant use of the connection, or reshare the folder. |
| Creating a table fails because the metastore is at its table limit | This metastore has a 500-table quota, and old Bronze tables use it up (it was full on 2026-10-20) | Run `notebooks/99_maintenance/drop_stale_bronze_tables` by hand after checking its list with the team (DL-038). It only drops tables no notebook reads. |
| `%pip install` fails | The workspace can't reach PyPI | Rerun the task. If it keeps failing, check the workspace's network settings. |
| The notebook can't find a seed CSV | The notebook can't find the repository files, for example it was run from a copy outside the bundle folder | Run it from the deployed bundle folder, or set `SEED_PATH_OVERRIDE`. |
| `01_build_analytics` fails `Gold_versions_unchanged_during_run` | A Gold table was rewritten while Analytics was running | Make sure nobody else is running Gold, then rerun Analytics. |
| `02_analytics_validation` fails recomputation, lineage or Gold reconciliation | An Analytics formula changed, Gold changed after Analytics was built, or the last build stopped partway | Rerun `01_build_analytics` to completion, then validation. If it still fails, the formula change is wrong. |
| `refresh_dashboard` fails | The job's run-as identity lacks **Can Run** on the dashboard, or `dashboard_id` / `warehouse_id` is wrong | The data is already built. Fix the permission or variable (see [dashboard/README.md](../dashboard/README.md)), then **Repair run** only that task. |
| Task timed out | Slow compute, a serverless start-up wait, or an unexpectedly large input | Setup, run-evidence and dashboard tasks allow 1800 s for serverless waits; Analytics limits are about three times the longest observed run. **Repair run** once. If it times out again, look at what changed in the input. |
| CI **Validate repository** fails on a PR | A unit test failed: the job definition, a notebook cell, SQL syntax, a seed file or the docs alignment | The test message names the file, task, cell or seed row. Run the unit tests locally ([making changes](making-changes.md#run-the-unit-tests-before-a-pr)), fix it, and push. |
| CI **Validate Databricks bundle** fails on a PR | Invalid YAML, a wrong notebook path, or a notebook that isn't on the branch yet | Run `databricks bundle validate -t dev` locally, fix the path, or merge `main` into your branch. |
| Deploy workflow fails at "Check required GitHub configuration" | `DATABRICKS_HOST`, `DATABRICKS_TOKEN` or `DATABRICKS_ALERT_EMAIL` is missing | A repository admin adds it under **Settings → Environments → development**. |

If a BLOCK failure doesn't make sense, don't rerun repeatedly. Ask in the team chat with the `check_id`, `run_id` and `sample_keys`.

## 5. Roll back a table

Every table is a Delta table, so earlier versions are kept. Use this if a run wrote something wrong. The version number below is an example; use one from the history.

```sql
-- see the versions and when they were written
DESCRIBE HISTORY tuklas_dev.`04_gold`.fact_province_year;

-- look at an earlier version without changing anything
SELECT * FROM tuklas_dev.`04_gold`.fact_province_year VERSION AS OF 12;

-- restore it
RESTORE TABLE tuklas_dev.`04_gold`.fact_province_year TO VERSION AS OF 12;
```

- Restore downstream tables too, or rebuild them, so the layers stay consistent.
- Analytics rows record the Gold versions they were built from (`_gold_fact_version`, `_gold_dim_province_version`, `_gold_dim_year_version`). Use them to find the matching Gold version.
- After a restore, refresh the dashboard so it shows the restored data.
- Tell the team, and note the restore in the PR or issue that fixes the cause.
