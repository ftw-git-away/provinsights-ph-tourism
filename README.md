# ProvInsights

[![CI](https://github.com/ftw-git-away/provinsights-ph-tourism/actions/workflows/ci.yml/badge.svg)](https://github.com/ftw-git-away/provinsights-ph-tourism/actions/workflows/ci.yml)

**Philippine Province-Level Tourism, Recovery, and Economic Analytics Project**

ProvInsights is GitAway's FTW Batch 12 LT3 capstone. It brings together Department of Tourism (DOT), Philippine Statistics Authority (PSA), and Philippine Standard Geographic Code (PSGC) data to examine provincial tourism activity, recovery relative to 2019, and associations with local economic conditions.

**Tourism activity means reported overnight travelers.** It is not a count of unique people or all visitors. Accommodation and food service GVA is an economic proxy that includes spending unrelated to tourism. Findings support descriptive comparisons and further investigation, not causal or investment-return claims.

The [Bronze ingestion guide](docs/bronze-ingestion-guide.md) describes workspace work and the shared control pattern.

## Analytical scope

The canonical questions and definitions are in [docs/business-and-analytical-questions.md](docs/business-and-analytical-questions.md).

1. Distribution of tourism activity: provincial volume, concentration, population-adjusted intensity, and traveler composition.
2. Post-pandemic change: 2022–2023 compared with 2019, including traveler-type recovery and potential emerging destinations.
3. Tourism and local economic conditions: traveler intensity versus GDP per capita, traveler change versus accommodation and food service GVA growth, and economic shares.

The common analytical window is **2019–2023**. The DOT notebook also lands 2024 source data; ingestion coverage does not extend the finalized analytical scope.

Before comparable results are published, the team must resolve historical PSGC mapping, province/HUC/NCR treatment, annual population denominators, missing-data rules, reporting breaks such as Aklan/Boracay, and screening thresholds. Missing or unavailable values must not be interpreted as zero.

## Data sources

| Source | Role |
| --- | --- |
| DOT overnight-traveler reports — DS_05 | Provincial tourism activity and recovery, after source extraction and geographic validation |
| PSA population sources | Population denominators, subject to the approved annual method |
| PSA provincial GDP, GDP per capita, and accommodation/food service GVA — DS_27–DS_32 | Economic comparisons; current prices for shares and constant prices for growth |
| PSGC — DS_33 and DS_34 | Geographic reference and historical crosswalk input |
| PSA tourism satellite accounts and regional tables | National context and cross-checks, not interchangeable with provincial tourism measures |

See [Source assessment](docs/consolidated-data-sources.md) and the [Source inventory](https://docs.google.com/spreadsheets/d/18tTQHJLcJrIFVfNzgvT97ZMM6PfJNnAL/edit) for source identifiers and limitations.

## Processing approach

The intended flow is:

```text
Government source files in Google Drive
    → Databricks Bronze ingestion and provenance
    → Silver normalization and quality rules
    → Gold analytical models
    → Analytics and dashboard
```

## Repository guide

```text
.github/
  PULL_REQUEST_TEMPLATE.md
  workflows/
    ci.yml
docs/
  business-and-analytical-questions.md
  consolidated-data-sources.md
  bronze-ingestion-guide.md
  project-decision-log.md
  data-sources.md
  architecture.md                 # placeholder
  runbook.md                      # placeholder
notebooks/
  01_ingestion/
    02_ingest_psgc.ipynb
    03_ingest_dot.ipynb
  README.md
resources/
  jobs/
    tourism_pipeline.yml          # placeholder on main
src/
  01-ingestion/                   # folder guidance
  02-bronze/
  03-silver/
  04-gold/
  05-analytics/
  06-data-quality/
tests/
  README.md                       # validation guidance
dashboard/
  README.md                       # dashboard guidance
```

Stage folders under `src/` currently contain guidance, not implemented transformation code. Planned paths described in other documents may differ from the files currently committed.

## Team workflow

1. Link work to an issue and state its acceptance criteria.
2. Make a focused change on a branch.
3. Open a PR using the [PR template](.github/PULL_REQUEST_TEMPLATE.md), explaining behavior, source or schema changes, and validation evidence.
4. Request a teammate review and address findings before merging.
5. Update relevant documentation when implementation or decisions change.

Use [Business and analytical questions](docs/business-and-analytical-questions.md) for analytical scope, [Source assessment](docs/consolidated-data-sources.md) for source caveats, [Decision log](docs/project-decision-log.md) for approved choices, and [Bronze guide](docs/bronze-ingestion-guide.md) for ingestion responsibilities. Preserve original source artifacts and keep credentials out of Git.

CI checks repository structure, Python files under `src/`, notebook structure, and syntax in explicitly marked Python/SQL cells. It does not execute Databricks ingestion, validate source data, or currently validate a Databricks bundle.
## Team and handoff

**GitAway — FTW Batch 12 LT3:** Cole, Nella, Cha, Gab, and Haze.

Use the GitHub Project and issues for assignments and checkpoints. The repository is **Not yet ready** for independent engineering handoff: shared setup and PSA ingestion must be merged, complete run instructions are needed, and downstream models and analytics remain to be implemented.
