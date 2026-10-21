# ProvInsights Documentation

Every ProvInsights document, split by reader. **Business readers** (planners, reviewers, the panel) need only Part A. **Technical readers** (whoever runs, maintains or extends the pipeline) start with Part B. New to the project? Read the [README](../README.md) first.

## Part A. For business readers

What question ProvInsights answers, what the data can and cannot say, and what the dashboard shows. No code or table names needed.

| Document | What it covers |
| --- | --- |
| [Business and analytical questions](business-and-analytical-questions.md) | The problem, the business question, AQ1 to AQ4, the data at a glance, definitions, province groups, scope and caveats |
| [Data sources](consolidated-data-sources.md) | Which government sources are used, what each one feeds, known source problems and how they were handled |
| [Dashboard evidence](dashboard-evidence.md) | Each dashboard page, with screenshots and the numbers it shows |
| [Decision log](project-decision-log.md) | Every approved decision (DL-001 onwards), with the pull request that approved it, and the open issues |

## Part B. For technical readers

### B1. Understand how it is built

| Document | What it covers |
| --- | --- |
| [Architecture](architecture.md) | Components, data flow, data quality, orchestration, CI/CD, design decisions and limitations |
| [Architecture diagram](architecture.png) | The pipeline on one page |
| [Bronze ingestion guide](bronze-ingestion-guide.md) | Google Drive folders and file IDs, the ingestion notebooks, control tables and run checks |
| [Schema and source-to-target mapping](schema-and-source-to-target-mapping.md) | The Gold star schema, how each source maps to it, and how Analytics and the dashboard profile are calculated |
| [Data dictionary](data-dictionary.md) | Every table and column, from ingestion to the dashboard |

### B2. Set it up, run it, change it

Each task has its own document, so a reader only reads the part they need.

| When you need to… | Read | Audience |
| --- | --- | --- |
| Set ProvInsights up once (new workspace or handoff), grant access, configure | [Setup and handoff](setup-and-handoff.md) | New owner, administrator |
| Run the pipeline, check a run, fix a failure, roll back | [Runbook](runbook.md) | Operator, day to day |
| Change a seed, a check, a job task, the dashboard, or load a new year | [Making changes](making-changes.md) | Developer |
| Look up job tasks, order and settings | [`resources/README.md`](../resources/README.md) | Developer |
| Look up the seed files | [`resources/seeds/README.md`](../resources/seeds/README.md) | Developer |
| Find a notebook | [`notebooks/README.md`](../notebooks/README.md) | Developer |
| Open, refresh or edit the dashboard | [`dashboard/README.md`](../dashboard/README.md) | Developer |
| Configure CI and CD | [`.github/workflows/README.md`](../.github/workflows/README.md) | Administrator |

### B3. Quality and evidence

| Document | What it covers |
| --- | --- |
| [Data-quality rules](data-quality-rules.md) | BLOCK and REVIEW severities, every check ID by layer, and the known-exceptions register |
| [`tests/README.md`](../tests/README.md) | What the unit tests in CI check, and what is checked inside the pipeline instead |
| [Pipeline and CI/CD evidence](pipeline-evidence.md) | Full run of all 19 job tasks, task dependencies, the CI and CD workflows, and screenshots in [`images/`](images/) |
| [Gold run evidence](gold-run-evidence.md) | Results of the latest Gold run |
| [Analytics run evidence](analytics-run-evidence.md) | Results of the latest Analytics build and validation |

## Conventions

- Decisions are cited as `DL-XXX` and open issues as `OI-X`, both in the [decision log](project-decision-log.md). Check IDs (`DQ-...`) are in the [data-quality rules](data-quality-rules.md).
- When a change affects a definition, a table or a check, update the matching document in the same pull request.
