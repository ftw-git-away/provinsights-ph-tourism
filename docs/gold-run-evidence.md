# Gold Layer Run Evidence

This document records the successful Databricks execution of the Gold layer (`tuklas_dev`, schema `04_gold`). The results were produced by `04_gold_run_evidence`, which reads the Gold tables, `gold_run_log` and `dq_results`.

| | |
| --- | --- |
| **Run date** | 11 October 2026 |
| **Run by** | Charlene Mae Orogo |
| **Notebooks** | `00_gold_setup`, `01_gold_dim_province`, `02_gold_dim_year`, `03_gold_fact_province_year` |

## Summary

- `dim_province` holds 100 rows, `dim_year` holds 6 rows and `fact_province_year` holds 600 rows, as expected.
- All 23 checks passed: 22 BLOCK checks and 1 REVIEW check.
- The latest run of each notebook ended as `SUCCESS`, with no BLOCK failures.
- REVIEW flags: none. The only REVIEW check, `DQ-GLD-09` (total travelers is at least each component), passed with 0 violations.
- The fact table matches Silver row by row: 600 of 600 rows for DOT, 500 of 500 for PSA economy and 600 of 600 for population.

## Results

### Row counts

| table_name | rows | expected | ok |
| --- | --- | --- | --- |
| dim_province | 100 | 100 | True |
| dim_year | 6 | 6 | True |
| fact_province_year | 600 | 600 | True |

### Latest run per notebook

| notebook_name | run_id | status | tables_written | rows_written | dq_checks_run | dq_block_failures | dq_review_flags | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 01_gold_dim_province | gold_dim_province_20261011_154914_bd7fb645 | SUCCESS | 1 | 100 | 6 | 0 | 0 | dim_province=100; 6 checks, 0 for review. |
| 02_gold_dim_year | gold_dim_year_20261011_155436_36c15ce7 | SUCCESS | 1 | 6 | 5 | 0 | 0 | dim_year=6; 5 checks, 0 for review. |
| 03_gold_fact_province_year | gold_fact_province_year_20261011_160234_938f4d09 | SUCCESS | 1 | 600 | 12 | 0 | 0 | fact_province_year=600; 12 checks, 0 for review. |

### Check summary

| severity | status | count |
| --- | --- | --- |
| BLOCK | PASS | 22 |
| REVIEW | PASS | 1 |

> **Disclaimer:** The `REVIEW | PASS | 1` row does not mean a REVIEW flag was raised. It counts the one check with REVIEW severity (`DQ-GLD-09`, total travelers is at least each component), and that check passed. A REVIEW flag would appear as `REVIEW | FAIL`. No check failed in this run.

### All checks (failures first)

No check failed, so the list is in notebook order.

