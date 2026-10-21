# ProvInsights Runbook

How to set up, run, check and fix the ProvInsights pipeline. For how the pieces fit together, see [architecture.md](architecture.md). For what each table and column means, see the [data dictionary](data-dictionary.md).

## Contents

0. [Hand-off: set up in a new workspace](#0-hand-off-set-up-in-a-new-workspace)
1. [Before you start](#1-before-you-start)
2. [Configuration reference](#2-configuration-reference)
3. [Run the full pipeline](#3-run-the-full-pipeline)
4. [Run part of the pipeline](#4-run-part-of-the-pipeline)
5. [Check that a run succeeded](#5-check-that-a-run-succeeded)
6. [When something fails](#6-when-something-fails)
7. [Roll back a table](#7-roll-back-a-table)
8. [Common changes](#8-common-changes)

---

## 0. Hand-off: set up in a new workspace

Do this once, when ProvInsights is handed to a new owner or moved to a workspace where it has never run. Steps 0.1 to 0.7 set it up; 0.8 lists what to transfer from the current team. In the current workspace everything below already exists, so skip to [section 1](#1-before-you-start).

The version being handed over is the `v1.0-handoff` tag on `main`. Start from that tag, not from a later commit, and confirm the commit with `git rev-parse v1.0-handoff`.

### 0.1 What the new workspace needs

- A Databricks workspace with Unity Catalog and serverless compute for notebooks and jobs
- A SQL warehouse (serverless is fine) for the dashboard refresh
- A Google account that can read the three source folders listed in the [Bronze ingestion guide](bronze-ingestion-guide.md#source-access)
- Admin access to the GitHub repository, to set the environments in 0.6

### 0.2 Create the catalog and the two ingestion schemas

The notebooks use the catalog name `tuklas_dev`. The setup tasks create `03_silver`, `04_gold`, `05_analytics` and `06_data_quality`, but `00_ingestion_setup` only checks that `01_ingestion` exists and stops if it doesn't, and the ingestion notebooks write to `02_bronze` without creating it. Run this once in a SQL editor:

```sql
CREATE CATALOG IF NOT EXISTS tuklas_dev;
CREATE SCHEMA IF NOT EXISTS tuklas_dev.`01_ingestion`;
CREATE SCHEMA IF NOT EXISTS tuklas_dev.`02_bronze`;
```

Then give the team `USE CATALOG`, `CREATE SCHEMA` and write access on `tuklas_dev` (section 1, "Access you need").

To use a different catalog name, change `CATALOG = "tuklas_dev"` at the top of every notebook and the catalog set on every dashboard dataset, in one pull request.

### 0.3 Create the Google Drive connection

1. In **Catalog Explorer → External data → Connections**, create a Google Drive connection named exactly **`capstone_gdrive`** and sign in with the Google account from 0.1. The name is hard-coded in the ingestion notebooks.
2. Grant the people and the job's run-as user permission to use the connection.
3. Check it: open `03_ingest_dot`, run the cells up to the folder listing, and confirm it lists the six DOT PDFs.

No keys or tokens go into the notebooks or the repository. Access is controlled only through this connection.

### 0.4 Check the source files

The notebooks find each file by its Google Drive file ID (`SOURCE_FILES` and `*_FOLDER` at the top of each ingestion notebook). If the files are copied to new folders, the IDs change: update those settings in a pull request. File names and dataset IDs must follow the [naming convention](bronze-ingestion-guide.md#file-naming).

### 0.5 Create the dashboard and set the bundle variables

1. Import the dashboard: **Dashboards → Create dashboard → ⋮ → Import dashboard from file**, using `dashboard/provinsights.lvdash.json`. Set each dataset's catalog and schema to `tuklas_dev.05_analytics` if they aren't set.
2. Publish it with the SQL warehouse from 0.1, and give the job's run-as user at least **Can Run** on it.
3. Copy the dashboard ID (from its URL) and the warehouse ID (**SQL Warehouses → Connection details**), and set them as the defaults of `dashboard_id` and `warehouse_id` in `databricks.yml` in a pull request.

The dashboard shows no data until the first pipeline run finishes in 0.7.

### 0.6 Set up GitHub

Create the two GitHub environments, `development` (deployment branch `main` only) and `ci-validate`, each with `DATABRICKS_HOST`, `DATABRICKS_TOKEN` and `DATABRICKS_ALERT_EMAIL`. The values, and why there are two environments, are in [`.github/workflows/README.md`](../.github/workflows/README.md#required-github-configuration). Use a validate-only token for `ci-validate`.

### 0.7 First deploy and run

1. Merge the pull requests from 0.4 and 0.5, or run **Actions → CD - Deploy ProvInsights PH to Databricks → Run workflow**. This deploys the job and the seed files.
2. Run the pipeline with **run_pipeline** ticked, or with Option A or B in [section 3](#3-run-the-full-pipeline). The setup tasks create the remaining schemas and control tables on the first run.
3. Check the run with [section 5](#5-check-that-a-run-succeeded). On the current sources, a complete run gives 100 units, 600 fact rows and 958 Analytics rows, with no BLOCK failures.
4. Open the dashboard and compare the test units in [`dashboard/README.md`](../dashboard/README.md#test-unit-reconciliation).

### 0.8 What to transfer

These are tied to a person on the current team, so they don't move with the repository. Transfer or replace each one before the team's access ends.

| Item | Why it matters | What to do |
| --- | --- | --- |
| `capstone_gdrive` connection | It signs in with one person's Google account. If that account loses access, ingestion fails. | Re-create or re-authorize it with the new owner's Google account (0.3), and transfer ownership of the connection in Unity Catalog. |
| Google Drive source folders | The connection can only read folders shared with its account. | Share the three folders with the new owner, or copy them and update the file IDs (0.4). |
| Shared dashboard | Owned by the person who created it, and published with their credentials. | Transfer ownership to the new owner and republish. Check that `dashboard_id` in `databricks.yml` is unchanged. |
| Databricks job | Runs as the person who last deployed it. | Redeploy from the new owner's account (0.7), so the job runs as them. |
| GitHub tokens | `DATABRICKS_TOKEN` in both GitHub environments is a personal access token. | Create new tokens from the new owner's account, update both environments (0.6), and revoke the old tokens. |
| Failure emails | Go to the address in `DATABRICKS_ALERT_EMAIL`. | Change it to the new owner's address. |
| Repository access | Reviews and merges need write access. | Add the new owners on GitHub and keep `main` protected. |

---

## 1. Before you start

**Important:** every run writes to the shared catalog `tuklas_dev` and, at the end, refreshes the shared dashboard. Tell the team in the group chat before you start a run, and don't start one while another is running. The job allows only one run at a time, but a notebook run by hand is not blocked.

### Access you need

| Need | For | How to check |
| --- | --- | --- |
| Databricks workspace account | Everything | You can open the workspace |
| `USE CATALOG`, `CREATE SCHEMA` and write access on `tuklas_dev` | Creating and replacing tables | `SHOW SCHEMAS IN tuklas_dev` works and lists `01_ingestion` to `06_data_quality` |
| Use of the Unity Catalog connection `capstone_gdrive` | Reading source files from Google Drive | The folder listing cell in any ingestion notebook returns files |
| Read access to the three Google Drive source folders (PSA, PSGC, DOT) | Ingestion | Same as above |
| **Can Run** on the shared dashboard and use of the SQL warehouse | The `refresh_dashboard` task | See [dashboard/README.md](../dashboard/README.md) |
| GitHub write access to the repository | Pull requests, running the deploy workflow | You can open a PR |

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

### Tools (only for running from your computer)

- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/) (the deploy workflow pins version 1.19.0)
- Git
- Python 3.12, only for the unit tests (section 8)

The notebooks install their own libraries (`openpyxl`, `pdfplumber`) with `%pip install` when they run on Databricks.

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
| Source folder and file URLs | `SOURCE_FILES` and `*_FOLDER` in each ingestion notebook | none | File IDs are stable; see [bronze-ingestion-guide.md](bronze-ingestion-guide.md) |
| `YEARS_TO_RUN` | `03_ingest_dot` | `"all"` | Or a list such as `["2023"]` to reload only those years |
| Seed CSV paths | `SEED_RELATIVE_PATH` in Silver and Gold notebooks | `resources/seeds/...` | Set `SEED_PATH_OVERRIDE` (for example a Volume path) only when the repository files are not available |
| DQ thresholds and expected lists | Configuration cell of each Silver, Gold and Analytics notebook | none | Documented in [data-quality-rules.md](data-quality-rules.md) section 5 |
| `alert_email` | Bundle variable (`databricks.yml`) | none, required | Receives failure emails; passed with `--var` or from GitHub |
| `dashboard_id` | Bundle variable (`databricks.yml`) | The shared PROVINSIGHTS DASHBOARD | Change only if the dashboard is replaced (new ID), in a PR |
| `warehouse_id` | Bundle variable (`databricks.yml`) | The SQL warehouse used by the dashboard | Runs the dashboard queries during `refresh_dashboard` |

## 3. Run the full pipeline

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

## 4. Run part of the pipeline

### Rerun after a failure

In Databricks, open the failed run and click **Repair run**. It reruns the failed task and everything after it, and skips the tasks that already succeeded. Fix the cause first (section 6).

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

## 5. Check that a run succeeded

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

## 6. When something fails

Start with the failed task's output in the job run. The last cell usually names the check or error. Then find the matching row below.

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| A Silver, Gold or Analytics task fails with a BLOCK check | The data breaks a correctness rule: duplicate key, unmapped label, totals that don't reconcile, a value changed between layers | Run the failed-checks query. `sample_keys` shows the rows. Fix the cause (usually a seed or an upstream table), then **Repair run**. Never weaken a BLOCK check to get past it. Downgrading one needs a decision-log entry. |
| Run is `SUCCESS_WITH_REVIEW` | Something unusual, such as a large year-over-year jump | If it's in the known exceptions register, nothing to do. If it's new, raise it with the team and record the outcome in the [decision log](project-decision-log.md). |
| An Analytics notebook stops with "No DQ-ANL ID for check ..." | A new or renamed check has no documented ID | Add it to `DQ_ID_BUILD` (build) or match a prefix in `DQ_ID_RULES` (validation), and list it in [data-quality-rules.md](data-quality-rules.md) section 6.7. Tables from earlier phases of that run may already be replaced, so rerun the build in full. |
| `01_silver_geography` fails on crosswalk coverage | A DOT or PSA label isn't in the seed, usually a new year or a renamed place | Add the label to the right seed CSV in `resources/seeds/` through a PR (section 8), then rerun from Silver. |
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
| CI **Validate repository** fails on a PR | A unit test failed: the job definition, a notebook cell, SQL syntax, a seed file or the docs alignment | The test message names the file, task, cell or seed row. Run the unit tests locally (section 8), fix it, and push. |
| CI **Validate Databricks bundle** fails on a PR | Invalid YAML, a wrong notebook path, or a notebook that isn't on the branch yet | Run `databricks bundle validate -t dev` locally, fix the path, or merge `main` into your branch. |
| Deploy workflow fails at "Check required GitHub configuration" | `DATABRICKS_HOST`, `DATABRICKS_TOKEN` or `DATABRICKS_ALERT_EMAIL` is missing | A repository admin adds it under **Settings → Environments → development**. |

If a BLOCK failure doesn't make sense, don't rerun repeatedly. Ask in the team chat with the `check_id`, `run_id` and `sample_keys`.

## 7. Roll back a table

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

## 8. Common changes

Every change goes through a pull request using the [PR template](../.github/PULL_REQUEST_TEMPLATE.md). CI must pass, and a teammate must review it.

### Run the unit tests before a PR

CI runs these on every push and pull request. Running them first saves a round trip. They need only the repository files, not Databricks.

```bash
python -m pip install -r tests/requirements.txt
python -m unittest discover -s tests/unit -t tests/unit -v
```

What each test covers is in [tests/README.md](../tests/README.md).

### Update a crosswalk seed

1. Edit the CSV in `resources/seeds/` (see [seeds/README.md](../resources/seeds/README.md) for the columns and roles).
2. If the change is a new rule (a new exclusion, a place added to another), add a decision to the [decision log](project-decision-log.md).
3. Run the unit tests. `test_seeds.py` checks columns, keys, roles and PSGC codes.
4. After merge, rerun from `01_silver_geography`, or the matching Silver notebook for PSA and population seeds.
5. Check that the coverage checks pass, and paste the results into the PR.

### Add or change a data-quality check

Follow [data-quality-rules.md section 10](data-quality-rules.md#10-adding-or-changing-a-check). In the Analytics notebooks, also give the check a `DQ-ANL` ID, or the notebook stops when the check runs.

### Add a job task

Add the task to [`resources/jobs/tourism_pipeline.yml`](../resources/jobs/tourism_pipeline.yml) with its `depends_on` and a timeout. Add it to the Tasks table and Run order in [`resources/README.md`](../resources/README.md) too, because `test_job_definition.py` checks that both match the job. Then run `databricks bundle validate` and the unit tests.

### Change the dashboard

Edit the dashboard in place in Databricks and publish. Don't re-import it, because every import creates a new dashboard with a new ID. If it is ever replaced, update `dashboard_id` in `databricks.yml` through a PR. See [dashboard/README.md](../dashboard/README.md).

### Load a new year of source data

1. Put the new file in the right Google Drive folder and add it to `SOURCE_FILES` in the ingestion notebook.
2. For DOT, set `YEARS_TO_RUN` to the new year to load only that year.
3. Expect `01_silver_geography` to fail on coverage if the new file prints labels the seeds don't know. Add them as described above.
4. Check the year range in the Configuration cells of the Silver, Gold and Analytics notebooks. The current build covers 2019-2024. The business questions use 2019-2023 as the trend and 2023 as the analysis year (DL-031), and the supporting recovery tables use 2019 as the baseline (DL-004).
5. Moving the analysis year (for example to 2024) changes the leading destinations, medians and province groups. Record it in the decision log and update [business-and-analytical-questions.md](business-and-analytical-questions.md) and the dashboard text.
6. Run the full pipeline, then update the run evidence documents.
