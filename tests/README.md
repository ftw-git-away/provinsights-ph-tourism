# Tests and Validation

Tests and validation check that the pipeline's data is correct and follows the project's rules. There are two kinds:

| Kind | Where it runs | What it needs | When |
| --- | --- | --- | --- |
| **Unit tests** (`tests/unit/`) | GitHub Actions (CI) | Repository files only: no Databricks, no network | Every push and pull request |
| **Data-quality checks** (in the pipeline notebooks) | Databricks job `tourism_pipeline` | The tables in `tuklas_dev` | Every pipeline run |

## Unit tests (`tests/unit/`)

| File | Checks | What it covers |
| --- | --- | --- |
| `test_job_definition.py` | YAML | `resources/jobs/tourism_pipeline.yml`: unique task keys, every notebook path exists, every `depends_on` points to a real task, no cycles, each layer (by notebook folder) starts only after every task of the previous layer, every task has a timeout, retries only on `ingest_*` tasks, failure emails and one run at a time; the Tasks table and Run order diagram in `resources/README.md` list the same tasks as the job |
| `test_notebook_python.py` | Python | Every notebook is valid JSON with valid cell types and a markdown cell; every Python cell compiles (including notebooks without a `%python` magic); `CATALOG` is `tuklas_dev`; no tokens or passwords; every `dq(...)` call uses a documented severity (`BLOCK`, `REVIEW`, `LOG`), passed by position or as `severity=` |
| `test_notebook_sql.py` | SQL | Every `%sql` cell and every `spark.sql("...")` literal parses as Databricks SQL (`sqlglot`) |
| `test_seeds.py` | CSV data | The four seeds in `resources/seeds/`: row counts and columns, unique keys, allowed `row_role` values, 10-digit PSGC codes, every unit code (and every HUC's `from_unit_psgc_code`) is one of the 100 reporting units, coordinates inside the Philippines, DOT validity years in order |
| `test_docs_alignment.py` | Docs | Silver, Gold and Analytics checks match both ways: every check ID used in a layer's notebooks is a row in section 6 of `docs/data-quality-rules.md`, and every row there is used by a notebook of the same layer. Silver IDs come from `dq("ID", ...)` calls; Gold and Analytics IDs from string literals that are exactly an ID (they also pass IDs through helpers and lookup tables such as `DQ_ID_BUILD`). Mentions in markdown or comments do not count |

Run them locally (versions are pinned in `tests/requirements.txt`, the same file CI uses):

```bash
python -m pip install -r tests/requirements.txt
python -m unittest discover -s tests/unit -t tests/unit -v
```

**Limits of the static checks**

- `spark.sql(variable)` calls are not checked, because the SQL is only known at run time. Only string and f-string literals are parsed.
- Statements that `sqlglot` cannot model (currently only `SHOW`) are allowed through unparsed. Any other statement it cannot parse fails the test.
- A check ID built at run time (for example `f"DQ-GLD-{n:02d}"`) is not seen by `test_docs_alignment.py`. Write IDs as plain strings.

When a test fails, the message names the file, task, cell or seed row. Fix the code, or, if the change is intended (for example a new task or seed row), update the test and the matching README in the same pull request.

## Data-quality checks by layer

A problem should be caught as close as possible to where it is introduced, so each layer checks its own output.

| Layer | What is checked | Where |
| --- | --- | --- |
| Ingestion | Source file found, extraction reconciles with printed totals, required metadata | Ingestion notebooks (`notebooks/01_ingestion_bronze/`) |
| Bronze | Every file's status (`INGESTED`, `SKIPPED`, `FAILED`), technical failures and required source-lineage metadata | Ingestion-control tables written by the ingestion notebooks ([guide](../docs/bronze-ingestion-guide.md)) |
| Silver | Data types, required fields, crosswalk matches, one row per unit and year | `DQ-COM-*`, `DQ-DOT-*`, `DQ-PSA-*`, `DQ-POP-*` checks in each Silver notebook ([rules](../docs/data-quality-rules.md)) |
| Gold | Table grain, keys, joins, measures | `DQ-GLD-*` checks in each Gold notebook, summarised by `gold_run_evidence` ([evidence](../docs/gold-run-evidence.md)) |
| Analytics | Metrics, calculations, expected outputs | `notebooks/04_analytics/02_analytics_validation`, summarised by `analytics_run_evidence` ([evidence](../docs/analytics-run-evidence.md)) |

Every check writes one row to `tuklas_dev.06_data_quality.dq_results` with its ID, severity and status. A failed `BLOCK` check fails its task, and the job skips every task after it, so bad data never reaches the next layer.

| Severity | When it fails |
| --- | --- |
| `BLOCK` | The task fails and the pipeline stops |
| `REVIEW` | The run continues; the result must be reviewed |
| `LOG` | Recorded for information only |

### Important behaviour and where it is covered

| Behaviour | Covered by |
| --- | --- |
| Schema and data types | Types set when each table is built; `DQ-COM` checks in Silver |
| Required fields, null or invalid values | Silver `DQ-*` checks (e.g. `DQ-COM-06`, `DQ-COM-07`) |
| Primary/business keys, duplicates | One row per unit and year (`DQ-COM-03`); unique seed keys (`test_seeds.py`) |
| Source-to-target mappings | Seed crosswalks checked by `test_seeds.py`; new or renamed source labels fail `DQ-DOT-03`, `DQ-PSA-01`, `DQ-POP-01/02`; mapping documented in [`docs/schema-and-source-to-target-mapping.md`](../docs/schema-and-source-to-target-mapping.md) |
| Geographic relationships | PSGC units and crosswalks (`DQ-GEO-*`, `DQ-XW-*`); unit codes and coordinates in `test_seeds.py` |
| Time periods | Seed validity years (`test_seeds.py`); year checks in each Silver notebook |
| Business rules | Silver checks per source; Gold `DQ-GLD-*`; analytics validation |
| Rerun / idempotency | Silver notebooks overwrite each whole table (`write_silver`), so a rerun gives the same result. Not tested automatically yet |
| Final analytical outputs | `02_analytics_validation` and `analytics_run_evidence` |

### Creation and validation

Checks run inside the notebook that builds the table, just before it is written, so a bad table is never saved. Their results are kept separate from the data in `dq_results`, and each check is documented with its ID, so it is always clear what was checked and whether it passed.

## Goal

Tests and validation should provide evidence that:

> **The pipeline ran, the data has the expected structure and quality, and the resulting outputs can be trusted for the project's intended use.**