| notebook_name | check_id | severity | status | failed_rows | observed |
| --- | --- | --- | --- | --- | --- |
| 01_gold_dim_province | DQ-GLD-01 | BLOCK | PASS | 0 | 100 rows, 0 duplicates, 0 bad codes |
| 01_gold_dim_province | DQ-GLD-01b | BLOCK | PASS | 0 | 0 incomplete |
| 01_gold_dim_province | DQ-GLD-01c | BLOCK | PASS | 0 | 0 |
| 01_gold_dim_province | DQ-GLD-01d | BLOCK | PASS | 0 | ['2Q 2026'] |
| 01_gold_dim_province | DQ-GLD-01e | BLOCK | PASS | 0 | 100 units -> 100 rows |
| 01_gold_dim_province | DQ-GLD-01f | BLOCK | PASS | 0 | 0 missing |
| 02_gold_dim_year | DQ-GLD-02 | BLOCK | PASS | 0 | 6 years, 1 baseline, window [2019, 2020, 2021, 2022, 2023], recovery [2022, 2023] |
| 02_gold_dim_year | DQ-GLD-02b | BLOCK | PASS | 0 | 0 duplicates |
| 02_gold_dim_year | DQ-GLD-02c | BLOCK | PASS | 0 | flags [2019, 2020, 2021, 2022, 2023], Silver [2019, 2020, 2021, 2022, 2023] |
| 02_gold_dim_year | DQ-GLD-02d | BLOCK | PASS | 0 | missing: [] |
| 02_gold_dim_year | DQ-GLD-02e | BLOCK | PASS | 0 | {'dot_travelers_unit_year': 'int', 'psa_economy_unit_year': 'int', 'population_unit_year': 'int'} |
| 03_gold_fact_province_year | DQ-GLD-03 | BLOCK | PASS | 0 | 600 rows, 0 duplicates |
| 03_gold_fact_province_year | DQ-GLD-04 | BLOCK | PASS | 0 | 0 unknown provinces, 0 unknown years |
| 03_gold_fact_province_year | DQ-GLD-05 | BLOCK | PASS | 0 | 0 rows differ (none), 0 Silver rows missing, 600/600 rows matched |
| 03_gold_fact_province_year | DQ-GLD-06 | BLOCK | PASS | 0 | 0 rows differ (none), 0 Silver rows missing, 500/500 rows matched |
| 03_gold_fact_province_year | DQ-GLD-07 | BLOCK | PASS | 0 | 0 rows differ (none), 0 Silver rows missing, 600/600 rows matched |
| 03_gold_fact_province_year | DQ-GLD-08 | BLOCK | PASS | 0 | 0 bad statuses, 0 NULL statuses, 0 not_reported rows with a value |
| 03_gold_fact_province_year | DQ-GLD-09 | REVIEW | PASS | 0 | 0 violations |
| 03_gold_fact_province_year | DQ-GLD-10 | BLOCK | PASS | 0 | 0 violations |
| 03_gold_fact_province_year | DQ-GLD-11 | BLOCK | PASS | 0 | 0 rows fail (0 with a NULL status) |
| 03_gold_fact_province_year | DQ-GLD-12 | BLOCK | PASS | 0 | 0 values outside range |
| 03_gold_fact_province_year | DQ-GLD-13 | BLOCK | PASS | 0 | 0 units |
| 03_gold_fact_province_year | DQ-GLD-14 | BLOCK | PASS | 0 | all present |

### Sample fact rows

Province names come from a join to `dim_province`. The fact table carries `province_psgc` only.

| province_psgc | province_name | year | total_travelers | traveler_value_status | gdp_total_current | population_total | comparable_to_2019 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0102800000 | Ilocos Norte | 2019 | 520880 | dash_as_zero | 90997089 | 609740 | True |
| 0102800000 | Ilocos Norte | 2020 |  | not_reported | 85976653 | 613422 | True |
| 0102800000 | Ilocos Norte | 2021 |  | not_reported | 91717340 | 616858 | True |
| 0102800000 | Ilocos Norte | 2022 | 155584 | dash_as_zero | 105323439 | 620052 | True |
| 0102800000 | Ilocos Norte | 2023 | 515863 | dash_as_zero | 118721957 | 623004 | True |
| 0102800000 | Ilocos Norte | 2024 | 203795 | dash_as_zero |  | 625723 | True |
| 0102900000 | Ilocos Sur | 2019 | 397022 | dash_as_zero | 86196267 | 711063 | True |
| 0102900000 | Ilocos Sur | 2020 |  | not_reported | 80616299 | 715811 | True |

### Caveat fields

The three caveat fields carried over from Silver, and `comparable_to_2019`, are present in the fact table. The table below lists, for each caveat, the provinces it applies to and the years covered.

<paste the Caveat fields table from the evidence notebook here>

- `comparable_to_2019` is false for Aklan from 2021 onward, because DOT counts Aklan differently from 2019.
- `foreign_includes_overseas_filipinos` is true for provinces where DOT prints foreign travelers and overseas Filipinos together, such as Batanes and Cagayan.
- `derived_values` is filled for units where a value was derived from a printed region total, such as City of Tacloban.
- `per_capita_recomputed` is true for Quezon, where per-capita GDP is recomputed.

## Notes

- **Empty values are NULL, not 0.** In the sample, Ilocos Norte has `not_reported` in 2020 and 2021, so `total_travelers` is NULL in those years (DL-009, DL-019).
- **2024 has no PSA economy data.** `gdp_total_current` is NULL for 2024, so `has_psa_economy` and `has_all_sources` are false for 2024 in `dim_year`. The comparison window is 2019 to 2023.
- **Population is missing for two units.** Two of the 100 units have no population value in any year. Silver records the reason in `population_note`.

## Screenshots

<attach the screenshots of the run-log table and the check results>