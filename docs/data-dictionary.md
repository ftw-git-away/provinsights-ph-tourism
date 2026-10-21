# ProvInsights Data Dictionary

What every table and column in the pipeline means, layer by layer, in the same order as the `notebooks/` folders. All tables are Delta tables in the Unity Catalog catalog `tuklas_dev`.

Related docs: [business and analytical questions](business-and-analytical-questions.md) (definitions), [schema and source-to-target mapping](schema-and-source-to-target-mapping.md) (how each Gold column is mapped from the sources), [data-quality rules](data-quality-rules.md) (every check ID), [architecture](architecture.md) and [runbook](runbook.md).

## Contents

1. [How to read this dictionary](#1-how-to-read-this-dictionary)
2. [`01_ingestion_bronze` → `01_ingestion` and `02_bronze`](#2-01_ingestion_bronze--01_ingestion-and-02_bronze)
3. [`02_silver` → `03_silver`](#3-02_silver--03_silver)
4. [`03_gold` → `04_gold`](#4-03_gold--04_gold)
5. [`04_analytics` → `05_analytics`](#5-04_analytics--05_analytics)
6. [Dashboard: `ds_profile`](#6-dashboard-ds_profile)
7. [Data quality: `06_data_quality`](#7-data-quality-06_data_quality)
8. [Value lists](#8-value-lists)

---

## 1. How to read this dictionary

### Notebook folders and schemas

The notebook folders were renumbered by pipeline step. The schemas they write to kept their original numbers, so a folder and its schema have different numbers.

| Notebook folder | Writes to schema | Layer |
| --- | --- | --- |
| `notebooks/01_ingestion_bronze` | `01_ingestion`, `02_bronze` | Ingestion control and Bronze |
| `notebooks/02_silver` | `03_silver` | Silver |
| `notebooks/03_gold` | `04_gold` | Gold |
| `notebooks/04_analytics` | `05_analytics` | Analytics |
| every layer | `06_data_quality` | Data-quality results |
| `notebooks/99_maintenance` | none | One-off notebooks run by hand |

Tables are named by schema in this dictionary, for example `05_analytics.tourism_economy`.

### Conventions

| Topic | Rule |
| --- | --- |
| **Province** | A **reporting unit**: one of 82 provinces, 16 HUCs that DOT reports separately, the City of Isabela, or NCR. 100 in total (DL-010). |
| **Key** | `province_psgc` (Gold and Analytics) or `unit_psgc_code` (Silver): the 10-digit PSGC 2Q 2026 code, stored as text so leading zeros are kept. |
| **Years** | Silver, Gold and Analytics cover 2019-2024. The business question uses 2019-2023 for trends and 2023 for AQ2 to AQ4 (DL-031). |
| **Missing** | NULL, never 0 (DL-009). A reported 0 is a real 0. |
| **Money** | `gdp_total_*` and `afs_gva_*` are in **thousand PhP**, as published. `gdp_per_capita_*` is in **PhP**. `*_current` = current prices, `*_constant` = constant 2018 prices. Shares use current prices; growth uses constant prices. |
| **Travelers** | Overnight travelers in accommodation establishments, as reported by DOT. They count stays, not unique people, and exclude day-trippers. |
| **Percentages and indexes** | `*_pct` columns run from 0 to 100. A recovery index is the comparison-year value ÷ the 2019 value × 100, so 100 = back at the 2019 level. |
| **Eligibility** | In Analytics, every metric has an `*_eligible` flag and an `*_exclusion_reason`. The metric is filled only when the row is eligible. |
| **Types** | Spark types where the notebook sets them (`STRING`, `INT`, `BIGINT`, `DECIMAL(20,0)`, `DOUBLE`, `BOOLEAN`, `TIMESTAMP`). Run `DESCRIBE TABLE` for any column not listed with a type. |
| **Lineage columns** | Columns starting with `_` record where a row came from and which run wrote it. They are listed once per layer. |

### The terms used in the business question

| Term | Where it comes from |
| --- | --- |
| Tourism activity | `total_travelers` |
| Tourism intensity | `tourism_intensity_per_1000` (travelers per 1,000 residents) |
| Leading destinations | Top 10 by average annual travelers, 2019-2023 (DL-032): `ds_profile.is_leading_destination` |
| Tourism-related output | `afs_gva_current` (A&F gross value added, a proxy, DL-007) |
| Output per visitor | `ds_profile.earnings_per_visitor` (DL-033) |
| Lower-income | `ds_profile.is_lagging` (DL-035) |
| Small base | `ds_profile.small_base_2023` (DL-036) |
| Province group | `ds_profile.group_label` (DL-034) |
| Tourism share of the economy | `afs_share_of_gdp_pct` (context only) |

---

## 2. `01_ingestion_bronze` → `01_ingestion` and `02_bronze`

### 2.1 `01_ingestion`: ingestion control

Created by `00_ingestion_setup`.

**`ingestion_run_log`**: one row per ingestion notebook run. Key: `run_id` (the row is inserted as `STARTED` and updated at the end, never appended twice).

| Column | Description |
| --- | --- |
| `run_id` | Run ID, for example `dot_20261021_...`. |
| `notebook_name` | Ingestion notebook. |
| `source_system`, `source_folder` | Source (DOT, PSA, PSGC) and its Google Drive folder. |
| `started_at`, `completed_at` | Run start and end. |
| `files_discovered`, `files_ingested`, `files_skipped`, `files_failed` | File counts for the run. |
| `tables_created` | Bronze tables written. |
| `status` | `STARTED`, `SUCCESS`, `PARTIAL_SUCCESS` or `FAILED`. |
| `notes` | Free text. |

**`file_manifest`**: one row per source file (and sheet) and Bronze table, per run. Key: (`run_id`, `source_dataset_id`, `source_file`, `source_sheet`, `destination_table`), the same columns its `MERGE INTO` matches on.

| Column | Description |
| --- | --- |
| `run_id`, `notebook_name` | The run. |
| `source_dataset_id` | Dataset ID, for example `DS_05`. |
| `source_system`, `source_file`, `source_sheet`, `source_path` | Where the data came from. |
| `destination_table` | Bronze table written. |
| `row_count`, `column_count` | Size of what was written. |
| `status` | `DISCOVERED`, `INGESTED`, `SKIPPED`, `NEEDS_REVIEW` or `FAILED`. |
| `discovered_at`, `ingested_at` | Timestamps. |
| `notes` | Includes a warning when a file's SHA-256 fingerprint changed since the last run. |

**`ingestion_errors`**: one row per failure. No unique key: a run can log several errors for one file; find them by `run_id` and `source_file`. Same source columns as `file_manifest`, plus `error_type`, `error_message`, `error_timestamp` and `notes`.

### 2.2 `02_bronze`: source data as printed

Written by `01_ingest_psa`, `02_ingest_psgc`, `03_ingest_dot` and `04_ingest_psa_ds18_pdf`, through the Unity Catalog connection `capstone_gdrive`. **Every value is kept as text, exactly as printed**; nothing is cleaned or mapped here.

| Table pattern | One row = | Examples |
| --- | --- | --- |
| `dot_ds_05_<year>` | One printed row of the DOT table for that year | `dot_ds_05_2023` |
| `psa_ds_<nn>` and `psa_ds_<nn>_<sheet>` | One printed row of a PSA table | `psa_ds_27` (GDP), `psa_ds_31` (A&F GVA), `psa_ds_18` (population) |
| `psa_ds_18_pdf_rows` | One printed row of the DS_18 population PDF | |
| `psgc_ds_33_<sheet>`, `psgc_ds_34_<sheet>` | One printed row of a PSGC sheet | `psgc_ds_34_psgc` |
| `*_report_text` | One non-table line (title, "as of" date, footnote) | `dot_ds_05_report_text` |
| `*_pdf`, `*_source_files` | One original file stored as binary | `dot_ds_05_pdf`, `psgc_source_files`, `psa_ds_18_pdf` |

**Keys.** Bronze tables have no business key: they keep every printed row, duplicates included. A row is located by its file and position: (`_source_file`, `_source_sheet`, `source_row_number`) for Excel and CSV tables, or (`_source_file`, `page_number`, `pdf_line_number`) for PDF tables. Binary-file tables (`*_pdf`, `*_source_files`) have one row per file, keyed by `_source_file`.

**Columns on every Bronze row**

| Column | Description |
| --- | --- |
| `source_row_number`, or `page_number` and `pdf_line_number` | The row's position in the source file (DL-023). |
| `_source_dataset_id` | Dataset ID. |
| `_source_file`, `_source_sheet`, `_source_path` | File, sheet and Drive path. |
| `_source_system` | DOT, PSA or PSGC. |
| `_ingested_at` | When the row was written. |
| `_run_id` | Ingestion run that wrote it. |
| `_source_sha256` | SHA-256 fingerprint of the source file, so a replaced file is detected. |

File IDs and folder links are in the [Bronze ingestion guide](bronze-ingestion-guide.md).

---

## 3. `02_silver` → `03_silver`

Silver turns each source into clean, typed values for the 100 reporting units. Each notebook checks its output before writing and records the run in `silver_run_log`.

**Lineage columns on Silver tables:** `_source_dataset_id`, `_source_file`, `_source_sha256`, `_bronze_run_id` (the Bronze run read), `_silver_run_id` (the Silver run that wrote the row) and `_processed_at`.

### 3.1 Units and geography (`01_silver_geography`)

**`geo_reporting_unit`**: one row per reporting unit (100 rows). Key: `unit_psgc_code`. The source of Gold `dim_province`.

| Column | Description |
| --- | --- |
| `unit_psgc_code`, `unit_name` | Unit code and official name. |
| `unit_type` | `Province`, `HUC`, `Independent city` or `NCR`. |
| `region_code`, `region_name` | Region from the PSGC code (DL-003). |
| `census_population_ref`, `census_population_ref_year` | PSGC census population and its year. Reference only. |
| `dot_reported` | `true` when DOT reports the unit in at least one year. |
| `dot_first_year`, `dot_last_year` | First and last year DOT reports it. |
| `dot_breaks_comparability`, `dot_comparability_note` | Whether, and why, DOT's coverage of the unit changes across years (for example Boracay in Aklan). |
| `unit_note` | Notes on how the unit was formed, for example Lucena counted in Quezon (DL-011). |
| `psgc_version` | `2Q 2026`. |

**`geo_psgc`**: one row per PSGC entity (region, province, city, municipality, barangay), with `psgc_code`, `psgc_name`, `geographic_level`, `city_class`, `region_code`, `region_name`, `parent_province_code`, `unit_psgc_code` (the reporting unit it rolls up to), `correspondence_code`, `old_names`, `income_class`, `urban_rural_2020`, `population_2024`, `status`, `psgc_version` and `source_row_number`. Key: `psgc_code` (10 digits, unique; DQ-GEO-01).

**`map_dot_area_to_psgc`**: the reviewed DOT crosswalk seed, one row per printed DOT label and validity period. Key: (`dot_indent_level`, `dot_parent_label`, `dot_area_label`, `valid_from_year`). Main columns: `valid_to_year`, `row_role`, `unit_psgc_code`, `exclude_reason`, `breaks_comparability`. Column meanings are in [`resources/seeds/README.md`](../resources/seeds/README.md).

### 3.2 Tourism (`02_silver_dot`)

**`dot_travelers_unit_year`**: one row per unit and DOT year (100 × 6 = 600 rows). Key: (`unit_psgc_code`, `year`). The source of the tourism columns in Gold.

| Column | Type | Description |
| --- | --- | --- |
| `unit_psgc_code`, `unit_name`, `unit_type`, `region_code`, `region_name` | STRING | The unit. |
| `year` | INT | Year. |
| `foreign_travelers`, `overseas_filipinos`, `domestic_travelers`, `total_travelers` | BIGINT | Travelers summed from the DOT rows mapped to the unit. NULL when `not_reported`. |
| `traveler_value_status` | STRING | How the values were reported (DL-019). See [value lists](#8-value-lists). |
| `comparable_to_2019` | BOOLEAN | `false` when DOT counted the unit differently from 2019 that year (DL-020). |
| `comparability_note` | STRING | Which DOT rows break comparability. |
| `foreign_includes_overseas_filipinos` | BOOLEAN | `true` for the five Region II units (DL-030). |
| `contributing_rows`, `dash_total_rows`, `dash_cells_in_printed_rows` | integer | How many DOT rows fed the unit, how many had a `-` total, and how many `-` cells were inside printed rows. |
| `dot_labels` | STRING | The DOT labels summed into the unit. |

**`dot_travelers_row`**: one cleaned DOT region or province-level row per year, with its crosswalk role. For tracing and reconciliation. No enforced key: one row per printed DOT row and year.

**`dot_excluded_rows`**: one row per DOT row not loaded into any unit (SBMA, Cotabato City, Boracay double counts), with `exclude_reason`, `belongs_to_unit`, the traveler values and the source position (DL-013, DL-015, DL-016). Logical key: (`year`, `area_label`, `parent_label`).

### 3.3 Economy (`03_silver_psa_economy`)

**`psa_economy_unit_year`**: one row per unit and year, 2019-2023 (500 rows). Key: (`unit_psgc_code`, `year`).

| Column | Type | Unit | Description |
| --- | --- | --- | --- |
| `unit_psgc_code`, `unit_name`, `unit_type`, `region_code`, `region_name` | STRING | | The unit. |
| `year` | INT | | Year. |
| `gdp_total_current` | DECIMAL(20,0) | thousand PhP, current | GDP (PSA DS_27). |
| `gdp_total_constant` | DECIMAL(20,0) | thousand PhP, 2018 prices | GDP (PSA DS_28). |
| `gdp_per_capita_current` | DECIMAL(20,0) | PhP, current | GDP per person (PSA DS_29). |
| `afs_gva_current` | DECIMAL(20,0) | thousand PhP, current | A&F gross value added (PSA DS_31). |
| `afs_gva_constant` | DECIMAL(20,0) | thousand PhP, 2018 prices | A&F gross value added (PSA DS_32). |
| `derived_values` | STRING | | Measures derived from a region total instead of published (DL-024). NULL when none. |
| `per_capita_recomputed` | BOOLEAN | | `true` when per-capita GDP was recomputed (Quezon with Lucena, DL-011). |

**`ref_indicator`**: one row per economy measure, with `measure`, `dataset_id`, `bronze_table`, `psa_table`, `title`, `unit`, `price_basis` and `additivity`. Gold uses it to write the unit into each column's comment. Key: `measure`.

**`psa_economy_row`**: one PSA value per dataset, printed row and year, with its role. For tracing and reconciliation. No enforced key: one row per dataset, printed row and year. **`map_psa_area_to_psgc`**: the reviewed PSA crosswalk seed. Key: `psa_label` (checked by DQ-PSA-10).

### 3.4 Population (`04_silver_population`)

**`population_unit_year`**: one row per unit and year, 2019-2024 (600 rows). Key: (`unit_psgc_code`, `year`).

| Column | Type | Description |
| --- | --- | --- |
| `unit_psgc_code`, `unit_name`, `unit_type`, `region_code`, `region_name` | STRING | The unit. |
| `year` | INT | Year. |
| `population_total` | BIGINT | Projected mid-year population (PSA DS_18, DL-021). |
| `population_source` | STRING | Which file and method gave the value. See [value lists](#8-value-lists). |
| `population_note` | STRING | For provinces with HUCs, which HUCs were subtracted and their total. |
| `source_reference` | STRING | Every DS_18 row used for the value. |

**`population_row`**: one DS_18 value used, per source table, printed row and year. No enforced key: one row per source table, printed row and year. **`map_psa_population_area_to_psgc`**: the reviewed population crosswalk seed. Key: (`source_table`, `block_label`, `area_label`).

### 3.5 `silver_run_log`

One row per Silver notebook run, keyed by `run_id`: `run_id`, `notebook_name`, `started_at`, `completed_at`, `tables_written`, `rows_written`, `dq_checks_run`, `dq_block_failures`, `dq_review_flags`, `status` (`STARTED`, `SUCCESS`, `SUCCESS_WITH_REVIEW` or `FAILED`) and `notes`.

---

## 4. `03_gold` → `04_gold`

A star schema. Gold copies values from Silver without recomputing them. Units are also stored as column comments.

### 4.1 `dim_province`

One row per reporting unit (100 rows). Key: `province_psgc`. Built by `01_gold_dim_province`.

| Column | Description |
| --- | --- |
| `province_psgc` | PSGC 2Q 2026 code. Primary key. |
| `province_name` | Official PSGC name. |
| `unit_type` | `Province`, `HUC`, `Independent city` or `NCR`. |
| `region_psgc`, `region_name` | Region (DL-003). |
| `city_class` | HUC, independent component city or component city. NULL for provinces and NCR. |
| `comparability_note` | Why DOT's coverage of the unit changes across years. NULL when stable. |
| `psgc_snapshot` | `2Q 2026`. |
| `census_population_ref`, `census_population_ref_year` | PSGC census population and year. Reference only; never a denominator. |
| `latitude`, `longitude` | One map point per unit, from `resources/seeds/map_unit_coordinates.csv` (checked by DQ-GLD-01g). |

### 4.2 `dim_year`

One row per year, 2019-2024 (6 rows). Key: `year`. Built by `02_gold_dim_year`.

| Column | Type | Description |
| --- | --- | --- |
| `year` | INT | Year. Primary key. |
| `is_baseline_year` | BOOLEAN | `true` for 2019 (DL-004). Used by the supporting recovery tables. |
| `is_recovery_year` | BOOLEAN | `true` for 2022 and 2023. Used by the supporting recovery tables. |
| `in_comparison_window` | BOOLEAN | `true` for 2019-2023. |
| `has_all_sources` | BOOLEAN | DOT, PSA economy and population all have data that year (2019-2023). |
| `has_dot`, `has_psa_economy`, `has_population` | BOOLEAN | That source has data for at least one unit that year. Year-level only. |

### 4.3 `fact_province_year`

One row per unit and year (100 × 6 = 600 rows). Key: (`province_psgc`, `year`). Built by `03_gold_fact_province_year` from the three Silver unit-year tables. Years a source doesn't cover are NULL.

| Column | Type | Unit | Description |
| --- | --- | --- | --- |
| `province_psgc` | STRING | | Unit. Foreign key to `dim_province`. |
| `year` | INT | | Year. Foreign key to `dim_year`. |
| `foreign_travelers`, `overseas_filipinos`, `domestic_travelers`, `total_travelers` | BIGINT | travelers | From `dot_travelers_unit_year`. |
| `traveler_value_status` | STRING | | DL-019. Never NULL in a DOT year. When `not_reported`, all four traveler columns are NULL. |
| `foreign_includes_overseas_filipinos` | BOOLEAN | | DL-030. |
| `gdp_total_current` | DECIMAL(20,0) | thousand PhP, current | From `psa_economy_unit_year`. |
| `gdp_total_constant` | DECIMAL(20,0) | thousand PhP, 2018 prices | |
| `gdp_per_capita_current` | DECIMAL(20,0) | PhP, current | |
| `afs_gva_current` | DECIMAL(20,0) | thousand PhP, current | |
| `afs_gva_constant` | DECIMAL(20,0) | thousand PhP, 2018 prices | |
| `derived_values` | STRING | | DL-024. Currently `afs_gva_constant` for the City of Tacloban, 2019-2023. |
| `per_capita_recomputed` | BOOLEAN | | DL-011. Currently Quezon, 2019-2023. |
| `population_total` | BIGINT | persons | From `population_unit_year`. |
| `population_source` | STRING | | See [value lists](#8-value-lists). |
| `comparable_to_2019` | BOOLEAN | | DL-020. Also `true` for units DOT doesn't report, so always combine with `traveler_value_status <> 'not_reported'`. |
| `built_at` | TIMESTAMP | | When the Gold run built the table. |

### 4.4 `gold_run_log`

One row per Gold notebook run, keyed by `run_id`. Same columns as `silver_run_log`.

---

## 5. `04_analytics` → `05_analytics`

Built by `01_build_analytics` and checked by `02_analytics_validation`; summarized by `03_analytics_run_evidence`. 958 rows in total on the 21 October 2026 run.

| Table | Grain | Rows | Answers |
| --- | --- | --: | --- |
| [`tourism_activity`](#52-tourism_activity) | Unit × year | 600 | AQ1, and the input for the leading destinations |
| [`tourism_concentration`](#53-tourism_concentration) | Year | 6 | AQ1 |
| [`tourism_economy`](#54-tourism_economy) | Unit | 100 | AQ2 to AQ4 |
| [`tourism_recovery`](#55-tourism_recovery) | Unit × comparison year | 200 | Supporting context (dashboard appendix) |
| [`traveler_segment_recovery`](#56-traveler_segment_recovery) | Unit, 2023 below-2019 cohort | 52 | Supporting context (dashboard appendix) |

### 5.1 Lineage columns (every Analytics table)

| Column | Type | Description |
| --- | --- | --- |
| `_analytics_run_id` | STRING | The build run that wrote the row, for example `analytics_20261021_005954_d19b1b91`. The same in all five tables. |
| `_gold_fact_version` | integer | Delta version of `fact_province_year` that the build read. |
| `_gold_dim_province_version` | integer | Delta version of `dim_province` that the build read. |
| `_gold_dim_year_version` | integer | Delta version of `dim_year` that the build read. |
| `_processed_at` | TIMESTAMP | When the build ran. One value for the whole run. |

To reproduce a value exactly, read Gold `VERSION AS OF` the recorded versions.

### 5.2 `tourism_activity`

One row per unit and year (600 rows). Key: (`province_psgc`, `year`).

**Copied from Gold**, with the same meaning: `province_psgc`, `province_name`, `unit_type`, `region_psgc`, `region_name`, `year`, `total_travelers`, `population_total`, `population_source`, `traveler_value_status`, `comparable_to_2019`, `comparability_note`, `foreign_includes_overseas_filipinos`, `latitude`, `longitude`, `derived_values`, `per_capita_recomputed`.

| Column | Type | Description |
| --- | --- | --- |
| `activity_eligible` | BOOLEAN | `total_travelers` is not NULL and DOT reported the unit that year. A reported 0 is eligible; `reported_partial` rows are eligible, with the status as a caveat. |
| `activity_exclusion_reason` | STRING | `Not reported by DOT` or `Total travelers is NULL`. NULL when eligible. |
| `intensity_eligible` | BOOLEAN | `activity_eligible` and `population_total` greater than 0. |
| `intensity_exclusion_reason` | STRING | Why intensity is not calculated. |
| `tourism_intensity_per_1000` | DOUBLE | **Tourism intensity**: `total_travelers ÷ population_total × 1,000`. |
| `tourism_rank` | INT | Rank by `total_travelers` within the year, 1 = most. Eligible rows only; ties share a rank. |
| `intensity_rank` | INT | Rank by `tourism_intensity_per_1000` within the year. |
| `tourism_share_pct` | DOUBLE | The unit's travelers ÷ all eligible travelers that year × 100. |
| `tourism_rank_2019` | INT | The unit's 2019 `tourism_rank`, repeated on every year. Supporting context. |
| `usual_strong_destination_2019` | BOOLEAN | `tourism_rank_2019` ≤ 10. Superseded for the business question by the leading destinations (DL-026 → DL-032); kept for the recovery appendix. |

### 5.3 `tourism_concentration`

One row per year (6 rows). Key: `year`. "Top 5" and "top 10" here are the busiest units **in that year**, not the leading destinations.

| Column | Type | Description |
| --- | --- | --- |
| `year` | INT | Year. |
| `eligible_reporting_unit_count` | BIGINT | Units with `activity_eligible` that year. |
| `excluded_reporting_unit_count` | BIGINT | 100 minus the eligible count. |
| `eligible_total_travelers` | BIGINT | Sum of travelers over eligible units. |
| `top_5_travelers`, `top_5_unit_count` | BIGINT | Travelers in the 5 busiest units that year, and how many units that is. |
| `top_5_share_pct` | DOUBLE | `top_5_travelers ÷ eligible_total_travelers × 100`. |
| `top_10_travelers`, `top_10_unit_count` | BIGINT | Travelers in the 10 busiest units that year, and how many units that is. |
| `top_10_share_pct` | DOUBLE | `top_10_travelers ÷ eligible_total_travelers × 100`. |

### 5.4 `tourism_economy`

One row per unit (100 rows). Key: `province_psgc`, with `baseline_year` = 2019 and `comparison_year` = 2023. Columns the business question uses are marked **BQ**.

**Unit**

| Column | Description |
| --- | --- |
| `province_psgc`, `province_name`, `unit_type`, `region_psgc`, `region_name`, `comparability_note`, `latitude`, `longitude` | From `dim_province`. **BQ** |
| `baseline_year`, `comparison_year` | Always 2019 and 2023. |

**Tourism**

| Column | Type | Description |
| --- | --- | --- |
| `travelers_2019`, `travelers_2023` | BIGINT | Total travelers. `travelers_2023` is **BQ**. |
| `travelers_2020` | BIGINT | Used only for `baseline_under_review_2019`. |
| `status_2019`, `status_2023` | STRING | `traveler_value_status`. `status_2023` is **BQ**. |
| `comp_2019`, `comp_2023` | BOOLEAN | `comparable_to_2019`. |
| `population_total_2023`, `population_source_2023` | BIGINT, STRING | 2023 population and its source. |
| `tourism_intensity_eligible` | BOOLEAN | 2023 travelers and population available, population greater than 0. |
| `tourism_intensity_per_1000_2023` | DOUBLE | 2023 travelers per 1,000 residents. |
| `tourism_intensity_exclusion_reason` | STRING | Why 2023 intensity is not calculated. |

**Economy**

| Column | Type | Unit | Description |
| --- | --- | --- | --- |
| `afs_gva_current_2023` | DECIMAL(20,0) | thousand PhP, current | 2023 A&F GVA, the numerator of output per visitor. **BQ** |
| `gdp_total_current_2023` | DECIMAL(20,0) | thousand PhP, current | 2023 GDP. |
| `gdp_per_capita_current_2023` | DECIMAL(20,0) | PhP, current | 2023 GDP per capita; decides lower-income (DL-035). **BQ** |
| `gdp_per_capita_current_2019` | DECIMAL(20,0) | PhP, current | Supporting only (DL-027, superseded). |
| `afs_gva_constant_2019`, `afs_gva_constant_2023` | DECIMAL(20,0) | thousand PhP, 2018 prices | For A&F growth. |
| `afs_share_eligible` | BOOLEAN | | 2023 A&F GVA and GDP available, GDP greater than 0. |
| `afs_share_of_gdp_pct` | DOUBLE | % | **Tourism share of the economy**: `afs_gva_current_2023 ÷ gdp_total_current_2023 × 100`. **BQ**, context only. |
| `afs_share_exclusion_reason` | STRING | | Why the share is not calculated. |
| `derived_values_2019`, `derived_values_2023` | STRING | | DL-024. |
| `per_capita_recomputed_2019`, `per_capita_recomputed_2023` | BOOLEAN | | DL-011. |

**Change 2019 to 2023 (supporting)**

| Column | Type | Description |
| --- | --- | --- |
| `tourism_change_eligible` | BOOLEAN | Same rule as 2023 recovery eligibility. |
| `tourism_change_pct` | DOUBLE | `(travelers_2023 - travelers_2019) ÷ travelers_2019 × 100`. |
| `tourism_change_exclusion_reason` | STRING | Why tourism change is not calculated. |
| `afs_growth_eligible` | BOOLEAN | Both constant-price A&F values available, 2019 greater than 0. |
| `afs_gva_growth_pct` | DOUBLE | `(afs_gva_constant_2023 - afs_gva_constant_2019) ÷ afs_gva_constant_2019 × 100`. |
| `afs_growth_exclusion_reason` | STRING | Why A&F growth is not calculated. |
| `tourism_direction`, `economy_direction` | STRING | `up`, `down` or `unchanged`, on unrounded values (DL-022). |
| `alignment_eligible` | BOOLEAN | Both changes are eligible. |
| `tourism_economy_pattern` | STRING | Code for the pair, for example `tourism_up_economy_down`. |
| `tourism_economy_pattern_label` | STRING | The same in words. |
| `alignment_exclusion_reason` | STRING | Why no pattern is assigned. |

**Copied from the recovery tables (supporting)**: `recovery_index_2022`, `recovery_class_2022`, `recovery_eligible_2022`, `recovery_exclusion_reason_2022`, the same four for 2023, `tourism_rank_2019`, `usual_strong_destination_2019`, `baseline_under_review_2019`, `baseline_review_reason`, `small_base_2019`, `destination_label`, `destination_label_reason`. See [5.5](#55-tourism_recovery).

### 5.5 `tourism_recovery`

One row per unit and comparison year, 2022 and 2023 (200 rows). Key: (`province_psgc`, `baseline_year`, `comparison_year`). **Supporting context only** (DL-031); shown in the dashboard appendix.

| Column | Type | Description |
| --- | --- | --- |
| `province_psgc`, `province_name`, `unit_type`, `region_psgc`, `region_name`, `comparability_note` | STRING | From `dim_province`. |
| `baseline_year`, `comparison_year` | INT | 2019, and 2022 or 2023. |
| `travelers_2019`, `travelers_comparison_year` | BIGINT | Total travelers in each year. |
| `status_2019`, `status_comparison`, `comp_2019`, `comp_comparison` | | Status and comparability in each year. |
| `foreign_includes_overseas_filipinos` | BOOLEAN | Comparison-year flag. |
| `derived_values_2019`, `derived_values_comparison`, `per_capita_recomputed_2019`, `per_capita_recomputed_comparison` | | Caveats from Gold. |
| `recovery_eligible` | BOOLEAN | Both years reported and comparable, 2019 greater than 0, comparison year not negative. |
| `recovery_exclusion_reason` | STRING | Why recovery is not calculated. |
| `traveler_change_absolute` | BIGINT | `travelers_comparison_year - travelers_2019`. |
| `recovery_index` | DOUBLE | `travelers_comparison_year ÷ travelers_2019 × 100`. |
| `recovery_class` | STRING | `above_2019`, `unchanged` or `below_2019`, on the unrounded index. |
| `travelers_2020`, `status_2020` | | 2020 values, for the baseline review. |
| `baseline_under_review_2019` | BOOLEAN | 2020 travelers higher than 2019, which suggests an undercounted 2019 base (DL-029). |
| `baseline_review_reason` | STRING | Reason text. |
| `small_base_2019` | BOOLEAN | 2019 travelers below 10,000 (DL-028). Not the same as the 2023 small base (DL-036). |
| `tourism_rank_2019`, `usual_strong_destination_2019` | | From `tourism_activity`. |
| `destination_label` | STRING | 2023 rows only: `under_review` or `possible_emerging` under DL-028; otherwise NULL. Not used by the business question. |
| `destination_label_reason` | STRING | Why the label was given. |

### 5.6 `traveler_segment_recovery`

One row per unit that was recovery-eligible and **below its 2019 level in 2023** (52 rows). Key: (`province_psgc`, `baseline_year`, `comparison_year`). **Supporting context only.**

| Column | Description |
| --- | --- |
| `province_psgc`, `province_name`, `unit_type`, `region_psgc`, `region_name`, `comparability_note` | From `dim_province`. |
| `baseline_year`, `comparison_year` | 2019 and 2023. |
| `below_2019` | Always `true`. |
| `overall_recovery_index`, `overall_recovery_class` | The unit's 2023 overall recovery. |
| `travelers_2019`, `travelers_2023`, `comparable_to_2019` | Overall travelers and the 2023 comparability flag. |
| `foreign_includes_overseas_filipinos` | When `true`, foreign and overseas Filipino recovery are not calculated (DL-030). |
| `derived_values_2019`, `per_capita_recomputed_2019`, `derived_values_2023`, `per_capita_recomputed_2023` | Caveats from Gold. |

For each segment (`domestic`, `foreign`, `overseas_filipino`):

| Column | Type | Description |
| --- | --- | --- |
| `<segment>_travelers_2019`, `<segment>_travelers_2023` | BIGINT | Segment travelers. |
| `<segment>_eligible` | BOOLEAN | 2019 greater than 0 and 2023 not negative (and the Region II flag is `false` for foreign and overseas Filipino). |
| `<segment>_exclusion_reason` | STRING | Why the segment is not calculated. |
| `<segment>_recovery_index` | DOUBLE | 2023 ÷ 2019 × 100. |
| `<segment>_recovery_class` | STRING | `above_2019`, `unchanged` or `below_2019`. |
| `<segment>_small_base` | BOOLEAN | 2019 segment travelers below 1,000 (DL-028). |

### 5.7 `analytics_run_log`

One row per Analytics notebook run, keyed by `run_id`, with the same fields in the same order as `silver_run_log` (run ID, notebook, start, end, tables written, rows written, checks run, BLOCK failures, REVIEW flags, status, notes). `01_build_analytics` writes to it but doesn't create it, so check the column names with `DESCRIBE TABLE`.

---

## 6. Dashboard: `ds_profile`

The dashboard dataset `ds_profile` (`dashboard/datasets/05_profile_2023.sql`) derives the 2023 province profile from `tourism_activity` and `tourism_economy`. It is not stored as a table; it runs when the dashboard refreshes (`refresh_dashboard`, the job's last task). Pages 2 to 4 use it, and `ds_aq3_table` and `ds_aq4_table` use the same logic. One row per unit (100 rows). Key: `place`, the unit's PSGC name, which is unique across the 100 units (the dataset does not include `province_psgc`).

| Field | Description |
| --- | --- |
| `place` | `province_name`. |
| `region_name`, `unit_type`, `latitude`, `longitude` | From `tourism_economy`. |
| `is_leading_destination` | **Leading destination**: one of the 10 units with the highest average annual travelers over eligible years, 2019-2023 (DL-032). |
| `destination_group` | `Leading destinations` or `Beyond the leading destinations`. |
| `travelers_2023` | 2023 overnight travelers. |
| `earnings_per_visitor` | **Output per visitor**, PhP: `afs_gva_current_2023 × 1,000 ÷ travelers_2023` (DL-033). NULL when 2023 travelers are not reported or 0, or A&F GVA is missing. Rounded to whole pesos. |
| `small_base_2023` | **Small base**: fewer than 10,000 travelers in 2023, shown as "Check before naming" (DL-036). |
| `afs_share_of_gdp_pct` | Tourism share of the economy, %, for context. |
| `gdp_per_capita_thousand` | 2023 GDP per capita in thousand PhP, 1 decimal. |
| `is_lagging` | **Lower-income**: 2023 GDP per capita below the median of all 100 units (₱140,165 in 2023, DL-035). |
| `wealth_group` | `Lagging (below-median GDP per capita)` or `Not lagging`. |
| `is_high_output` | Output per visitor at or above the 2023 median (₱8,652). |
| `group_label` | **Province group** against the 2023 medians of travelers (279,150) and output per visitor (DL-034). See [value lists](#8-value-lists). |
| `map_group` | `Leading destination` for leading destinations, otherwise `group_label`. |
| `what_the_data_shows` | The group in words, for example "Few visitors, but high output per visitor". |
| `what_to_look_at` | The question shown for the group, for example "What keeps visitor numbers low?" (DL-037). |

The travelers and output-per-visitor medians are taken over units with both values in 2023. The GDP per capita median uses all 100 units.

---

## 7. Data quality: `06_data_quality`

### `dq_results`

No unique key: several rows can share a `run_id` and `check_id` (for example one row per recomputed column in Analytics). To find the rows for one check, filter on `run_id` and `check_id`; `notes` names the specific Analytics check. Rows come from every Silver, Gold and Analytics notebook.

| Column | Type | Description |
| --- | --- | --- |
| `run_id` | STRING | The notebook run that ran the check. |
| `notebook_name` | STRING | Notebook, for example `02_silver_dot`. |
| `check_id` | STRING | Documented ID: `DQ-COM`, `DQ-DOT`, `DQ-PSA`, `DQ-POP` (Silver), `DQ-GLD` (Gold) or `DQ-ANL` (Analytics). See [data-quality rules](data-quality-rules.md). |
| `table_name` | STRING | The table checked, or `cross-table`. |
| `severity` | STRING | `BLOCK`, `REVIEW` or `LOG`. |
| `status` | STRING | `PASS` or `FAIL`. |
| `failed_rows` | BIGINT | Number of rows that failed. |
| `expected`, `observed` | STRING | What the check expected and what it found. |
| `sample_keys` | STRING | Up to 20 keys of failing rows. |
| `checked_at` | TIMESTAMP | When the check ran. |
| `notes` | STRING | Extra context. For Analytics, the check's original name, since several checks can share one ID. |

---

## 8. Value lists

### `traveler_value_status` (DL-019)

| Value | Meaning | Travelers |
| --- | --- | --- |
| `reported` | Every contributing DOT row was printed, with no `-` cells. | Sum of the rows |
| `dash_as_zero` | Every row was printed; some `-` cells inside a printed total were counted as 0. | Sum of the rows |
| `reported_partial` | Some contributing rows have a `-` total (NCR every year, Sorsogon 2019). | Sum of the printed rows, with the status as a caveat |
| `not_reported` | No contributing row has a printed total, or DOT has no row for the unit (BARMM provinces and Sulu every year; Abra in 2023). | NULL |

### `population_source` (DL-021)

| Value | Meaning |
| --- | --- |
| `ds18_excel` | DS_18 Excel total: provinces without a separate HUC, Quezon, City of Isabela, NCR. |
| `ds18_pdf` | DS_18 PDF row, for the 16 HUCs, 2020-2024. |
| `estimated_from_2020_trend` | 2019 value for the 16 HUCs, estimated from their 2020 to 2021 trend. |
| `ds18_excel_minus_huc` | Province total minus its HUCs from the PDF, 2020-2024. |
| `ds18_excel_minus_estimated_huc` | Province total minus its estimated HUCs, 2019. |
| NULL | No value: Maguindanao del Norte and del Sur, which DS_18 prints as one Maguindanao before the 2022 split. |

### `unit_type` (DL-010)

| Value | Count |
| --- | --: |
| `Province` | 82 (including the 5 BARMM provinces and Sulu, which DOT doesn't report) |
| `HUC` | 16 (outside NCR, except Lucena, which is counted in Quezon) |
| `Independent city` | 1 (City of Isabela) |
| `NCR` | 1 |

### Province groups (`group_label`, DL-034)

| Group | Travelers vs median | Output per visitor vs median | Gap the data shows | What to look at |
| --- | --- | --- | --- | --- |
| `Established` | At or above | At or above | None on these two measures | Do the benefits reach nearby provinces? |
| `Busy but low-output` | At or above | Below | Output per visitor | Where does visitor spending go? |
| `Small but high-output` | Below | At or above | Visitor numbers | What keeps visitor numbers low? |
| `Limited activity` | Below | Below | Both | How does tourism compare with other sectors here? |
| `Insufficient data` | No output per visitor | | Not placed in a group | |

### Other codes

| Column | Values |
| --- | --- |
| `recovery_class`, `<segment>_recovery_class` | `above_2019` (index > 100), `unchanged` (= 100), `below_2019` (< 100) |
| `tourism_direction`, `economy_direction` | `up`, `down`, `unchanged` |
| `destination_label` | `under_review`, `possible_emerging`, NULL |
| Run log `status` | `STARTED`, `SUCCESS`, `SUCCESS_WITH_REVIEW`, `PARTIAL_SUCCESS` (ingestion only), `FAILED` |
| `file_manifest.status` | `DISCOVERED`, `INGESTED`, `SKIPPED`, `NEEDS_REVIEW`, `FAILED` |
| `dq_results.severity` | `BLOCK`, `REVIEW`, `LOG` |
