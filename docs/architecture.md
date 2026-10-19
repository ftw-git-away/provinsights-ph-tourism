# ProvInsights Architecture

This document explains how ProvInsights turns government source files into a province-level dashboard: the components, how data flows between them, where quality is enforced, and why the main design choices were made.

For the business questions see [business-and-analytical-questions.md](business-and-analytical-questions.md). For table-level columns see [schema-and-source-to-target-mapping.md](schema-and-source-to-target-mapping.md). For how to run the pipeline see [runbook.md](runbook.md).

## Contents

1. [Purpose and users](#1-purpose-and-users)
2. [Architecture overview](#2-architecture-overview)
3. [Detailed data flow](#3-detailed-data-flow)
4. [Components by layer](#4-components-by-layer)
5. [Data quality and governance](#5-data-quality-and-governance)
6. [Orchestration and deployment](#6-orchestration-and-deployment)
7. [Key design decisions](#7-key-design-decisions)
8. [Lineage, reruns and reproducibility](#8-lineage-reruns-and-reproducibility)
9. [Limitations and known gaps](#9-limitations-and-known-gaps)

---

## 1. Purpose and users

**Problem.** The purpose of this project is to identify whether tourism growth is reaching beyond the usual strong destinations, and how tourism moves with local tourism-related economic activity. The answer needs three government sources that use different place names, different years and different formats (PDF and Excel). None of them can be compared directly.

**What the architecture provides.** One trusted table per province and year that joins tourism, economy and population on a single geographic key, metrics computed once from that table, and a dashboard that reads only those metrics. Every number can be traced back to the source file and row it came from.

**Users.**

| User | Uses |
| --- | --- |
| Tourism planners (non-technical) | The dashboard |
| Data team (GitAway) | Notebooks, job, data-quality results, run logs |
| Reviewers and future maintainers | This document, the decision log, run evidence |

## 2. Architecture overview

![ProvInsights architecture](<img width="1304" height="567" alt="image" src="https://github.com/user-attachments/assets/ef61c59c-1f5d-42c4-9898-3ea0dc846171" />)

Everything runs on **Databricks** with **Unity Catalog** and **Delta Lake**, in the catalog `tuklas_dev`. Each layer has its own schema:

| Schema | Layer | Holds |
| --- | --- | --- |
| `01_ingestion` | Ingestion control | `ingestion_run_log`, `file_manifest`, `ingestion_errors` |
| `02_bronze` | Bronze | Source tables kept exactly as printed, plus the original files as binary |
| `03_silver` | Silver | Cleaned, typed tables mapped to reporting units; `silver_run_log` |
| `04_gold` | Gold | Star schema: `dim_province`, `dim_year`, `fact_province_year`; `gold_run_log` |
| `05_analytics` | Analytics (serving) | Five metric tables for the business questions; `analytics_run_log` |
| `06_data_quality` | Governance | `dq_results`: one row per check per run, across all layers |

| Component | Technology |
| --- | --- |
| Source storage | Google Drive, read through the Unity Catalog connection `capstone_gdrive` |
| Processing | Databricks notebooks (PySpark and SQL) |
| Storage | Delta tables in Unity Catalog |
| Reference data | Reviewed seed CSVs in [`resources/seeds/`](../resources/seeds/) |
| Orchestration | Databricks job `tourism_pipeline`, defined in a Databricks Asset Bundle |
| CI/CD | GitHub Actions: validate on pull request, deploy on merge |
| Serving | Databricks dashboard on `05_analytics` |

## 3. Detailed data flow

```mermaid
flowchart LR
    subgraph SRC["Sources (Google Drive)"]
        DOT["DOT DS_05<br/>overnight travelers<br/>PDF, 2019–2024"]
        PSA["PSA DS_26–32<br/>GDP, GDP per capita, A&F GVA<br/>Excel"]
        POP["PSA DS_18<br/>population projections<br/>Excel + PDF"]
        PSGC["PSGC 2Q 2026<br/>DS_33, DS_34<br/>Excel"]
    end

    subgraph BR["02_bronze: as printed"]
        B1["dot_ds_05_YEAR"]
        B2["psa_ds_27 … psa_ds_32"]
        B3["psa_ds_18, psa_ds_18_pdf_rows"]
        B4["psgc_ds_34_SHEET"]
    end

    SEED[("resources/seeds<br/>crosswalks + coordinates")]

    subgraph SV["03_silver: cleaned, one row per unit-year"]
        G["geo_psgc<br/>geo_reporting_unit"]
        S1["dot_travelers_unit_year"]
        S2["psa_economy_unit_year"]
        S3["population_unit_year"]
    end

    subgraph GD["04_gold: star schema"]
        DP["dim_province (100)"]
        DY["dim_year (6)"]
        F["fact_province_year (600)"]
    end

    subgraph AN["05_analytics: metrics"]
        A["tourism_activity<br/>tourism_concentration<br/>tourism_recovery<br/>traveler_segment_recovery<br/>tourism_economy"]
    end

    DQ[("06_data_quality.dq_results")]
    DASH["Dashboard"]

    DOT --> B1
    PSA --> B2
    POP --> B3
    PSGC --> B4
    B4 --> G
    SEED --> G
    B1 --> S1
    B2 --> S2
    B3 --> S3
    G --> S1 & S2 & S3
    G --> DP
    S1 & S2 & S3 --> DY
    S1 & S2 & S3 --> F
    DP & DY --> F
    F --> A
    DP & DY --> A
    A --> DASH
    SV -. checks .-> DQ
    GD -. checks .-> DQ
    AN -. checks .-> DQ
```

**Grain at each step.** Bronze keeps one row per printed source row. Silver reduces each source to one row per **reporting unit and year**. Gold joins the three sources at that same grain: 100 units × 6 years (2019–2024) = 600 rows. Analytics computes metrics at the grain each business question needs (unit-year, year, or unit).

## 4. Components by layer

### 4.1 Sources

| Source | Dataset | Format | Used for |
| --- | --- | --- | --- |
| DOT Regional Distribution of Overnight Travelers | DS_05, 2019–2024 | PDF, one per year | Tourism activity, recovery, traveler segments |
| PSA Provincial Accounts | DS_27 to DS_32 (DS_26 for reconciliation) | Excel | GDP, GDP per capita, A&F GVA (current and constant 2018 prices) |
| PSA Projected Mid-Year Population | DS_18 | Excel and PDF | Population denominator for tourism intensity |
| PSA Philippine Standard Geographic Code | DS_33, DS_34 (2Q 2026) | Excel | The geographic key shared by every table |

Source identifiers, coverage and limitations are in [consolidated-data-sources.md](consolidated-data-sources.md).

### 4.2 Ingestion and Bronze (`notebooks/01_ingestion`)

- `00_ingestion_setup` creates the control tables. It only uses `CREATE ... IF NOT EXISTS`.
- One notebook per source (`01_ingest_psa`, `02_ingest_psgc`, `03_ingest_dot`, `04_ingest_psa_ds18_pdf`) reads the files from Google Drive and writes Bronze tables.
- **Values are kept as text, exactly as printed.** No cleaning, mapping, deduplication or type conversion happens in Bronze.
- Every row keeps its position in the source (`source_row_number`, or `page_number` and `pdf_line_number` for PDFs) and carries `_run_id` and a source fingerprint (`_source_sha256`), so a changed file is detected (DL-023).
- The original PDF and Excel files are stored as binary (for example `dot_ds_05_pdf`, `psgc_source_files`), so the exact input can be re-read later.
- Titles, footnotes and "as of" notes go into `*_report_text` tables instead of being discarded.
- Each run is logged in `ingestion_run_log`, each file in `file_manifest`, and each failure in `ingestion_errors`.

Details: [bronze-ingestion-guide.md](bronze-ingestion-guide.md).

### 4.3 Silver (`notebooks/03_silver`)

Silver turns each source into clean, typed values for a common set of **100 reporting units** (DL-010).

| Notebook | Main outputs | What it does |
| --- | --- | --- |
| `01_silver_geography` | `geo_psgc`, `geo_reporting_unit`, `map_dot_area_to_psgc` | Builds the geography backbone from PSGC and the reviewed crosswalk seed. Region always comes from the PSGC code (DL-003). |
| `02_silver_dot` | `dot_travelers_unit_year`, `dot_travelers_row`, `dot_excluded_rows` | Maps every DOT label to a unit, applies row roles (add to parent, exclude), interprets `-` (DL-019), sets `traveler_value_status` and `comparable_to_2019` (DL-020). |
| `03_silver_psa_economy` | `psa_economy_unit_year`, `psa_economy_row`, `ref_indicator` | Matches PSA rows by cleaned name, adds Lucena into Quezon (DL-011), fills a single missing row from its region total (DL-024), records each measure's unit and price basis. |
| `04_silver_population` | `population_unit_year`, `population_row` | Combines DS_18 Excel and PDF to separate the 16 HUCs from their provinces (DL-021). |

Each notebook keeps a `*_row` table with one row per source value used, so every unit-year total can be traced back to the Bronze rows that made it. Rows that are deliberately left out are kept in an exceptions table, not dropped silently.

### 4.4 Gold (`notebooks/04_gold`)

Gold is a **star schema** that brings the three sources together.

| Table | Grain | Key | Built from |
| --- | --- | --- | --- |
| `dim_province` | Reporting unit (100) | `province_psgc` | `geo_reporting_unit`, `geo_psgc`, coordinates seed |
| `dim_year` | Year (2019–2024) | `year` | Silver coverage; flags the baseline year, recovery years and comparison window |
| `fact_province_year` | Unit × year (600) | (`province_psgc`, `year`) | `dot_travelers_unit_year`, `psa_economy_unit_year`, `population_unit_year` |

Gold copies values from Silver without recomputing them. A year a source doesn't cover is NULL, never 0 (DL-009). Caveat flags (`traveler_value_status`, `comparable_to_2019`, `foreign_includes_overseas_filipinos`, `derived_values`, `per_capita_recomputed`) are carried into the fact table so downstream layers keep them. Units of measure are stored as column comments from `ref_indicator`.

### 4.5 Analytics (`notebooks/05_analytics`)

`01_build_analytics` computes every business metric **once**, so the dashboard never recalculates anything.

| Table | Grain | Answers |
| --- | --- | --- |
| `tourism_activity` | Unit × year | AQ1.1: volume, intensity per 1,000 residents, rank, share |
| `tourism_concentration` | Year | AQ1.1: top-5 and top-10 share of travelers |
| `tourism_recovery` | Unit × comparison year | AQ1.2: recovery index against 2019 |
| `traveler_segment_recovery` | Unit (2023 below-2019 cohort) | AQ1.3: domestic, foreign and overseas Filipino recovery |
| `tourism_economy` | Unit | AQ2.1 to AQ2.4: tourism change against real A&F GVA growth, A&F share of GDP, 2019 GDP per capita |

The notebook builds each table in a temporary view, runs its blocking checks, and only then replaces the persisted table. `02_analytics_validation` then re-checks the persisted tables independently: it recomputes every derived metric from its inputs and reconciles base values to Gold at the exact Gold versions recorded on each row. `03_analytics_run_evidence` compares selected values against figures calculated straight from the source files.

Formulas and eligibility rules are in [schema-and-source-to-target-mapping.md §4.4](schema-and-source-to-target-mapping.md#44-calculations-in-05_analytics).

### 4.6 Serving: dashboard

The dashboard is a Databricks dashboard that reads **only** the `05_analytics` tables, plus `dim_province` for names and map points. It has seven pages for a non-technical audience, ending with a page on how far each number can be trusted. Because the metrics are computed in Analytics, the dashboard layer contains display logic only, and any number on it can be traced to a row in `05_analytics`. Page guide: [dashboard/README.md](../dashboard/README.md).

## 5. Data quality and governance

Quality is enforced **inside every layer from Silver on**, not as a separate step at the end.

```mermaid
flowchart LR
    BUILD["Build candidate result"] --> CHECK["Run checks"]
    CHECK -->|"all BLOCK checks pass"| WRITE["Write Delta table"]
    CHECK -->|"any BLOCK check fails"| STOP["Stop: table not replaced<br/>run marked FAILED"]
    CHECK -->|"REVIEW check fails"| FLAG["Write, mark run<br/>SUCCESS_WITH_REVIEW"]
    FLAG --> WRITE
    CHECK --> LOG[("dq_results")]
```

| Severity | Meaning | Effect |
| --- | --- | --- |
| **BLOCK** | The output would be wrong (duplicate keys, orphan keys, totals that don't reconcile, values changed between layers) | The notebook stops before writing. Downstream tasks don't run, and the job sends a failure email. |
| **REVIEW** | Something unusual that a person should look at (for example a jump that may be a small base or a doubtful 2019 count) | The table is written, the run is marked `SUCCESS_WITH_REVIEW`, and the flag is disclosed in run evidence and on the dashboard. |

- **Where results go.** Every check writes one row to `06_data_quality.dq_results` with `run_id`, `notebook_name`, `check_id`, `severity`, `status`, `failed_rows`, `expected`, `observed` and `sample_keys`. Each layer also has a run log (`silver_run_log`, `gold_run_log`, `analytics_run_log`) that records `STARTED`, `SUCCESS`, `SUCCESS_WITH_REVIEW` or `FAILED`.
- **What is checked.** Common checks (keys, nulls, row counts), source reconciliation (unit totals against printed region and national totals), crosswalk coverage (every DOT and PSA label maps to a unit or a documented exclusion), Gold join completeness (Silver values arrive in the fact unchanged), and Analytics recomputation.
- **Known exceptions.** Accepted deviations are listed in a register so a check doesn't fail on a case the team has already reviewed.
- **Decisions.** Every rule that changes data (a mapping, an exclusion, how `-` is read) has an entry in the [decision log](project-decision-log.md).

Check IDs, thresholds and the exceptions register: [data-quality-rules.md](data-quality-rules.md). Latest results: [gold-run-evidence.md](gold-run-evidence.md) and [analytics-run-evidence.md](analytics-run-evidence.md).

## 6. Orchestration and deployment

### 6.1 Pipeline job

The Databricks job **ProvInsights PH - End-to-End Pipeline** ([`resources/jobs/tourism_pipeline.yml`](../resources/jobs/tourism_pipeline.yml)) runs 18 notebook tasks in dependency order:

```text
ingestion_setup ─┬─ ingest_psa
                 ├─ ingest_psgc
                 ├─ ingest_dot
                 └─ ingest_psa_ds18_pdf
                          │ (all ingestion done)
silver_setup ─ silver_geography ─┬─ silver_dot
                                 ├─ silver_psa_economy
                                 └─ silver_population
                          │ (all Silver done)
gold_setup ─┬─ gold_dim_province ─┐
            └─ gold_dim_year ─────┴─ gold_fact_province_year ─ gold_run_evidence
                          │
analytics ─ analytics_validation ─ analytics_run_evidence
```

- Each layer starts with a setup task that waits for the whole previous layer, so a layer never reads half-finished inputs.
- Only one run at a time (`max_concurrent_runs: 1`), a three-hour job timeout, and per-task timeouts set at about three times the longest observed run.
- A failure emails the address in the bundle variable `alert_email`.

Task settings and how to add a task: [`resources/README.md`](../resources/README.md).

### 6.2 CI/CD

```mermaid
flowchart LR
    PR["Pull request"] --> CI["CI: Validate repository<br/>+ Validate Databricks bundle"]
    CI --> REVIEW["Teammate review"]
    REVIEW --> MERGE["Merge to main"]
    MERGE --> CD["CD: validate + deploy bundle<br/>(target dev)"]
    CD -. manual run with run_pipeline .-> JOB["Run tourism_pipeline"]
```

- **CI** ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) checks the repository structure, Python syntax, notebook structure and the syntax of marked Python and SQL cells, then runs `databricks bundle validate`.
- **CD** ([`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)) deploys the bundle when a merge to `main` touches pipeline files. Deploying updates the job but doesn't run it. A manual run with `run_pipeline` set also starts the job.
- The workspace URL and token live in GitHub environment settings, never in the repository.

## 7. Key design decisions

| Decision | Why | Alternative rejected | Ref |
| --- | --- | --- | --- |
| **Medallion layers in separate schemas**, plus a separate Analytics layer | Each layer has one job: preserve, clean, model, compute. A problem can be traced to the layer that caused it. | Cleaning and computing in one notebook per source, which mixes concerns and makes errors hard to locate | — |
| **Bronze keeps values as printed text, with the original file stored** | Government PDFs and Excel files vary in layout. Keeping the raw text means a parsing or cleaning rule can be fixed and rerun without re-downloading. | Typing and cleaning during ingestion, which loses evidence when a rule is wrong | DL-023 |
| **PSGC 2Q 2026 as the single geographic key for every year** | Sources use different names and older boundaries. One code list makes a unit mean the same thing in every year and every source. | Joining on place names, which breaks on spelling and boundary changes | DL-002, DL-010 |
| **Reporting unit = province, separately reported HUC, City of Isabela, or NCR** | This is the finest level all three sources share. | Province only, which would mix HUCs into provinces differently in each source | DL-010 to DL-012 |
| **Reviewed seed CSVs for crosswalks** | Mapping 160+ DOT labels and 130+ PSA labels needs human judgment. Keeping the result in version control makes it reviewable and repeatable. | Fuzzy matching at run time, which can change silently | DL-010 to DL-018 |
| **Missing is NULL, never 0, with a status column** | A missing report is not zero tourism. Treating it as 0 would invent declines. | Filling with 0 | DL-009, DL-019 |
| **Star schema in Gold** | One fact table at a shared grain makes cross-source comparison a simple join, and the dimensions carry the year rules so they aren't hard-coded in each query. | One wide table per question | — |
| **Metrics computed once in Analytics, not in the dashboard** | Every number has one definition, can be validated, and is the same wherever it appears. | Dashboard-level calculations, which can't be tested and drift between pages | — |
| **Analytics records the Gold Delta versions it read** | Any metric can be reproduced exactly with `VERSION AS OF`, even after Gold is rebuilt. | Reading "latest" with no record | — |
| **BLOCK and REVIEW severities, checked before writing** | Wrong data never reaches the dashboard, while unusual-but-valid data is shown with a flag instead of hidden. | One severity level, which either blocks too much or lets errors through | [data-quality-rules.md](data-quality-rules.md) |
| **Comparability judged per unit and year** | DOT changed what it counts for some places (Boracay, Clark). A unit-year that isn't comparable to 2019 is flagged rather than removed. | Dropping affected units entirely | DL-013, DL-014, DL-020 |
| **Report associations, not causation** | The data shows patterns; it can't show what causes them. | Claims about investment returns or growth levers | DL-007, DL-008 |
| **Infrastructure as code (Databricks Asset Bundle)** | The job is versioned with the notebooks, reviewed in pull requests and deployed the same way every time. | A job configured by hand in the workspace | — |

All 30 decisions, with dates and the pull requests that approved them, are in the [decision log](project-decision-log.md).

## 8. Lineage, reruns and reproducibility

**Lineage.** A dashboard number can be traced back to its source:

| From | To | Through |
| --- | --- | --- |
| Analytics row | Gold version | `_analytics_run_id`, `_gold_fact_version`, `_gold_dim_province_version`, `_gold_dim_year_version` |
| Gold fact | Silver unit-year | Same key, values copied unchanged (checked by a BLOCK rule) |
| Silver unit-year | Bronze rows | `*_row` tables and the crosswalk seeds |
| Bronze row | Source file | `source_row_number` or page and line, `_source_sha256`, stored original file |

**Reruns.** Setup notebooks only create what's missing. Ingestion replaces only the datasets or years selected. Silver, Gold and Analytics write after their checks pass and replace their tables, so running the job twice on the same inputs gives the same result. The five Analytics tables are written as separate Delta operations, so a run that stops partway reports which tables were and weren't replaced.

**Reproducing the pipeline.** Deploy the bundle and run `tourism_pipeline` (see the [runbook](runbook.md) and the [README](../README.md#databricks-deployment)). The run logs and `dq_results` show whether the new run matches the recorded evidence.

## 9. Limitations and known gaps

**Data limitations** (affect what the results can claim):

- Tourism activity means **reported overnight travelers** in accommodation establishments, not unique visitors.
- A&F GVA is a proxy for tourism-related activity. It also includes spending by residents.
- DOT reporting coverage changes over time for some units, so their recovery against 2019 is flagged rather than treated as exact (OI-5, DL-029).
- Six units have no DOT data (BARMM provinces and Sulu), and Sulu's PSA region differs from its PSGC region (OI-2).
- The 2019 population of the 16 HUCs and their provinces is estimated (DL-021).

**Architecture limitations** (planned improvements):

- The pipeline runs in a single development target (`dev`, catalog `tuklas_dev`). There is no separate production target or catalog yet.
- The job is triggered manually. It has no schedule, because the sources are published yearly.
- Source files are placed in Google Drive by hand. There is no automatic download from DOT or PSA.
