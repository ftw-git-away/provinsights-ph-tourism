# ProvInsights

[![CI](https://github.com/ftw-git-away/provinsights-ph-tourism/actions/workflows/ci.yml/badge.svg)](https://github.com/ftw-git-away/provinsights-ph-tourism/actions/workflows/ci.yml)

**Province-level tourism and economic analytics to identify destinations beyond the leading tourist destinations that warrant closer attention**

ProvInsights is GitAway's FTW Batch 12 LT3 capstone. It brings together Department of Tourism (DOT), Philippine Statistics Authority (PSA), and Philippine Standard Geographic Code (PSGC) data in one Databricks pipeline, so planners can see where tourism is concentrated, how provinces compare in visitors and tourism-related output per visitor, and which provinces beyond the leading destinations warrant closer attention.

## Problem

**Tourism is one of the country's biggest industries, but its benefits are concentrated in a few places.** In 2023, tourism employed 6.21 million Filipinos and made up 8.6% of GDP (PSA, Philippine Tourism Satellite Account). Yet in 2017, Boracay, an island of only about 10 km², hosted one in three visitors to the country, and in 2018 it had to close for six months to recover from overcrowding and pollution. The pattern continues: in 2023, the 10 leading destinations received **43.7%** of all overnight travelers, while many provinces with beaches, mountains and culture received far fewer.

<p align="center">
  <img width="720" alt="Crowded White Beach in Boracay, Aklan" src="https://github.com/user-attachments/assets/9dbf098e-9f11-4c84-90bc-bc43654ae07c" />
  <br />
  <sub>Boracay, Aklan. Photo: <a href="https://www.rappler.com/culture-desk/travel/boracay-included-world-greatest-places-2022-time-magazine">Rappler</a>.</sub>
</p>

**The DOT has made spreading tourism a national goal.** Its [National Tourism Development Plan (NTDP) 2023-2028](https://www.visitcentralluzon.com/wp-content/uploads/2026/02/DOT-NTDP-23-00043-Department-of-Tourism-National-Tourism-Development-Plan-2023-2028.pdf) sets **Goal 4: Equalization of tourism product development and promotion**, which aims to create opportunities for emerging provinces (Objective 4.1) and link them with key destinations through circuits and joint promotion (Objective 4.2). The plan also calls for product mapping across all regions and provinces (Objective 4.3) and for better tourism data and monitoring (Objectives 2.2 and 4.5).

**But the evidence planners need is scattered.** To act on Goal 4, planners need to know which provinces are left behind, what gap each one shows, and where closer attention is warranted. Visitor counts come from DOT as yearly PDFs, economic and population data come from PSA in different spreadsheet formats, and official place codes come from PSGC. The sources cover different years and do not name places the same way.

**ProvInsights brings them together.** One Databricks pipeline connects tourism, population and economic data for every province, and a dashboard turns it into a province-by-province view: where the gaps are and which provinces warrant closer attention. It shows where to look. It does not prescribe interventions, investments or lead agencies (DL-037).

**Who it is for:** DOT and its regional offices (national planning), provincial and city tourism offices (local planning), DTI (local businesses), and development planners (NEDA/DEPDev).

## Business question

> **How can tourism and economic data across Philippine provinces be analyzed to identify destinations that warrant closer attention for tourism development?**

- **Closer attention** means a province shows a gap on the data (few visitors, low output per visitor, or both) that justifies further study. It is not a recommendation to invest.
- **Equalized tourism development** is the NTDP's Goal 4: opening more of the Philippines to tourism and supporting destinations beyond the established ones. The NTDP describes it as a direction, not a numeric target. ProvInsights supports it by showing where tourism is concentrated (AQ1) and which provinces warrant closer attention (AQ2 to AQ4).
- **Reporting units.** The analysis covers 100 reporting units: 82 provinces, 16 highly urbanized cities (HUCs) that DOT reports separately, the City of Isabela and the National Capital Region (DL-010). All are called "provinces" here.

## Analytical questions

The canonical questions, definitions and rules are in [docs/business-and-analytical-questions.md](docs/business-and-analytical-questions.md).

| Analytical question | Purpose | NTDP link | Analytics tables |
| --- | --- | --- | --- |
| **AQ1:** Which provinces have the highest and lowest tourism activity, and how is it distributed across provinces? | Shows how unevenly tourism is distributed, how much is concentrated in the leading destinations, and which provinces record the fewest visitors | Goal 4; Obj. 2.2 | `tourism_activity`, `tourism_concentration` |
| **AQ2:** How do provinces compare in both the number of visitors and the tourism-related output per visitor? | Examines whether provinces with similar visitor numbers generate similar output per visitor | Obj. 4.1 | `tourism_economy` |
| **AQ3:** Is high tourism-related output per visitor observed only in provinces with higher GDP per capita? | Tests whether the AQ2 pattern extends beyond GDP per capita | Goal 4 | `tourism_economy` |
| **AQ4:** Which provinces outside the leading destinations warrant closer attention, and what gap does the data show for each? | A named list of provinces, each with the gap indicated by the data | Obj. 4.1, 4.2 | `tourism_economy`, `tourism_activity` |

The questions build the answer in order: **find the gap** (AQ1), **compare** output per visitor (AQ2), **check** whether the pattern is explained by GDP per capita (AQ3), then **identify** where closer attention is warranted (AQ4).

The trend period is **2019-2023**, with 2020 and 2021 identified as COVID-19 years. AQ2 to AQ4 use **2023**, the latest year with both DOT and PSA provincial data.

## Key terms

| Term | Definition |
| --- | --- |
| **Overnight travelers (visitors)** | Travelers reported by DOT as staying overnight in accommodation establishments. The figure counts stays, not unique persons, and excludes day-trippers. |
| **Tourism activity** | The number of overnight travelers recorded in a province in a given year. |
| **Leading destinations** | The 10 provinces with the highest average annual overnight travelers across the years with reported data in 2019-2023 (DL-032). |
| **Tourism-related output** | Accommodation and food services (A&F) gross value added at current prices, used as a proxy for tourism-related economic activity (DL-007). |
| **Output per visitor** | A&F gross value added divided by overnight travelers for 2023, in PHP. A&F GVA is published in thousand PHP and multiplied by 1,000 before division (DL-033). |
| **Lower GDP per capita** | A 2023 GDP per capita (current prices) below the median of all reporting units that have a 2023 value (DL-035). |
| **Tourism share of the economy** | A&F gross value added divided by GDP, both at current prices, multiplied by 100, for 2023. |
| **Small base** | A province with fewer than 10,000 overnight travelers in 2023. Its output per visitor may be inflated by the small denominator (DL-036). |

**Tourism activity means reported overnight travelers.** It is not a count of unique people or all visitors. **A&F (hotels and restaurants) is a proxy for tourism's economic output**, because PSA publishes tourism's value added only at the national level. It also includes spending by residents, so it describes tourism-related patterns, not exact tourist spending. Findings support further study, not causal or investment-return claims (DL-008). A missing value is never treated as zero (DL-009).

## Province groups

Each province beyond the leading destinations is placed against the 2023 medians of visitors and output per visitor, taken across all provinces with data (DL-034).

| Group | Visitors | Output per visitor | Gap the data shows |
| --- | --- | --- | --- |
| **Established** | High | High | None on these two measures |
| **Busy but low-output** | High | Low | Output per visitor |
| **Small but high-output** | Low | High | Visitor numbers |
| **Limited activity** | Low | Low | Both |

The AQ4 priority list orders provinces by group (Busy but low-output, then Small but high-output, then Limited activity), then by lower GDP per capita, higher tourism share of the economy, and more visitors. Established provinces have no gap and are not listed. Small-base provinces stay in the list and are marked "Check before naming" (DL-037).

The groups describe positions relative to other provinces. They are not national benchmarks, and they do not say what a province needs or which agency should act.

## Data sources

| Source | Role |
| --- | --- |
| DOT Regional Distribution of Overnight Travelers (2019-2024) | Provincial tourism activity |
| PSA population projections | Population denominators for tourism intensity |
| PSA provincial GDP, GDP per capita, and accommodation and food services GVA | Output per visitor, tourism share of the economy, lower GDP per capita flag |
| PSA PSGC | Official place codes and the crosswalk that makes all sources agree on what a place means |

See [Source assessment](docs/consolidated-data-sources.md) and [Data sources](docs/data-sources.md) for identifiers and limitations.

## How the pipeline works

```text
Government source files
    → Ingestion and Bronze      (notebooks/01_ingestion)
    → Silver                    (notebooks/02_silver)
    → Gold                      (notebooks/03_gold)
    → Analytics                 (notebooks/04_analytics)
    → Dashboard
```

- **Silver** cleans each source and maps places to PSGC units. Each Silver notebook runs its own data-quality checks and fails on a BLOCK error.
- **Gold** is a star schema: `dim_province`, `dim_year` and `fact_province_year` (see [schema and source-to-target mapping](docs/schema-and-source-to-target-mapping.md)).
- **Analytics** calculates the business metrics once, in `tuklas_dev.05_analytics`. Every row carries the Analytics run ID and the exact Gold Delta versions it was built from. `tourism_recovery` and `traveler_segment_recovery` are also built as supporting tables, but they are not used to answer the business question.
- **Data quality:** check results are saved in `06_data_quality.dq_results`, and each layer records its runs in a run log (`silver_run_log`, `gold_run_log`, `05_analytics.analytics_run_log`). A BLOCK check protects correctness. A REVIEW check flags something unusual that needs a person to look.

Run evidence: [Gold](docs/gold-run-evidence.md) and [Analytics](docs/analytics-run-evidence.md).

The job in [`resources/jobs/tourism_pipeline.yml`](resources/jobs/tourism_pipeline.yml) runs the layers in dependency order. Task order, settings and how to add a task are in [`resources/README.md`](resources/README.md).

## Dashboard

The Databricks AI/BI dashboard answers one analytical question per page.

| Page | Answers |
| --- | --- |
| 1. Where visitors go | AQ1: highest and lowest tourism activity |
| 2. Output per visitor | AQ2: visitors and tourism-related output per visitor |
| 3. Tourism and GDP per capita | AQ3: whether high output per visitor is limited to higher-GDP provinces |
| 4. Provinces to look at | AQ4: provinces outside the leading destinations that warrant closer attention |
| Definitions | Key terms and the proxy note |

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
  architecture.md                 # placeholder
  runbook.md                      # placeholder
notebooks/
  01_ingestion_bronze/                   # sources to Bronze
  02_silver/
  03_gold/
  04_analytics/                   # build, validation, run evidence
  99_maintenance/                 # one-off maintenance, run by hand (not in the job)
resources/
  jobs/tourism_pipeline.yml       # end-to-end Databricks job
  seeds/                          # reviewed crosswalk files
databricks.yml                    # Databricks bundle
src/                              # folder guidance; pipeline logic lives in the notebooks
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

CI checks repository structure, Python files under `src/`, notebook structure, syntax in marked Python and SQL cells, and the Databricks bundle. It does not run the notebooks or validate source data.

## Team GitAway

**GitAway, FTW Batch 12 LT3:** Cole, Nella (lead), Cha, Gab, and Haze.
