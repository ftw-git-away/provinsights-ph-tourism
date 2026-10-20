# Tests and Validation

Tests and validation check that the pipeline's data is correct and follows the project's rules. There are two kinds:

| Kind | Where it runs | What it needs | When |
| --- | --- | --- | --- |
| **Unit tests** (`tests/unit/`) | GitHub Actions (CI) | Repository files only: no Databricks, no network | Every push and pull request |
| **Data-quality checks** (in the pipeline notebooks) | Databricks job `tourism_pipeline` | The tables in `tuklas_dev` | Every pipeline run |

## Unit tests (`tests/unit/`)

| File | Checks | What it covers |
| --- | --- | --- |
| `test_job_definition.py` | YAML | `resources/jobs/tourism_pipeline.yml`: 18 unique tasks, every notebook path exists, every `depends_on` points to a real task, no cycles, setup tasks wait for the whole previous layer, every task has a timeout, retries only on `ingest_*` tasks, failure emails and one run at a time |
| `test_notebook_python.py` | Python | Every notebook has a markdown cell; every Python cell compiles (including notebooks without a `%python` magic); `CATALOG` is `tuklas_dev`; no tokens or passwords; `dq(...)` uses a documented severity (`BLOCK`, `REVIEW`, `LOG`) |
| `test_notebook_sql.py` | SQL | Every `%sql` cell and every `spark.sql("...")` string parses as Databricks SQL (`sqlglot`) |
| `test_seeds.py` | CSV data | The four seeds in `resources/seeds/`: row counts and columns, unique keys, allowed `row_role` values, 10-digit PSGC codes, every unit code is one of the 100 reporting units, coordinates inside the Philippines, DOT validity years in order |
| `test_docs_alignment.py` | Docs | Every DQ check ID used in a Silver notebook is listed in `docs/data-quality-rules.md` |

Run them locally:

```bash
python -m pip install sqlglot pyyaml
python -m unittest discover -s tests/unit -t tests/unit -v
```

When a test fails, the message names the file, task, cell or seed row. Fix the code, or, if the change is intended (for example a new task or seed row), update the test and the matching README in the same pull request.

## Data-quality checks by layer

A problem should be caught as close as possible to where it is introduced, so each layer checks its own output.

| Layer | What is checked | Where |
| --- | --- | --- |
| Ingestion | Source file found, extraction reconciles with printed totals, required metadata | Ingestion notebooks (`notebooks/01_ingestion/`) |
| Bronze | Schema, record counts, duplicates, source tracking | Written during ingestion; `01_bronze_validation` is a draft |
| Silver | Data types, required fields, crosswalk matches, one row per unit and year | `DQ-COM-*`, `DQ-DOT-*`, `DQ-PSA-*`, `DQ-POP-*` checks in each Silver notebook ([rules](../docs/data-quality-rules.md)) |
| Gold | Table grain, keys, joins, measures | `DQ-GLD-*` checks in each Gold notebook, summarised by `gold_run_evidence` ([evidence](../docs/gold-run-evidence.md)) |
| Analytics | Metrics, calculations, expected outputs | `05_analytics/02_analytics_validation`, summarised by `analytics_run_evidence` ([evidence](../docs/analytics-run-evidence.md)) |

Every check writes one row to `tuklas_dev.06_data_quality.dq_results` with its ID, severity and status. A failed `BLOCK` check fails its task, and the job skips every task after it, so bad data never reaches the next layer.

| Severity | When it fails |
| --- | --- |
| `BLOCK` | The task fails and the pipeline stops |
| `REVIEW` | The run continues; the result must be reviewed |
| `LOG` | Recorded for information only |

### Creation and validation

Checks run inside the notebook that builds the table, just before it is written, so a bad table is never saved. Their results are kept separate from the data in `dq_results`, and each check is documented with its ID, so it is always clear what was checked and whether it passed.

## Not yet in place

- **Consolidated end-to-end quality gate:** one final task that confirms every critical check passed for the run. The framework is still to be chosen.
- **Gold rules document:** Gold checks (`DQ-GLD-*`) are listed in the run evidence, not in a rules document like `docs/data-quality-rules.md`.
- **Bronze validation:** `01_bronze_validation` is still a draft.

## Goal

Tests and validation should provide evidence that:

> **The pipeline ran, the data has the expected structure and quality, and the resulting outputs can be trusted for the project's intended use.**
