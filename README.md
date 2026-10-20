# ProvInsights

[![CI](https://github.com/ftw-git-away/provinsights-ph-tourism/actions/workflows/ci.yml/badge.svg)](https://github.com/ftw-git-away/provinsights-ph-tourism/actions/workflows/ci.yml)

**Province-level tourism and economic analytics to support equalized tourism development in the Philippines**

ProvInsights is GitAway's FTW Batch 12 LT3 capstone. It brings together Department of Tourism (DOT), Philippine Statistics Authority (PSA), and Philippine Standard Geographic Code (PSGC) data in one Databricks pipeline, so planners can see where tourism is concentrated, which provinces are left behind, and what kind of support each province needs.

## Problem

**Tourism is one of the country's biggest industries, but its benefits are concentrated in a few places.** In 2023, tourism employed 6.21 million Filipinos and made up 8.6% of GDP (PSA, Philippine Tourism Satellite Account). Yet in 2017, Boracay, an island of only about 10 km², hosted one in three visitors to the country, and in 2018 it had to close for six months to recover from overcrowding and pollution. The pattern continues: in 2023, the 10 leading destinations received **43.7%** of all overnight travelers, while many provinces with beaches, mountains and culture received far fewer.

<p align="center">
  <img width="720" alt="Crowded White Beach in Boracay, Aklan" src="https://github.com/user-attachments/assets/9dbf098e-9f11-4c84-90bc-bc43654ae07c" />
  <br />
  <sub>Boracay, Aklan. Photo: <a href="https://www.rappler.com/culture-desk/travel/boracay-included-world-greatest-places-2022-time-magazine">Rappler</a>.</sub>
</p>

**The DOT has made spreading tourism a national goal.** Its [National Tourism Development Plan (NTDP) 2023-2028](https://www.visitcentralluzon.com/wp-content/uploads/2026/02/DOT-NTDP-23-00043-Department-of-Tourism-National-Tourism-Development-Plan-2023-2028.pdf) sets **Goal 4: Equalization of tourism product development and promotion**, which aims to create opportunities for emerging provinces (Objective 4.1) and link them with key destinations through circuits and joint promotion (Objective 4.2). The plan also calls for product mapping across all regions and provinces (Objective 4.3) and for better tourism data and monitoring (Objectives 2.2 and 4.5).

**But the evidence planners need is scattered.** To act on Goal 4, planners need to know which provinces are left behind, what each one lacks, and where tourism is a realistic path. Visitor counts come from DOT as yearly PDFs, economic and population data come from PSA in different spreadsheet formats, and official place codes come from PSGC. The sources cover different years and do not name places the same way.

**ProvInsights brings them together.** One Databricks pipeline connects tourism, population and economic data for every province, and a dashboard turns it into a province-by-province plan: where the gaps are, what kind of support each province needs, and which provinces to prioritize.

**Who it is for:** DOT and its regional offices (national planning), provincial and city tourism offices (local planning), DTI (local businesses), and development planners (NEDA/DEPDev).

## Business question

> **How can tourism development be planned to benefit provinces beyond the leading tourist destinations?**

- **Tourism development** is an umbrella term for the support a province can receive: better access (roads, ports, airports), promotion and tourism circuits, links between local businesses and hotels and restaurants, and, where tourism is not yet a realistic path, a focus on other industries first.
- **Benefit** means a province gains more from tourism, through more visitors, more earnings from each visitor, or both.
- **Equalized tourism development** is the NTDP's Goal 4: opening more of the Philippines to tourism and supporting destinations beyond the established ones. The NTDP describes it as a direction, not a numeric target. ProvInsights supports it by showing where tourism is concentrated (AQ1) and which provinces to prioritize and how (AQ2 to AQ4).

## Analytical questions

The canonical questions, definitions, thresholds and queries are in [docs/business-and-analytical-questions.md](docs/business-and-analytical-questions.md).

| Analytical question | What it tells planners | NTDP link | Analytics tables |
| --- | --- | --- | --- |
| **AQ1:** Which provinces have the highest and lowest tourism activity? | Where tourism is concentrated, which provinces are left behind, and which 10 are the leading destinations | Goal 4; Obj. 2.2 | `tourism_activity`, `tourism_concentration` |
| **AQ2:** Which provinces generate the highest and lowest tourism-related output per visitor? | Which provinces need more visitors, and which need visitors to spend more locally | Obj. 4.1 | `tourism_economy`, `tourism_activity` |
| **AQ3:** Which provinces rely most and least on tourism-related activity, and is this limited to higher-income provinces? | Whether tourism is a realistic path for lower-income provinces, or whether other industries should come first | Goal 4 | `tourism_economy` |
| **AQ4:** Which provinces beyond the leading destinations should be prioritized, and what type of tourism development does each one need? | A named priority list, with a recommended action and lead agencies for each province | Obj. 4.1, 4.2, 7.5 | `tourism_economy`, `tourism_activity` |

The questions build the answer in order: **find the gap** (AQ1), **diagnose** what each province lacks (AQ2), **check** that tourism is a realistic path (AQ3), then **plan** (AQ4).

The trend years are **2019-2023**, and the analysis year for AQ2 to AQ4 is **2023**, the latest year with both DOT and PSA provincial data. 2020-2021 are labeled as COVID-19 years.

## Key terms

| Term | Plain meaning | How it is measured |
| --- | --- | --- |
| **Tourism activity** | How many people stay overnight in a province | DOT-reported overnight travelers in accommodation establishments. Not unique visitors, and not day-trippers. |
| **Tourism intensity** | Tourism activity relative to the local population | Overnight travelers per 1,000 residents |
| **Leading destinations** | The provinces that receive the most visitors | The 10 provinces with the highest average annual overnight travelers, 2019-2023 |
| **Earnings per visitor** | How much tourism-related output a province generates per traveler | Accommodation and food services output (PHP) per overnight traveler, 2023 |
| **Tourism share of the economy** | How much a province's economy relies on tourism-related activity | Accommodation and food services output as a % of provincial GDP, 2023 |
| **Lagging province** | A province with lower income than most | 2023 GDP per capita below the median of all provinces with data |

**Tourism activity means reported overnight travelers.** It is not a count of unique people or all visitors. **We use accommodation and food services (hotels and restaurants) as a proxy for tourism's economic output**, because PSA publishes tourism's value added only at the national level. It also includes spending by residents, so it describes tourism-related patterns, not exact tourist spending. Findings support planning priorities and further study, not causal or investment-return claims. A missing value is never treated as zero.

## Recommended actions

Each province beyond the leading destinations is grouped by its number of visitors and its earnings per visitor (above or below the 2023 median), and each group gets an action.

| Group | Action | Lead agencies |
| --- | --- | --- |
| Few visitors, high earnings per visitor | **Bring in more visitors**: improve access, feature in promotions, link to nearby leading destinations through circuits | DPWH, DOTr, TIEZA, DOT |
| Many visitors, low earnings per visitor | **Help visitors spend more locally**: multi-day packages, link local farmers and MSMEs to hotels and restaurants | DOT, LGUs, DTI, DA |
| Few visitors, low earnings per visitor | **Focus on other industries first**: prioritize other sectors or basic infrastructure, revisit tourism later | LGUs, NEDA/DEPDev |
| Many visitors, high earnings per visitor | **Sustain and connect**: maintain performance, link to neighboring provinces | DOT, LGUs |
| Leading destinations | **Spread visitors outward**: regional circuits and joint packages, manage crowding | DOT, LGUs |

Among provinces beyond the leading destinations, lagging provinces get extra priority.

Each action names the agencies that need to work together. This reflects the NTDP's call for **convergence**: national agencies and LGUs aligning their programs, since many factors behind tourism (roads, ports, local business support) are outside DOT's mandate.

## Data sources

| Source | Role |
| --- | --- |
| DOT Regional Distribution of Overnight Travelers (2019-2024) | Provincial tourism activity |
| PSA population projections | Population denominators for tourism intensity |
| PSA provincial GDP, GDP per capita, and accommodation and food services GVA | Earnings per visitor, tourism share of the economy, lagging flag |
| PSA PSGC | Official place codes and the crosswalk that makes all sources agree on what a place means |

See [Source assessment](docs/consolidated-data-sources.md) and [Data sources](docs/data-sources.md) for identifiers and limitations.

## How the pipeline works

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
- **Analytics** calculates the business metrics once, in `tuklas_dev.05_analytics`. Every row carries the Analytics run ID and the exact Gold Delta versions it was built from. `tourism_recovery` and `traveler_segment_recovery` are also built as supporting tables, but they are not used to answer the business question.
- **Data quality:** check results are saved in `06_data_quality.dq_results`, and each layer records its runs in a run log (`silver_run_log`, `gold_run_log`, `05_analytics.analytics_run_log`). A BLOCK check protects correctness. A REVIEW check flags something unusual that needs a person to look.

Run evidence: [Gold](docs/gold-run-evidence.md) and [Analytics](docs/analytics-run-evidence.md).

The job in [`resources/jobs/tourism_pipeline.yml`](resources/jobs/tourism_pipeline.yml) runs the layers in dependency order. Task order, settings and how to add a task are in [`resources/README.md`](resources/README.md).

## Dashboard

The Databricks AI/BI dashboard answers one analytical question per page.

| Page | Answers |
| --- | --- |
| 1. Where visitors go | AQ1: highest and lowest tourism activity |
| 2. Earnings per visitor | AQ2: tourism-related output per visitor |
| 3. Tourism and wealth | AQ3: reliance on tourism-related activity by income level |
| 4. Priority provinces | AQ4: priority provinces and the type of tourism development each needs |
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
  01_ingestion/                   # sources to Bronze
  03_silver/
  04_gold/
  05_analytics/                   # build, validation, run evidence
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
