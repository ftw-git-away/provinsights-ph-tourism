# Making Changes to ProvInsights

**Audience:** a developer adding a feature (Part 1) or an owner keeping the system current (Part 2: a new year of data, tokens, versions). Running and checking the pipeline is in the [runbook](runbook.md); one-time setup is in [setup and handoff](setup-and-handoff.md).

Every change goes through a pull request using the [PR template](../.github/PULL_REQUEST_TEMPLATE.md). CI must pass, and a teammate must review it.

## Contents

**Part 1. New features**
- [Run the unit tests before a PR](#run-the-unit-tests-before-a-pr)
- [Update a crosswalk seed](#update-a-crosswalk-seed)
- [Add or change a data-quality check](#add-or-change-a-data-quality-check)
- [Add a job task](#add-a-job-task)
- [Change the dashboard](#change-the-dashboard)

**Part 2. System updates**
- [Load a new year of source data](#load-a-new-year-of-source-data)
- [Renew the Databricks tokens](#renew-the-databricks-tokens)
- [Update tool and library versions](#update-tool-and-library-versions)
- [Replace the dashboard or SQL warehouse](#replace-the-dashboard-or-sql-warehouse)
- [Re-authorize the Google Drive connection](#re-authorize-the-google-drive-connection)

# Part 1. New features

## Run the unit tests before a PR

CI runs these on every push and pull request. Running them first saves a round trip. They need only the repository files, not Databricks.

```bash
python -m pip install -r tests/requirements.txt
python -m unittest discover -s tests/unit -t tests/unit -v
```

What each test covers is in [tests/README.md](../tests/README.md).

## Update a crosswalk seed

1. Edit the CSV in `resources/seeds/` (see [seeds/README.md](../resources/seeds/README.md) for the columns and roles).
2. If the change is a new rule (a new exclusion, a place added to another), add a decision to the [decision log](project-decision-log.md).
3. Run the unit tests. `test_seeds.py` checks columns, keys, roles and PSGC codes.
4. After merge, wait for the CD deploy to finish, then rerun from `01_silver_geography`, or the matching Silver notebook for PSA and population seeds.
5. Check that the coverage checks pass, and post the `dq_results` rows (or a screenshot) as a comment on the merged PR, so the review trail stays in one place.

## Add or change a data-quality check

Follow [data-quality-rules.md section 10](data-quality-rules.md#10-adding-or-changing-a-check). In the Analytics notebooks, also give the check a `DQ-ANL` ID, or the notebook stops when the check runs.

## Add a job task

Add the task to [`resources/jobs/tourism_pipeline.yml`](../resources/jobs/tourism_pipeline.yml) with its `depends_on` and a timeout. Add it to the Tasks table and Run order in [`resources/README.md`](../resources/README.md) too, because `test_job_definition.py` checks that both match the job. Then run `databricks bundle validate` and the unit tests.

## Change the dashboard

1. Edit the shared dashboard in place in Databricks and publish. Don't re-import it for routine edits: every import creates a new dashboard with a new ID.
2. Save the change back to the repository so `dashboard/` stays current: **⋮ → Export dashboard**, save it as `dashboard/provinsights.lvdash.json`, and if a query changed, update the matching file in `dashboard/datasets/`.
3. Run `python dashboard/tools/build_lvdash.py --check`, then open a PR with the JSON and SQL.

Re-import only to recover a broken dashboard or to set one up (see [setup and handoff](setup-and-handoff.md#15-create-the-dashboard-and-set-the-bundle-variables)), then update `dashboard_id` in `databricks.yml` through a PR. Details: [dashboard/README.md](../dashboard/README.md).
# Part 2. System updates

## Load a new year of source data

1. Put the new file in the right Google Drive folder and add it to `SOURCE_FILES` in the ingestion notebook.
2. For DOT, set `YEARS_TO_RUN` to the new year to load only that year.
3. Check the year range in the Configuration cells of the Silver, Gold and Analytics notebooks. The current build covers 2019-2024. The business questions use 2019-2023 as the trend and 2023 as the analysis year (DL-031), and the supporting recovery tables use 2019 as the baseline (DL-004).
4. Open a PR with these changes, get it reviewed and merged, and wait for the CD deploy to finish. A run before the deploy uses the old notebooks.
5. Run the full pipeline ([runbook, section 1](runbook.md#1-run-the-full-pipeline)). Expect `01_silver_geography` to fail on coverage if the new file prints labels the seeds don't know: add them ([update a crosswalk seed](#update-a-crosswalk-seed)) and rerun.
6. Set `YEARS_TO_RUN` back to `"all"` in a follow-up PR. If it stays as one year, a fresh setup in a new workspace would load only that year.
7. Moving the analysis year (for example to 2024) changes the leading destinations, medians and province groups. Record it in the decision log and update [business-and-analytical-questions.md](business-and-analytical-questions.md) and the dashboard text.
8. Update the run evidence documents.

## Renew the Databricks tokens

Both GitHub environments use a Databricks personal access token. The deploy token (`development`) expires on **2027-01-02** and the CI token (`ci-validate`) on **2027-01-23** ([pipeline evidence](pipeline-evidence.md#5-configuration-and-secrets)). Renew both before the first date.

1. In Databricks, **Settings → Developer → Access tokens → Generate new token**. Use a deploy-capable account for `development` and a validate-only identity for `ci-validate`.
2. In GitHub, **Settings → Environments → development** (then **ci-validate**), replace `DATABRICKS_TOKEN`.
3. Check it: run **Actions → CD - Deploy ProvInsights PH to Databricks → Run workflow** (without `run_pipeline`), and re-run CI on any open PR. Both should pass the "Validate bundle" step.
4. Revoke the old tokens in Databricks, and note the new expiry dates in [pipeline-evidence.md](pipeline-evidence.md#5-configuration-and-secrets).

## Update tool and library versions

| What | Where | After changing |
| --- | --- | --- |
| Databricks CLI (1.19.0) | `.github/workflows/ci.yml`, `deploy.yml` | CI and a manual CD run pass |
| Test libraries (`sqlglot`, `pyyaml`) | `tests/requirements.txt` | Unit tests pass locally and in CI |
| Notebook libraries (`openpyxl`, `pdfplumber`) | `%pip install` cells in the ingestion notebooks | A full pipeline run succeeds |

Change one thing per PR, so a failure points to one cause.

## Replace the dashboard or SQL warehouse

If the dashboard is recreated or the warehouse changes, update `dashboard_id` or `warehouse_id` in `databricks.yml` through a PR, and give the job's run-as identity **Can Run** on the new dashboard. The next run's `refresh_dashboard` task confirms it.

## Re-authorize the Google Drive connection

The `capstone_gdrive` connection signs in with one person's Google account. If that account changes or loses access, re-create or re-authorize the connection and reshare the folders ([setup and handoff, 1.3 and 1.8](setup-and-handoff.md#13-create-the-google-drive-connection)). Check it by running the folder-listing cell of `03_ingest_dot`.
