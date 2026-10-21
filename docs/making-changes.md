# Making Changes to ProvInsights

**Audience:** a developer changing the pipeline: seeds, checks, job tasks, the dashboard, or a new year of data. Running and checking the pipeline is in the [runbook](runbook.md); one-time setup is in [setup and handoff](setup-and-handoff.md).

Every change goes through a pull request using the [PR template](../.github/PULL_REQUEST_TEMPLATE.md). CI must pass, and a teammate must review it.

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
4. After merge, rerun from `01_silver_geography`, or the matching Silver notebook for PSA and population seeds.
5. Check that the coverage checks pass, and paste the results into the PR.

## Add or change a data-quality check

Follow [data-quality-rules.md section 10](data-quality-rules.md#10-adding-or-changing-a-check). In the Analytics notebooks, also give the check a `DQ-ANL` ID, or the notebook stops when the check runs.

## Add a job task

Add the task to [`resources/jobs/tourism_pipeline.yml`](../resources/jobs/tourism_pipeline.yml) with its `depends_on` and a timeout. Add it to the Tasks table and Run order in [`resources/README.md`](../resources/README.md) too, because `test_job_definition.py` checks that both match the job. Then run `databricks bundle validate` and the unit tests.

## Change the dashboard

Edit the dashboard in place in Databricks and publish. Don't re-import it, because every import creates a new dashboard with a new ID. If it is ever replaced, update `dashboard_id` in `databricks.yml` through a PR. See [dashboard/README.md](../dashboard/README.md).

## Load a new year of source data

1. Put the new file in the right Google Drive folder and add it to `SOURCE_FILES` in the ingestion notebook.
2. For DOT, set `YEARS_TO_RUN` to the new year to load only that year.
3. Expect `01_silver_geography` to fail on coverage if the new file prints labels the seeds don't know. Add them as described above.
4. Check the year range in the Configuration cells of the Silver, Gold and Analytics notebooks. The current build covers 2019-2024. The business questions use 2019-2023 as the trend and 2023 as the analysis year (DL-031), and the supporting recovery tables use 2019 as the baseline (DL-004).
5. Moving the analysis year (for example to 2024) changes the leading destinations, medians and province groups. Record it in the decision log and update [business-and-analytical-questions.md](business-and-analytical-questions.md) and the dashboard text.
6. Run the full pipeline, then update the run evidence documents.
