# Data Quality Rules and Failure Policy

Every Silver table is checked before it is written, and every check has an ID, a severity and a pre-agreed action when it fails. A failure is never handled ad hoc. This document lists the checks the Silver notebooks run today, so the IDs in `06_data_quality.dq_results` can be looked up here (Issue #5).

**Covers:** `00_silver_setup`, `01_silver_geography`, `02_silver_dot`, `03_silver_psa_economy`, `04_silver_population`. Gold checks are listed as planned at the end.

---

## 1. Failure policy

| Severity | What happens when the check fails | When to use it |
| --- | --- | --- |
| **BLOCK** | The notebook writes its check results, writes **no** Silver table, logs the run as `FAILED` and raises an error. The previous Silver tables stay as they were, and the job stops. | The output would be wrong or misleading (double counting, broken keys, missing shown as zero, totals that do not reconcile). |
| **REVIEW** | The run continues and is logged as `SUCCESS_WITH_REVIEW`. The failure must be looked at before Gold is published. | The data may be valid but needs a person to decide (outliers, a source that changed, an unexpected flag). |
| **LOG** | Recorded only; always `PASS`. Used to list things for the record. | Known, documented conditions (derived values, estimates, unused seed rows). |

* A BLOCK check is downgraded only through a decision-log entry.
* An expected exception is written into the check (an expected list or a tolerance, see section 5), not ignored after the fact. When the exception changes, the check is changed in a PR.

## 2. How the checks run

All Silver notebooks follow the same pattern:

1. A `STARTED` row is written to `03_silver.silver_run_log`.
2. The Silver tables are built **in memory** from Bronze and the reviewed seeds.
3. Every check runs and is recorded with `dq(...)`.
4. All results are appended to `06_data_quality.dq_results`, pass or fail.
5. If any BLOCK check failed, the run is logged as `FAILED` and the notebook raises an error. Otherwise each Silver table is **overwritten** (so a rerun gives the same result), and the run is logged as `SUCCESS` or `SUCCESS_WITH_REVIEW`.

## 3. Where results are stored

**`tuklas_dev.06_data_quality.dq_results`:** one row per check per run (created by `00_silver_setup`).

| Column | Meaning |
| --- | --- |
| `run_id` | Run that evaluated the check (same ID as in `silver_run_log`) |
| `notebook_name` | Notebook that ran it |
| `check_id` | ID from section 6 (e.g. `DQ-DOT-15`) |
| `table_name` | Table or input checked |
| `severity` | `BLOCK`, `REVIEW` or `LOG` |
| `status` | `PASS` or `FAIL` |
| `failed_rows` | Rows (or groups) that failed; 0 = `PASS` |
| `expected`, `observed` | Expected and observed result, as text |
| `sample_keys` | Up to 20 failing keys (or, for LOG checks, the listed items) |
| `checked_at` | When the check ran |
| `notes` | Free text (e.g. known exceptions excluded from the count) |

**`tuklas_dev.03_silver.silver_run_log`:** one row per notebook run, with `status` (`STARTED`, `SUCCESS`, `SUCCESS_WITH_REVIEW`, `FAILED`), `dq_checks_run`, `dq_block_failures` and `dq_review_flags`.

Latest results for one notebook:

```sql
SELECT check_id, severity, status, failed_rows, observed, sample_keys
FROM tuklas_dev.`06_data_quality`.dq_results
WHERE notebook_name = '04_silver_population'
  AND run_id = (SELECT max(run_id) FROM tuklas_dev.`03_silver`.silver_run_log
                WHERE notebook_name = '04_silver_population')
ORDER BY check_id;
```

Everything that needs attention across the latest run of every notebook:

```sql
WITH latest AS (
  SELECT notebook_name, max(run_id) AS run_id
  FROM tuklas_dev.`03_silver`.silver_run_log GROUP BY notebook_name)
SELECT d.notebook_name, d.check_id, d.severity, d.observed, d.sample_keys
FROM tuklas_dev.`06_data_quality`.dq_results d JOIN latest l USING (notebook_name, run_id)
WHERE d.status = 'FAIL'
ORDER BY d.severity, d.notebook_name, d.check_id;
```

## 4. Check IDs

| Prefix | Area | Defined in |
| --- | --- | --- |
| `DQ-COM` | Common checks, same meaning in every notebook | several |
| `DQ-GEO` | PSGC geography and reporting units | `01_silver_geography` |
| `DQ-XW` | DOT → PSGC crosswalk seed | `01_silver_geography` |
| `DQ-DOT` | DOT overnight travelers | `01_silver_geography`, `02_silver_dot` |
| `DQ-PSA` | PSA provincial accounts | `03_silver_psa_economy` |
| `DQ-POP` | DS_18 population | `04_silver_population` |
| `DQ-JOIN`, `DQ-GOLD` | Gold star and views | planned (section 8) |

IDs are never reused for a different check. Gaps in the numbering are draft IDs from the first version of this document that were merged into other checks or became decisions (section 9).

## 5. Thresholds and expected lists

These values are set in each notebook's **Configuration** cell. Changing one is a PR, and the reason goes in the PR description (or the decision log, if it changes a rule).

| Setting | Value | Used by | Notebook |
| --- | --- | --- | --- |
| `EXPECTED_LEVEL_COUNTS` | 18 regions, 82 provinces, 149 cities, 1,493 municipalities, 14 sub-municipalities, 42,010 barangays (PSGC 2Q 2026) | DQ-GEO-02 | `01_silver_geography` |
| `EXPECTED_UNIT_COUNTS` | 82 provinces, 16 HUCs, 1 independent city, NCR = 100 units (DL-010) | DQ-GEO-07 | `01_silver_geography` |
| `EXPECTED_UNITS_WITHOUT_DOT` | Basilan, Lanao del Sur, Tawi-Tawi, Maguindanao del Norte, Maguindanao del Sur, Sulu | DQ-DOT-09 | `01_silver_geography`, `02_silver_dot` |
| `EXPECTED_BREAK_UNITS` | Aklan (DL-013) | DQ-XW-06 | `01_silver_geography` |
| `EXPECTED_NOT_COMPARABLE` | Aklan 2021–2024 (DL-013, DL-020) | DQ-DOT-17 | `02_silver_dot` |
| `YOY_RATIO_REVIEW` | 5× up or down | DQ-DOT-11 | `02_silver_dot` |
| `PANDEMIC_SWING_YEARS` | 2020, 2021, 2022 (changes into these years are not flagged) | DQ-DOT-11 | `02_silver_dot` |
| `ROUNDING_TOLERANCE` | 5, in the table's unit (thousand PhP for GDP and GVA) | DQ-PSA-03, DQ-PSA-04 | `03_silver_psa_economy` |
| `DS26_TOLERANCE_PCT` | 2% (Table 3.63 is a later release) | DQ-PSA-06 | `03_silver_psa_economy` |
| `REGION_TOLERANCE` | 5 persons | DQ-POP-04, DQ-POP-06 | `04_silver_population` |
| `IMPLIED_TOLERANCE_PCT` | 0.5% | DQ-POP-11 | `04_silver_population` |
| `EXPECTED_NULL_UNITS` | Maguindanao del Norte, Maguindanao del Sur (population) | DQ-POP-07 | `04_silver_population` |
| `KNOWN_BOUNDARY_DIFF` | Cotabato (Special Geographic Area, proposed DL-025) | DQ-POP-11 | `04_silver_population` |

## 6. Checks by notebook

### 6.1 Common checks (`DQ-COM`)

| ID | Check | Severity | Run in |
| --- | --- | --- | --- |
| DQ-COM-02 | No NULL code or name | BLOCK | geography |
| DQ-COM-03 | One row per unit and year; row count = units × years | BLOCK | DOT (100 × 6), PSA economy (100 × 5), population (100 × 6) |
| DQ-COM-04 | Lineage filled on every unit-year that has values | BLOCK | DOT |
| DQ-COM-06 | Every value used converts to a number (DOT: a number or `-`; population: a whole number) | BLOCK | DOT, PSA economy, population |
| DQ-COM-07 | Values are NULL exactly when the status is `not_reported`; status uses the allowed values (DL-009, DL-019) | BLOCK | DOT |
| DQ-COM-09 | No Unicode replacement characters (`�`) in names | BLOCK | geography, PSA economy, population |

### 6.2 `01_silver_geography`

| ID | Check | Severity |
| --- | --- | --- |
| DQ-GEO-01 | PSGC codes are 10 digits and unique | BLOCK |
| DQ-GEO-02 | Entity counts per level match the 2Q 2026 release | REVIEW |
| DQ-GEO-03 | One PSGC source file (one version) for all years (DL-002, DL-003) | BLOCK |
| DQ-GEO-04 | Every city, municipality, sub-municipality and barangay rolls up to a unit (except the listed unitless areas) | BLOCK |
| DQ-GEO-05 | Every `region_code` is a PSGC region (region always comes from the code, DL-003) | BLOCK |
| DQ-GEO-07 | 100 reporting units, unique, with the expected type counts (DL-010) | BLOCK |
| DQ-GEO-08 | Every unit has a census population reference | REVIEW |
| DQ-XW-01 | Seed key unique; validity periods for the same label do not overlap | BLOCK |
| DQ-XW-02 | `row_role` and `exclude_reason` are valid; each role has its required fields | BLOCK |
| DQ-XW-03 | Seed `unit_psgc_code` is a reporting unit; `area_psgc_code` is a PSGC code | BLOCK |
| DQ-XW-04 | Seed rows that match no DOT Bronze row are listed | LOG |
| DQ-XW-05 | Every `breaks_comparability` seed row resolves to a reporting unit | BLOCK |
| DQ-XW-06 | The units flagged `dot_breaks_comparability` are exactly the expected ones (Aklan) | REVIEW |
| DQ-DOT-03 | Every DOT level-0/1 Bronze row matches exactly one seed row | BLOCK |
| DQ-DOT-05 | At most one `province_unit` row per unit per year | BLOCK |
| DQ-DOT-09 | Units without DOT rows are exactly the BARMM provinces and Sulu | REVIEW |
| DQ-DOT-15 | Per year: loaded rows + non-double-count exclusions = DOT `GRAND TOTAL` (`-` counted as 0) | BLOCK |

### 6.3 `02_silver_dot`

| ID | Check | Severity |
| --- | --- | --- |
| DQ-COM-03, 04, 06, 07 | See 6.1 | BLOCK |
| DQ-DOT-01 | Domestic + foreign + overseas Filipino = total in every printed row | BLOCK |
| DQ-DOT-03 | Every level-0/1 row has a crosswalk role | BLOCK |
| DQ-DOT-04 | Only level-0/1 rows are used (level-2 sub-rows are already inside their parent) | BLOCK |
| DQ-DOT-07 | Aklan counts Boracay once: 2019 = Aklan + Boracay rows; 2023 = Aklan row only (DL-013) | BLOCK |
| DQ-DOT-09 | BARMM provinces and Sulu are `not_reported`, never 0 | BLOCK |
| DQ-DOT-10 | Region II units carry the foreign / overseas Filipino flag | LOG |
| DQ-DOT-11 | Year-over-year change above 5× (or below 1/5), outside the pandemic swing | REVIEW |
| DQ-DOT-15 | Per year: units + non-double-count exclusions = DOT `GRAND TOTAL` | BLOCK |
| DQ-DOT-16 | Status counts from DL-019: 28 `not_reported` from `-` rows, 7 `reported_partial` | REVIEW |
| DQ-DOT-17 | `comparable_to_2019 = false` only for the expected unit-years (Aklan 2021–2024, DL-020) | REVIEW |

DOT grand totals that DQ-DOT-15 reconciles to (from the Bronze extraction):

| Year | Grand total |
| --- | --- |
| 2019 | 56,766,370 |
| 2020 | 11,873,332 |
| 2021 | 13,986,579 |
| 2022 | 39,947,584 |
| 2023 | 55,329,974 |
| 2024 | 63,867,806 |

### 6.4 `03_silver_psa_economy`

| ID | Check | Severity |
| --- | --- | --- |
| DQ-PSA-01 | Every Bronze label is in the seed `map_psa_area_to_psgc` | BLOCK |
| DQ-PSA-02 | Seed: every unit has exactly one `unit` row; every `unit` / `add_to_unit` code is a reporting unit | BLOCK |
| DQ-COM-06, 03, 09 | See 6.1 | BLOCK |
| DQ-PSA-03 | For every dataset, year and printed region: region total = sum of its rows (± rounding) | BLOCK |
| DQ-PSA-04 | NCR row = sum of the NCR city rows (± rounding, DL-012) | BLOCK |
| DQ-PSA-05 | Every unit-year has all five measures (after derivation) | REVIEW |
| DQ-PSA-06 | National A&F GVA 2022–2023 vs DS_26 (Table 3.63), within 2% | REVIEW |
| DQ-PSA-07 | Quezon's recomputed per-capita GDP lies between the published Quezon and Lucena values (DL-011) | BLOCK |
| DQ-PSA-08 | Values derived from a region total are listed (DL-024); each carries the lineage of the region-total row it comes from | LOG |
| DQ-PSA-09 | A&F GVA ≤ GDP for every unit-year, current and constant prices | BLOCK |
| DQ-PSA-10 | Each `psa_label` appears once in the seed (checked before the join, so a repeated label can't duplicate rows) | BLOCK |

The notebook also stops before any check if a table's year columns are not exactly 2019–2023, so a new year can't be loaded into one table but not the other.

### 6.5 `04_silver_population`

| ID | Check | Severity |
| --- | --- | --- |
| DQ-POP-01 | Every DS_18 Excel area label is in the seed `map_psa_population_area_to_psgc`, and every Excel seed label is found exactly once | BLOCK |
| DQ-POP-02 | Every PDF seed row is found exactly once (HUC and region rows inside their block) | BLOCK |
| DQ-POP-03 | Every Excel area row has its `Total` row right below it (`source_row_number`, DL-023) | BLOCK |
| DQ-COM-06, 03, 09 | See 6.1 | BLOCK |
| DQ-POP-04 | Excel: each region = sum of its rows, and PHILIPPINES = regions + NCR (± rounding), 2015–2025 | BLOCK |
| DQ-POP-05 | Every PDF area and region total equals the Excel total, 2020–2025 | BLOCK |
| DQ-POP-06 | PDF: each province with HUCs = sum of the rows printed in its block (± rounding), so its HUCs are inside the province total; all 14 × 6 province-years must be compared (a missing side fails) | REVIEW |
| DQ-POP-07 | Every unit-year has a population > 0, except Maguindanao del Norte and del Sur, which are NULL | BLOCK |
| DQ-POP-08 | Units + rows that are not units (Maguindanao, Cotabato City) = PHILIPPINES, every year (a missing year fails) | BLOCK |
| DQ-POP-09 | Each province with HUCs: province + its HUCs = DS_18 province total; all 14 × 6 province-years must be compared | BLOCK |
| DQ-POP-10 | The 2019 HUC estimates are listed (DL-021) | LOG |
| DQ-POP-11 | Population vs the population PSA used for its per-capita GDP (GDP × 1,000 ÷ per capita), 2019–2023, within 0.5% | REVIEW |

The notebook also stops before any check if `psa_ds_18` has no `source_row_number`, or if the year columns are not exactly 2015–2025 (Excel) and 2020–2025 (PDF).

## 7. Known exceptions register

Expected, documented conditions. Each one is built into a check (expected list or tolerance), so it doesn't raise a new failure on every run.

| Exception | Affected | Handling | Check | Reference |
| --- | --- | --- | --- | --- |
| No DOT data for BARMM and Sulu | Basilan, Lanao del Sur, Tawi-Tawi, Maguindanao del Norte, Maguindanao del Sur, Sulu | `not_reported`, NULL travelers | DQ-DOT-09 | DL-009, DL-010 |
| DOT `-` marker | 28 unit-years `not_reported` from `-` rows; 7 `reported_partial` (NCR every year, Sorsogon 2019) | `-` cell = 0; `-` row total = missing | DQ-COM-07, DQ-DOT-16 | DL-019 |
| Boracay counted at the Caticlan jetty from 2021 | Aklan 2021–2024 | `comparable_to_2019 = false` | DQ-XW-06, DQ-DOT-07, DQ-DOT-17 | DL-013, DL-020 |
| Clark Freeport Zone printed separately from 2023 | Pampanga 2023–2024 | Added to Pampanga; stays comparable | DQ-DOT-15 | DL-014 |
| SBMA and Cotabato City in DOT | SBMA / Subic Bay Freeport Zone, Cotabato City | Not loaded; kept in `dot_excluded_rows`; still counted in the grand-total reconciliation | DQ-DOT-15 | DL-015, DL-016 |
| Region II prints foreign and overseas Filipinos together | Region II units | `foreign_includes_overseas_filipinos = true` | DQ-DOT-10 | #33 |
| Large year-over-year changes outside the pandemic | Zamboanga Sibugay 2022→2023 and 2023→2024; City of Isabela 2022→2023 | Listed for review (DQ-DOT-11 is `FAIL` / REVIEW until the team decides) | DQ-DOT-11 | OI-5 |
| Lucena printed separately by PSA | Quezon | Added to Quezon; per-capita GDP recomputed | DQ-PSA-07 | DL-011 |
| City of Tacloban missing from DS_32 | Tacloban `afs_gva_constant`, 2019–2023 | Region VIII total − other rows; listed in `derived_values` | DQ-PSA-08 | DL-024 |
| DS_18 prints Maguindanao before the 2022 split | Maguindanao del Norte, del Sur (population) | NULL | DQ-POP-07 | #43 §7.4 |
| 2019 HUC population not published | 16 HUCs and their 14 provinces, 2019 | `estimated_from_2020_trend`; within 0.46% of PSA's own figure | DQ-POP-10, DQ-POP-11 | DL-021 |
| Cotabato covers a larger area in DS_18 than in the PSA economy tables | Cotabato (17.5–19.0% larger population, 2019–2023) | Excluded from the DQ-POP-11 count and shown in its notes; use PSA's published per-capita GDP for Cotabato | DQ-POP-11 | DL-025 (proposed) |

## 8. Planned for Gold (not yet implemented)

| ID | Check | Severity |
| --- | --- | --- |
| DQ-JOIN-01 | `fact_province_year` has one row per unit and year (100 × 6) and no orphan keys to `dim_province` or `dim_year` (#43 rule 3) | BLOCK |
| DQ-JOIN-02 | Every Silver unit-year is in the fact: DOT, PSA economy and population values copied without change | BLOCK |
| DQ-JOIN-03 | For each comparable unit and comparison year, tourism values exist for 2019 and that year, and economic values for 2019 and 2023; failures listed with the reason (#43 rule 7) | REVIEW |
| DQ-GOLD-01 | Shares use current-price columns only; growth uses constant-price columns only (#43 rule 8) | BLOCK |
| DQ-GOLD-02 | Units without comparable data are not placed in a quadrant (shown as insufficient data) | BLOCK |

## 9. Draft IDs not used

The first version of this document (Issue #5) proposed some IDs that are not checks today:

| Draft ID | Draft check | What happened |
| --- | --- | --- |
| DQ-COM-01 | Columns and types match the schema | Not implemented; types are set when each table is built |
| DQ-COM-05 | Bronze rows in = Silver rows out + excluded rows | Covered per source by the total reconciliations (DQ-DOT-15, DQ-PSA-03, DQ-POP-08) |
| DQ-COM-08 | Years outside 2019–2023 flagged | Replaced by the year-column checks in each notebook and `dim_year.in_comparison_window` |
| DQ-GEO-06 | `Prov Sum` sheet not used | A decision (#43 D2), not a check |
| DQ-DOT-02 | Region rows = grand total | Covered by DQ-DOT-15 |
| DQ-DOT-06 | Region taken from PSGC | Covered by DQ-GEO-05 |
| DQ-DOT-08 | Aklan flagged not comparable | Replaced by DQ-XW-05, DQ-XW-06 and DQ-DOT-17 |
| DQ-DOT-12 to 14 | Tarlac City 2020, component cities, economic zones | Decided in the crosswalk seed (DL-015 to DL-018) |

**Known overlap:** `DQ-DOT-09` means two related but different checks. In `01_silver_geography` (REVIEW), it checks that the units without DOT rows are exactly BARMM and Sulu. In `02_silver_dot` (BLOCK), it checks that those units are `not_reported` and never 0. `DQ-DOT-03` and `DQ-DOT-15` also run in both notebooks, with the same meaning. The geography version of `DQ-DOT-09` could be renamed `DQ-XW-07` in a later PR.

## 10. Adding or changing a check

1. Pick the next free number in the right prefix (never reuse an ID).
2. Add the `dq(...)` call **before** the write step, with a clear `expected` and `observed`, and up to 20 sample keys.
3. Add the check to the notebook's check table **and** to section 6 here.
4. If it encodes an expected exception, put the expected list or tolerance in the Configuration cell, and add a row to section 5 (and section 7 if it is a documented exception).
5. Run the notebook and paste its results into the PR.
