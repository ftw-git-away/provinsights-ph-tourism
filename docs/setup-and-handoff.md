# ProvInsights Setup and Handoff

**Audience:** a new owner or administrator setting ProvInsights up once, in a new workspace or after a handoff. For day-to-day runs see the [runbook](runbook.md); for changing the pipeline see [making changes](making-changes.md).

## Contents

1. [Hand-off: set up in a new workspace](#1-hand-off-set-up-in-a-new-workspace)
2. [Access and tools](#2-access-and-tools)
3. [Configuration reference](#3-configuration-reference)

---

## 1. Hand-off: set up in a new workspace

Do this once, when ProvInsights is handed to a new owner or moved to a workspace where it has never run. Steps 1.1 to 1.7 set it up; 1.8 lists what to transfer from the current team. In the current workspace everything below already exists, so you only need the [runbook](runbook.md).

The version being handed over is the `v1.0-handoff` tag on `main`. Start from that tag, not from a later commit, and confirm the commit with `git rev-parse v1.0-handoff^{commit}`. The commit SHA is also on the [`v1.0-handoff` release page](https://github.com/ftw-git-away/provinsights-ph-tourism/releases/tag/v1.0-handoff).

### 1.1 What the new workspace needs

- A Databricks workspace with Unity Catalog and serverless compute for notebooks and jobs
- A SQL warehouse (serverless is fine) for the dashboard refresh
- A Google account that can read the three source folders listed in the [Bronze ingestion guide](bronze-ingestion-guide.md#source-access)
- Admin access to the GitHub repository, to set the environments in 1.6

### 1.2 Create the catalog and the two ingestion schemas

The notebooks use the catalog name `tuklas_dev`. The setup tasks create `03_silver`, `04_gold`, `05_analytics` and `06_data_quality`, but `00_ingestion_setup` only checks that `01_ingestion` exists and stops if it doesn't, and the ingestion notebooks write to `02_bronze` without creating it. Run this once in a SQL editor:

```sql
CREATE CATALOG IF NOT EXISTS tuklas_dev;
CREATE SCHEMA IF NOT EXISTS tuklas_dev.`01_ingestion`;
CREATE SCHEMA IF NOT EXISTS tuklas_dev.`02_bronze`;
```

Then give the team `USE CATALOG`, `CREATE SCHEMA` and write access on `tuklas_dev` (section 2, "Access you need").

To use a different catalog name, change `CATALOG = "tuklas_dev"` at the top of every notebook and the catalog set on every dashboard dataset, in one pull request.

### 1.3 Create the Google Drive connection

1. In **Catalog Explorer → External data → Connections**, create a Google Drive connection named exactly **`capstone_gdrive`** and sign in with the Google account from 1.1. The name is hard-coded in the ingestion notebooks.
2. Grant the people and the job's run-as user permission to use the connection.
3. Check it: open `03_ingest_dot`, run the cells up to the folder listing, and confirm it lists the six DOT PDFs.

No keys or tokens go into the notebooks or the repository. Access is controlled only through this connection.

### 1.4 Check the source files

The notebooks find each file by its Google Drive file ID (`SOURCE_FILES` and `*_FOLDER` at the top of each ingestion notebook). If the files are copied to new folders, the IDs change: update those settings in a pull request. File names and dataset IDs must follow the [naming convention](bronze-ingestion-guide.md#file-naming).

### 1.5 Create the dashboard and set the bundle variables

1. Import the dashboard: **Dashboards → Create dashboard → ⋮ → Import dashboard from file**, using `dashboard/provinsights.lvdash.json`. Set each dataset's catalog and schema to `tuklas_dev.05_analytics` if they aren't set.
2. Publish it with the SQL warehouse from 1.1, and give the job's run-as user at least **Can Run** on it.
3. Copy the dashboard ID (from its URL) and the warehouse ID (**SQL Warehouses → Connection details**), and set them as the defaults of `dashboard_id` and `warehouse_id` in `databricks.yml` in a pull request.

The dashboard shows no data until the first pipeline run finishes in 1.7.

### 1.6 Set up GitHub

Create the two GitHub environments, `development` (deployment branch `main` only) and `ci-validate`, each with `DATABRICKS_HOST`, `DATABRICKS_TOKEN` and `DATABRICKS_ALERT_EMAIL`. The values, and why there are two environments, are in [`.github/workflows/README.md`](../.github/workflows/README.md#required-github-configuration). Use a validate-only token for `ci-validate`.

### 1.7 First deploy and run

1. Merge the pull requests from 1.4 and 1.5, or run **Actions → CD - Deploy ProvInsights PH to Databricks → Run workflow**. This deploys the job and the seed files.
2. Run the pipeline with **run_pipeline** ticked, or with Option A or B in the [runbook, section 1](runbook.md#1-run-the-full-pipeline). The setup tasks create the remaining schemas and control tables on the first run.
3. Check the run with the [runbook, section 3](runbook.md#3-check-that-a-run-succeeded). On the current sources, a complete run gives 100 units, 600 fact rows and 958 Analytics rows, with no BLOCK failures.
4. Open the dashboard and compare the test units in [`dashboard/README.md`](../dashboard/README.md#test-unit-reconciliation).

### 1.8 What to transfer

These are tied to a person on the current team, so they don't move with the repository. Transfer or replace each one before the team's access ends.

| Item | Why it matters | What to do |
| --- | --- | --- |
| `capstone_gdrive` connection | It signs in with one person's Google account. If that account loses access, ingestion fails. | Re-create or re-authorize it with the new owner's Google account (1.3), and transfer ownership of the connection in Unity Catalog. |
| Google Drive source folders | The connection can only read folders shared with its account. | Share the three folders with the new owner, or copy them and update the file IDs (1.4). |
| Shared dashboard | Owned by the person who created it, and published with their credentials. | Transfer ownership to the new owner and republish. Check that `dashboard_id` in `databricks.yml` is unchanged. |
| Databricks job | Runs as the person who last deployed it. | Redeploy from the new owner's account (1.7), so the job runs as them. |
| GitHub tokens | `DATABRICKS_TOKEN` in both GitHub environments is a personal access token. | Create new tokens from the new owner's account, update both environments (1.6), and revoke the old tokens. |
| Failure emails | Go to the address in `DATABRICKS_ALERT_EMAIL`. | Change it to the new owner's address. |
| Repository access | Reviews and merges need write access. | Add the new owners on GitHub and keep `main` protected. |

## 2. Access and tools

### Access you need

| Need | For | How to check |
| --- | --- | --- |
| Databricks workspace account | Everything | You can open the workspace |
| `USE CATALOG`, `CREATE SCHEMA` and write access on `tuklas_dev` | Creating and replacing tables | `SHOW SCHEMAS IN tuklas_dev` works and lists `01_ingestion` to `06_data_quality` |
| Use of the Unity Catalog connection `capstone_gdrive` | Reading source files from Google Drive | The folder listing cell in any ingestion notebook returns files |
| Read access to the three Google Drive source folders (PSA, PSGC, DOT) | Ingestion | Same as above |
| **Can Run** on the shared dashboard and use of the SQL warehouse | The `refresh_dashboard` task | See [dashboard/README.md](../dashboard/README.md) |
| GitHub write access to the repository | Pull requests, running the deploy workflow | You can open a PR |

### Tools (only for running from your computer)

- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/) (the deploy workflow pins version 1.19.0)
- Git
- Python 3.12, only for the unit tests ([making changes](making-changes.md#run-the-unit-tests-before-a-pr))

The notebooks install their own libraries (`openpyxl`, `pdfplumber`) with `%pip install` when they run on Databricks.

### One-time setup for local runs

```bash
git clone https://github.com/ftw-git-away/provinsights-ph-tourism.git
cd provinsights-ph-tourism

# sign in once and save a profile
databricks auth login --host <workspace URL> --profile <profile>
```

Never commit the workspace URL, a token or an email address. The bundle takes the alert email as a variable, and GitHub Actions reads the URL and token from the `development` environment settings.

## 3. Configuration reference

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
