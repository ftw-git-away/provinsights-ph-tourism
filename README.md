# ProvInsights

[![CI](https://github.com/ftw-git-away/provinsights-ph-tourism/actions/workflows/ci.yml/badge.svg)](https://github.com/ftw-git-away/provinsights-ph-tourism/actions/workflows/ci.yml)

**Philippine Province-Level Tourism and Economic Analytics Project**

ProvInsights is GitAway's FTW Batch 12 LT3 capstone. It brings together Department of Tourism (DOT), Philippine Statistics Authority (PSA), and Philippine Standard Geographic Code (PSGC) data to show where tourism is concentrated, how much tourism-related output each province generates per visitor, and which provinces beyond the leading destinations should be prioritized for tourism development.

**Tourism activity means reported overnight travelers.** It is not a count of unique people or all visitors. Accommodation and food services (A&F) GVA is an economic proxy that includes spending unrelated to tourism. Findings support planning priorities and further study, not causal or investment-return claims. A missing value is never treated as zero.

## Analytical scope

> **How can tourism development be planned to benefit provinces beyond the leading tourist destinations?**

The questions, definitions, queries and recommendation framework are in [docs/business-and-analytical-questions.md](docs/business-and-analytical-questions.md).

| Analytical question | What it shows | Analytics tables |
| --- | --- | --- |
| **AQ1:** Where do visitors go? | Concentration of overnight travelers in the 10 leading destinations | `tourism_activity`, `tourism_concentration` |
| **AQ2:** Which provinces earn more from each visitor, and which earn less? | Earnings per visitor and each province's quadrant | `tourism_economy`, `tourism_activity` |
| **AQ3:** Does tourism only do well in already-wealthy provinces? | Tourism share of the economy against GDP per capita | `tourism_economy` |
| **AQ4:** Which provinces beyond the leading destinations should be prioritized, and what do they need? | A recommended action for every province | `tourism_economy`, `tourism_activity` |

Trends cover **2019-2023**, and AQ2 to AQ4 use **2023**, the latest year with both DOT and PSA provincial data. The leading destinations are the 10 provinces with the highest average annual overnight travelers over 2019-2023. Source data in the pipeline covers 2019-2024.

## Data sources

| Source | Role |
| --- | --- |
| DOT overnight-traveler reports | Provincial tourism activity |
| PSA population sources | Population denominators for intensity |
| PSA provincial GDP, GDP per capita, and A&F GVA | Economic comparisons: current prices for shares, constant prices for growth |
| PSGC | Geographic reference and historical crosswalk |

See [Source assessment](docs/consolidated-data-sources.md) for identifiers and limitations.

## How the pipeline works

![ProvInsights architecture](docs/images/architecture.png)

Full description, design decisions and limitations: [docs/architecture.md](docs/architecture.md). How to run, check and fix the pipeline: [docs/runbook.md](docs/runbook.md).

```text
Government source files
    → Ingestion and Bronze      (notebooks/01_ingestion)
    → Silver                    (notebooks/03_silver)
    → Gold                      (notebooks/04_gold)
    → Analytics                 (notebooks/05_analytics)
    → Dashboard
```

- **Silver** cleans each source and maps places to PSGC units. Each Silver notebook runs its own data-quality checks and fails on a BLOCK error.
- **Gold** is a star schema: `dim_province`, `dim_year` and `fact_province_year` (see [schema and source-to-target mapping](docs/schema-and-source-to-target-mapping.md)).
- **Analytics** calculates the business metrics once, in five tables in `05_analytics`. Every row carries the Analytics run ID and the exact Gold Delta versions it was built from.
- **Data quality:** check results are saved in `06_data_quality.dq_results`, and each layer records its runs in a run log (`silver_run_log`, `gold_run_log`, `05_analytics.analytics_run_log`). A BLOCK check protects correctness. A REVIEW check flags something unusual that needs a person to look.

Run evidence: [Gold](docs/gold-run-evidence.md) and [Analytics](docs/analytics-run-evidence.md).

The job in [`resources/jobs/tourism_pipeline.yml`](resources/jobs/tourism_pipeline.yml) runs the layers in dependency order. Task order, settings and how to add a task are in [`resources/README.md`](resources/README.md).

## Repository guide

```text
.github/
  PULL_REQUEST_TEMPLATE.md
  workflows/                      # ci.yml, deploy.yml
docs/
  business-and-analytical-questions.md
  consolidated-data-sources.md
  data-sources.md
  schema-and-source-to-target-mapping.md
  bronze-ingestion-guide.md
  gold-run-evidence.md
  analytics-run-evidence.md
  project-decision-log.md
  architecture.md                 # architecture, design decisions, limitations
  runbook.md                      # how to run, check and fix the pipeline
  images/architecture.png
notebooks/
  01_ingestion/                   # sources to Bronze
  03_silver/
  04_gold/
  05_analytics/                   # build, validation, run evidence
resources/
  jobs/tourism_pipeline.yml       # end-to-end Databricks job
  seeds/                          # reviewed crosswalk files
databricks.yml                    # Databricks bundle
tests/
  README.md                       # validation guidance, no automated tests yet
dashboard/
  README.md                       # placeholder
```

## Databricks deployment

The pipeline is deployed to Databricks as a bundle defined in [`databricks.yml`](databricks.yml). It needs one variable, `alert_email`, which receives failure emails. No workspace URL or token is stored in the repository. GitHub Actions supplies them from the GitHub environments (see [`.github/workflows/README.md`](.github/workflows/README.md)).

**How changes reach Databricks**

1. Open a pull request. CI runs **Validate repository** and **Validate Databricks bundle**.
2. After approval, merge into `main`.
3. The **CD - Deploy ProvInsights PH to Databricks** workflow validates and deploys the bundle. Deploying updates the job but does not run it.

**Working with the bundle locally**

```bash
# sign in once
databricks auth login --host <workspace URL> --profile <profile>

# check the bundle (run before every pull request)
databricks bundle validate -t dev -p <profile> --var="alert_email=<your email>"

# deploy to your own dev folder
databricks bundle deploy -t dev -p <profile> --var="alert_email=<your email>"

# run the pipeline (writes to the shared tuklas_dev catalog; tell the team first)
databricks bundle run -t dev -p <profile> tourism_pipeline --var="alert_email=<your email>"
```

## Team workflow

1. Link work to an issue and state its acceptance criteria.
2. Make a focused change on a branch.
3. Open a PR using the [PR template](.github/PULL_REQUEST_TEMPLATE.md), explaining behavior, source or schema changes, and validation evidence.
4. Request a teammate review and address findings before merging.
5. Update relevant documentation when implementation or decisions change.

Use the [Decision log](docs/project-decision-log.md) for approved choices. Preserve original source artifacts and keep credentials out of Git.

CI checks repository structure, notebook structure, syntax in marked Python and SQL cells, and the Databricks bundle. It does not run the notebooks or validate source data.

## Team and handoff

**GitAway, FTW Batch 12 LT3:** Cole, Nella, Cha, Gab, and Haze.

Use the GitHub Project and issues for assignments and checkpoints.

**Handoff status: partly ready.** The ingestion, Silver, Gold and Analytics notebooks, the job definition, run evidence for Gold and Analytics, the architecture document and the runbook are in the repository. Still missing: automated tests in `tests/` and a dashboard guide.
