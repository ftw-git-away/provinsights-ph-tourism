# ProvInsights Documentation

Every ProvInsights document, grouped by what you need it for. New to the project? Read the [README](../README.md) first, then the business questions and the architecture.

## The question

| Document | What it covers |
| --- | --- |
| [Business and analytical questions](business-and-analytical-questions.md) | The business question, AQ1 to AQ4, definitions, province groups, scope and caveats |
| [Decision log](project-decision-log.md) | Every approved decision (DL-001 onwards), with the pull request that approved it, and the open issues |

## How it is built

| Document | What it covers |
| --- | --- |
| [Architecture](architecture.md) | Components, data flow, data quality, orchestration, CI/CD, design decisions and limitations |
| [Architecture diagram](architecture.png) | The pipeline on one page |
| [Data sources](consolidated-data-sources.md) | The sources used, what each one feeds, known source problems and how they were handled |
| [Bronze ingestion guide](bronze-ingestion-guide.md) | Google Drive folders and file IDs, the ingestion notebooks, control tables and run checks |
| [Schema and source-to-target mapping](schema-and-source-to-target-mapping.md) | The Gold star schema, how each source maps to it, and how Analytics and the dashboard profile are calculated |
| [Data dictionary](data-dictionary.md) | Every table and column, from ingestion to the dashboard |

## How to run it

| Document | What it covers |
| --- | --- |
| [Runbook](runbook.md) | Hand-off and new workspace setup, running the pipeline, checking a run, fixing failures, rolling back, common changes |
| [`resources/README.md`](../resources/README.md) | Job tasks, their order and settings, and how to add a task |
| [`resources/seeds/README.md`](../resources/seeds/README.md) | The reviewed crosswalk and coordinate seed files |
| [`notebooks/README.md`](../notebooks/README.md) | Notebook folders, the schemas they write to, and the notebooks in each |
| [`dashboard/README.md`](../dashboard/README.md) | Opening, refreshing and editing the dashboard; datasets, filters and expected values |
| [`.github/workflows/README.md`](../.github/workflows/README.md) | CI and CD workflows and the GitHub environments they need |

## Quality and evidence

| Document | What it covers |
| --- | --- |
| [Data-quality rules](data-quality-rules.md) | BLOCK and REVIEW severities, every check ID by layer, and the known-exceptions register |
| [`tests/README.md`](../tests/README.md) | What the unit tests in CI check, and what is checked inside the pipeline instead |
| [Pipeline and CI/CD evidence](pipeline-evidence.md) | Full run of all 19 job tasks, task dependencies, the CI and CD workflows, and screenshots in [`images/`](images/) |
| [Gold run evidence](gold-run-evidence.md) | Results of the latest Gold run |
| [Analytics run evidence](analytics-run-evidence.md) | Results of the latest Analytics build and validation |
| [Dashboard evidence](dashboard-evidence.md) | Each dashboard page checked against the Analytics tables, with screenshots in [`images/dashboard/`](images/dashboard/) |

## Conventions

- Decisions are cited as `DL-XXX` and open issues as `OI-X`, both in the [decision log](project-decision-log.md). Check IDs (`DQ-...`) are in the [data-quality rules](data-quality-rules.md).
- When a change affects a definition, a table or a check, update the matching document in the same pull request.
