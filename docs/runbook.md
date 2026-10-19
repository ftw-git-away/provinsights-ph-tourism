# ProvInsights Runbook

How to set up, run, check and fix the ProvInsights pipeline. For how the pieces fit together, see [architecture.md](architecture.md).

## Contents

1. [Before you start](#1-before-you-start)
2. [Configuration reference](#2-configuration-reference)
3. [Run the full pipeline](#3-run-the-full-pipeline)
4. [Run part of the pipeline](#4-run-part-of-the-pipeline)
5. [Check that a run succeeded](#5-check-that-a-run-succeeded)
6. [When something fails](#6-when-something-fails)
7. [Roll back a table](#7-roll-back-a-table)
8. [Common changes](#8-common-changes)

---

## 1. Before you start

**Important:** every run writes to the shared catalog `tuklas_dev`. Tell the team in the group chat before you start a run, and don't start one while another is running. The job allows only one run at a time, but a notebook run by hand is not blocked.

### Access you need

| Need | For | How to check |
| --- | --- | --- |
| Databricks workspace account | Everything | You can open the workspace |
| `USE CATALOG`, `CREATE SCHEMA` and write access on `tuklas_dev` | Creating and replacing tables | `SHOW SCHEMAS IN tuklas_dev` works and lists `01_ingestion` to `06_data_quality` |
| Use of the Unity Catalog connection `capstone_gdrive` | Reading source files from Google Drive | The folder listing cell in any ingestion notebook returns files |
| Read access to the three Google Drive source folders (PSA, PSGC, DOT) | Ingestion | Same as above |
| GitHub write access to the repository | Pull requests, running the deploy workflow | You can open a PR |

### Tools (only for running from your computer)

- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/) (the deploy workflow pins version 1.19.0)
- Git

No local Python environment is needed. The notebooks install their own libraries (`openpyxl`, `pdfplumber`) with `%pip install` when they run on Databricks.

### One-time setup for local runs

```bash
git clone https://github.com/ftw-git-away/provinsights-ph-tourism.git
cd provinsights-ph-tourism

# sign in once and save a profile
databricks auth login --host <workspace URL> --profile <profile>
```

Never commit the workspace URL, a token or an email address. The bundle takes the alert email as a variable, and GitHub Actions reads the URL and token from the `development` environment settings.

## 2. Configuration reference

Settings live in the notebooks' **Configuration** cells and in the bundle. They are not job parameters.

| Setting | Where | Default | Notes |
| --- | --- | --- | --- |
| `CATALOG` | First code cell of every notebook | `tuklas_dev` | Change it in every notebook if you ever run against another catalog |
| `GOOGLE_DRIVE_CONNECTION` | Ingestion notebooks | `capstone_gdrive` | Unity Catalog connection; no keys are stored in the repository |
| Source folder and file URLs | `SOURCE_FILES` and `*_FOLDER` in each ingestion notebook | — | File IDs are stable; see [bronze-ingestion-guide.md](bronze-ingestion-guide.md) |
| `YEARS_TO_RUN` | `03_ingest_dot` | `"all"` | Or a list such as `["2023"]` to reload only those years |
| Seed CSV paths | `SEED_RELATIVE_PATH` in Silver and Gold notebooks | `resources/seeds/...` | Set `SEED_PATH_OVERRIDE` (for example a Volume path) only when the repository files are not available |
| DQ thresholds and expected lists | Configuration cell of each Silver, Gold and Analytics notebook | — | Documented in [data-quality-rules.md](data-quality-rules.md) §5 |
| `alert_email` | Bundle variable (`databricks.yml`) | — | Receives failure emails; passed with `--var` or from GitHub |

## 3. Run the full pipeline

The job **ProvInsights PH - End-to-End Pipeline** runs all 18 tasks in order: ingestion, Silver, Gold, Analytics, validation and run evidence. The whole job has a three-hour timeout.

Pick one of these three ways.

### Option A: from GitHub (no local setup)

1. Go to **Actions → CD - Deploy ProvInsights PH to Databricks → Run workflow**.
2. Choose branch `main` and tick **run_pipeline**.
3. The workflow validates and deploys the bundle, then starts the job. Follow the run from the link in the workflow log, or in Databricks under **Workflows**.

A normal merge to `main` deploys the job but **does not run it**. Only a manual run with **run_pipeline** ticked starts it.

### Option B: from your computer

```bash
# 1. check the bundle
databricks bundle validate -t dev -p <profile> --var="alert_email=<your email>"

# 2. deploy your branch to your own dev folder
databricks bundle deploy -t dev -p <profile> --var="alert_email=<your email>"

# 3. run the job (writes to tuklas_dev; tell the team first)
databricks bundle run -t dev -p <profile> tourism_pipeline --var="alert_email=<your email>"
```

In the `dev` target the job shows up as `[dev <your user>] ProvInsights PH - End-to-End Pipeline`, so your deployment doesn't replace a teammate's.

### Option C: from the Databricks UI

Open **Workflows**, find the job, and click **Run now**. This runs whatever was last deployed, not your local changes.

## 4. Run part of the pipeline

### Rerun after a failure

In Databricks, open the failed run and click **Repair run**. It reruns the failed task and everything after it, and skips the tasks that already succeeded. Fix the cause first (section 6).

### Run one notebook by hand

You can open any notebook and run it top to bottom. Follow these rules:

- Run the layer's setup notebook first if the schema or run log might not exist (`00_ingestion_setup`, `00_silver_setup`, `00_gold_setup`). Setup notebooks are safe to rerun.
- Respect the order. A notebook reads the tables from the layer before it, so rebuilding Silver means rebuilding Gold and Analytics after it.

| If you changed or reloaded… | Rerun, in this order |
| --- | --- |
| One source in Bronze | Its Silver notebook → all three Gold notebooks → `01_build_analytics` → `02_analytics_validation` |
| `geo_*` or a crosswalk seed | `01_silver_geography` → every other Silver notebook → Gold → Analytics |
| A Gold notebook | The remaining Gold notebooks → Analytics |
| Analytics logic only | `01_build_analytics` → `02_analytics_validation` |

- Run evidence notebooks (`04_gold_run_evidence`, `03_analytics_run_evidence`) are read-only and can be run any time.

## 5. Check that a run succeeded

### Quick checklist

- [ ] The job run is green, with every task **Succeeded**.
- [ ] No run log has `FAILED` for this run (query below).
- [ ] Any REVIEW flag is one you expected (see the [known exceptions register](data-quality-rules.md#7-known-exceptions-register)).
- [ ] Gold row counts are 100, 6 and 600.
- [ ] `02_analytics_validation` finished with no BLOCK failure.

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
| `FAILED` | A BLOCK check failed or an error was raised; tables were **not** replaced | Section 6 |
| `STARTED` with no end time | The notebook stopped without finishing, for example a timeout or a cancelled run | Rerun it |

### Failed checks from the latest runs

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

Run `04_gold_run_evidence` and `03_analytics_run_evidence`. They summarize the latest runs, every check and the caveats. Their last cell prints markdown for [gold-run-evidence.md](gold-run-evidence.md) and [analytics-run-evidence.md](analytics-run-evidence.md). Paste it in after a run that changes results, and open a PR.

## 6. When something fails

Start with the failed task's output in the job run. The last cell usually names the check or error. Then find the matching row below.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| A Silver, Gold or Analytics task fails with a BLOCK check | The data breaks a correctness rule: duplicate key, unmapped label, totals that don't reconcile, a value changed between layers | Run the failed-checks query. `sample_keys` shows the rows. Fix the cause (usually a seed or an upstream table), then **Repair run**. Never weaken a BLOCK check to get past it. Downgrading one needs a decision-log entry. |
| Run is `SUCCESS_WITH_REVIEW` | Something unusual, such as a large year-over-year jump | If it's in the known exceptions register, nothing to do. If it's new, raise it with the team and record the outcome in the [decision log](project-decision-log.md). |
| `01_silver_geography` fails on crosswalk coverage | A DOT or PSA label isn't in the seed, usually a new year or a renamed place | Add the label to the right seed CSV in `resources/seeds/` through a PR (section 8), then rerun from Silver. |
| Ingestion task `FAILED` or `PARTIAL_SUCCESS` | A file is missing, renamed, or not shared with the connection | Check `ingestion_errors` and `file_manifest` for the file. Confirm it's in the Drive folder and that `SOURCE_FILES` matches its name and ID. |
| `file_manifest` notes say the source fingerprint changed | The source file in Drive was replaced | Confirm the change was intended. A new file can change every number downstream, so rerun the whole pipeline and compare the run evidence. |
| Folder listing returns nothing or a permission error | No access to `capstone_gdrive` or the folder | Ask a workspace admin to grant use of the connection, or reshare the folder. |
| `%pip install` fails | The workspace can't reach PyPI | Rerun the task. If it keeps failing, check the workspace's network settings. |
| The notebook can't find a seed CSV | The notebook can't find the repository files, for example it was run from a copy outside the bundle folder | Run it from the deployed bundle folder, or set `SEED_PATH_OVERRIDE`. |
| `01_build_analytics` fails `Gold_versions_unchanged_during_run` | A Gold table was rewritten while Analytics was running | Make sure nobody else is running Gold, then rerun Analytics. |
| `02_analytics_validation` fails recomputation or Gold reconciliation | An Analytics formula changed, or Gold changed after Analytics was built | Rerun `01_build_analytics`, then validation. If it still fails, the formula change is wrong. |
| Task timed out | Slow compute or an unexpectedly large input | Per-task timeouts are about three times the longest observed run. **Repair run** once. If it times out again, look at what changed in the input. |
| CI **Validate Databricks bundle** fails on a PR | Invalid YAML, a wrong notebook path, or a notebook that isn't on the branch yet | Run `databricks bundle validate -t dev` locally, fix the path, or merge `main` into your branch. |
| Deploy workflow fails at "Check required GitHub configuration" | `DATABRICKS_HOST`, `DATABRICKS_TOKEN` or `DATABRICKS_ALERT_EMAIL` is missing | A repository admin adds it under **Settings → Environments → development**. |

If a BLOCK failure doesn't make sense, don't rerun repeatedly. Ask in the team chat with the `check_id`, `run_id` and `sample_keys`.

## 7. Roll back a table

Every table is a Delta table, so earlier versions are kept. Use this if a run wrote something wrong.

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
- Tell the team, and note the restore in the PR or issue that fixes the cause.

## 8. Common changes

Every change goes through a pull request using the [PR template](../.github/PULL_REQUEST_TEMPLATE.md). CI must pass, and a teammate must review it.

### Update a crosswalk seed

1. Edit the CSV in `resources/seeds/` (see [seeds/README.md](../resources/seeds/README.md) for the columns and roles).
2. If the change is a new rule (a new exclusion, a place added to another), add a decision to the [decision log](project-decision-log.md).
3. After merge, rerun from `01_silver_geography`, or the matching Silver notebook for PSA and population seeds.
4. Check that the coverage checks pass, and paste the results into the PR.

### Add or change a data-quality check

Follow [data-quality-rules.md §10](data-quality-rules.md#10-adding-or-changing-a-check).

### Add a job task

Add the task to [`resources/jobs/tourism_pipeline.yml`](../resources/jobs/tourism_pipeline.yml) with its `depends_on` and a timeout. Then run `databricks bundle validate`. Details are in [`resources/README.md`](../resources/README.md).

### Load a new year of source data

1. Put the new file in the right Google Drive folder and add it to `SOURCE_FILES` in the ingestion notebook.
2. For DOT, set `YEARS_TO_RUN` to the new year to load only that year.
3. Expect `01_silver_geography` to fail on coverage if the new file prints labels the seeds don't know. Add them as described above.
4. Check the year range in the Configuration cells of the Silver, Gold and Analytics notebooks. The current build covers 2019–2024, with 2019 as the baseline and 2023 as the headline year (DL-004).
5. Run the full pipeline, then update the run evidence documents.
