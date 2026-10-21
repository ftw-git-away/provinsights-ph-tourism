# Analytics Layer Run Evidence (Issue #60)

This document confirms that the Analytics tables (`tuklas_dev`, schema `05_analytics`) are correct, consistent with Gold, and safe to use for downstream analysis. The results were produced by `03_analytics_run_evidence`, a read-only notebook that reads the Analytics tables, `05_analytics.analytics_run_log` and `06_data_quality.dq_results`.

> **Note:** Grain, keys, eligibility, classification, recomputation of every metric and reconciliation to Gold are checked by `01_build_analytics` and `02_analytics_validation`, which save their results to `dq_results` and `analytics_run_log`. This evidence reports those results without repeating them, and adds a comparison against the source files and a summary of exclusions, segment coverage and caveats.

| | |
| --- | --- |
| **Run date** | 21 October 2026 (UTC) |
| **Run by** | `Haze` |
| **Notebooks** | `01_build_analytics`, `02_analytics_validation`, `03_analytics_run_evidence` |
| **Build run** | `analytics_20261021_005954_d19b1b91` (SUCCESS) |
| **Validation run** | `analytics_validation_20261021_011314_56fc46bd` (SUCCESS) |
| **Gold versions** | fact_province_year `v152`, dim_province `v167`, dim_year `v109` |

## Summary

- **Build:** SUCCESS. 36 BLOCK checks and 6 REVIEW checks, all passed: 0 failures, 0 REVIEW findings. 5 tables, 958 rows written.
- **Validation:** SUCCESS. 148 BLOCK checks, all passed: 0 failures, 0 REVIEW findings.
- **Lineage:** all five tables carry the latest build run ID and the same Gold versions (v152 / v167 / v109); validation ran after the build.
- **Edge cases match the source files:** 80 of 80 values and 8 of 8 tourism–economy patterns.
- **Headline counts:** in 2023, 39 units are above 2019, 52 below and 9 not compared; 43 of 91 eligible units show tourism and A&F GVA moving in opposite directions.
- **Segment coverage (2023 below-2019 cohort of 52 units):** domestic 52/52, foreign 47/52, overseas Filipino 26/52.

## Results

### 1. Latest runs, checks and lineage

| notebook_name | run_id | status | tables_written | rows_written |
| --- | --- | --- | --: | --: |
| 01_build_analytics | analytics_20261021_005954_d19b1b91 | SUCCESS | 5 | 958 |
| 02_analytics_validation | analytics_validation_20261021_011314_56fc46bd | SUCCESS | 0 | 0 |

| notebook_name | severity | status | count |
| --- | --- | --- | --: |
| 01_build_analytics | BLOCK | PASS | 36 |
| 01_build_analytics | REVIEW | PASS | 6 |
| 02_analytics_validation | BLOCK | PASS | 148 |

All 190 checks passed. The five tables carry `_analytics_run_id = analytics_20261021_005954_d19b1b91` and Gold versions v152 / v167 / v109, and validation ran after the build.

> **Screenshots and detailed results in sections 2 and 3 below are from the 15 October 2026 run.** This run (21 October) has the same row counts (958), the same check counts (36 BLOCK + 6 REVIEW build, 148 BLOCK validation), and unchanged SQL; the edge-case values, headline counts and segment coverage are expected to be identical.

<img width="1182" height="158" alt="image" src="https://github.com/user-attachments/assets/68aea8ca-4e5e-4201-aeb8-c7ea1ec4f315" />

<img width="1178" height="257" alt="image" src="https://github.com/user-attachments/assets/3edfba6f-bd51-48a6-8dad-8746555761ad" />

<img width="1181" height="227" alt="image" src="https://github.com/user-attachments/assets/d197c735-9574-45ac-87c5-084f0d0c0985" />

<img width="1182" height="492" alt="image" src="https://github.com/user-attachments/assets/a15d0253-4cdb-44ee-84fc-be6c21b443f8" />

> In `dq_results`, a REVIEW check with status `FAIL` is a finding to review, not a failure.

### 2. Edge cases: Analytics vs source files

Expected values were calculated directly from DOT *Regional Distribution of Overnight Travelers* (2019, 2022, 2023), PSA Tables 3.72, 3.94 and 3.95, and PSA DS_18, applying DL-011, DL-013, DL-014, DL-019 and DL-021. Comparison tables are read at `baseline_year = 2019`. Traveler and population counts had to match exactly; % and per-1,000 values within 0.01.

**Result: 0 of 80 values differ; 8 of 8 patterns match.**

| Unit | Edge case | Travelers 2019 | Travelers 2023 | Intensity 2023 | Recovery Index 2022 | Recovery Index 2023 | Tourism change % | A&F growth % (constant) | A&F share % (current, 2023) | Pattern |
| --- | --- | --: | --: | --: | --: | --: | --: | --: | --: | --- |
| Aklan | Boracay; not comparable from 2021 | 2,251,966 | 2,200,138 | 3,544.36 | — | — | — | −35.05 | 3.24 | — |
| Pampanga | Clark added from 2023 | 910,666 | 1,655,887 | 671.56 | 123.45 | 181.83 | 81.83 | 6.50 | 2.65 | up / up |
| Quezon | Lucena inside Quezon | 1,301,486 | 1,264,181 | 543.01 | 91.15 | 97.13 | −2.87 | 50.57 | 4.05 | down / up |
| City of Baguio | Separately reported HUC | 1,536,458 | 1,309,930 | 3,527.25 | 67.84 | 85.26 | −14.74 | 9.35 | 9.96 | down / up |
| Abra | 2023 `not_reported` | 2,948 | — | — | 51.26 | — | — | 57.16 | 0.61 | — |
| Basilan | No DOT data | — | — | — | — | — | — | 0.84 | 0.10 | — |
| Aurora | Presentation example | 273,906 | 736,339 | 3,145.62 | 188.29 | 268.83 | 168.83 | −25.05 | 1.27 | up / down |
| Camiguin | Presentation example | 804,745 | 259,010 | 2,744.53 | 15.89 | 32.19 | −67.81 | −15.35 | 11.80 | down / down |

<img width="1182" height="461" alt="image" src="https://github.com/user-attachments/assets/71173063-50ac-4f63-b42f-56df622645ef" />

<img width="1182" height="312" alt="image" src="https://github.com/user-attachments/assets/fd6dfd00-6155-499e-8073-f9248d6c046b" />

**Sample calculations**
- **Pampanga, Recovery Index 2023:** (386,868 Pampanga + 1,269,019 Clark Freeport Zone) ÷ 910,666 × 100 = **181.83** (DL-014).
- **Aklan, travelers 2019:** 217,367 Aklan + 2,034,599 Boracay = **2,251,966**. No Recovery Index for 2022 or 2023, because Aklan is not comparable to 2019 from 2021 (DL-013).
- **Aurora, A&F growth:** 381,167 ÷ 508,545 − 1 = **−25.05%** (Table 3.95, constant prices). A match confirms growth uses constant prices.
- **Camiguin, A&F share:** A&F GVA ÷ GDP, 2023 (Tables 3.94 and 3.72, current prices) = **11.80%**. A match confirms share uses current prices.

**Trace (Analytics → Gold → Silver → source):** `02_analytics_validation` reconciles Analytics to Gold at the recorded Gold versions; the Gold run evidence reconciles Gold to Silver row by row (DQ-GLD-05 to 07); and this section reconciles Analytics to the source files for the units above.

### 3. Exclusions, segment coverage and caveats

**Recovery: units not compared, by reason**

| comparison_year | reason | count |
| --- | --- | --: |
| 2022 | 2019 travelers is NULL | 7 |
| 2022 | Comparison year travelers is NULL | 2 |
| 2022 | Comparison year not comparable to 2019 | 1 |
| 2023 | 2019 travelers is NULL | 7 |
| 2023 | Comparison year travelers is NULL | 1 |
| 2023 | Comparison year not comparable to 2019 | 1 |

- **2019 NULL (7):** the 5 BARMM provinces and Sulu (no DOT data) and Olongapo City (`not_reported` in 2019).
- **Comparison year NULL:** 2022: Angeles City and Davao Occidental; 2023: Abra (`not_reported`, DL-019).
- **Not comparable (1):** Aklan, from 2021 (DL-013, DL-020).

**Recovery classes**

| comparison_year | above_2019 | below_2019 | not compared |
| --- | --: | --: | --: |
| 2022 | 24 | 66 | 10 |
| 2023 | 39 | 52 | 9 |

No unit is exactly at 2019 (`unchanged`). Ineligible units stay NULL and are not forced into a class.

**Destination labels (2023)**

| destination_label | count |
| --- | --: |
| possible_emerging | 13 |
| under_review | 6 |
| no label | 81 |

<img width="1180" height="603" alt="image" src="https://github.com/user-attachments/assets/17cfc465-7361-45d3-9d71-c9d4ecbdbc00" />

**Tourism–economy patterns (2019–2023)**

| pattern | count |
| --- | --: |
| tourism_up_economy_up | 26 |
| tourism_down_economy_down | 22 |
| tourism_down_economy_up | 30 |
| tourism_up_economy_down | 13 |
| not eligible (tourism change not eligible) | 9 |

48 of 91 eligible units moved in the same direction and 43 in opposite directions.

<img width="1181" height="353" alt="image" src="https://github.com/user-attachments/assets/c170a044-96a4-4296-9f5a-bfebee0dc42c" />

**Traveler-segment coverage (2023 below-2019 cohort)**

| cohort_units | domestic_eligible | foreign_eligible | overseas_filipino_eligible | foreign_includes_overseas_filipinos |
| --: | --: | --: | --: | --: |
| 52 | 52 | 47 | 26 | 4 |

| segment | exclusion reason | count |
| --- | --- | --: |
| Foreign | Foreign includes overseas Filipinos for this unit | 4 |
| Foreign | 2019 foreign travelers printed as '-' by DOT | 1 |
| Overseas Filipino | 2019 overseas Filipinos printed as '-' by DOT | 22 |
| Overseas Filipino | Overseas Filipino included in foreign for this unit | 4 |

<img width="1181" height="387" alt="image" src="https://github.com/user-attachments/assets/52d2e539-3e39-40b1-a8f6-c9b8a598b74c" />

**Gold caveat fields carried into Analytics**

| province_name | derived_values (2019 and 2023) | per_capita_recomputed (2019 and 2023) |
| --- | --- | --- |
| Quezon | — | true |
| City of Tacloban | afs_gva_constant (DS_32) City of Tacloban from region total | false |

<img width="1187" height="151" alt="image" src="https://github.com/user-attachments/assets/d22fa36d-e5fe-483a-8db1-980e59d87568" />

## Notes

- **Missing is never 0.** Abra 2023 is `not_reported`, so it has no 2023 intensity, recovery or pattern; its 2022 recovery is still calculated (DL-009, DL-019).
- **Non-comparable years are kept and flagged.** Aklan 2022 and 2023 stay in `tourism_recovery` with `recovery_eligible = false` and a reason (DL-013, DL-020).
- **Price basis.** A&F growth uses constant prices; A&F share uses current prices (confirmed in Section 2).
- **Segment coverage.** Foreign recovery is not shown for units where DOT prints foreign travelers and overseas Filipinos together (`foreign_includes_overseas_filipinos`). Most overseas Filipino exclusions come from 2019 values that DOT printed as `-` (DL-019), not real zeros. Coverage should be shown next to these metrics (e.g. "26 of 52").
- **`reported_partial`.** Partly reported units (NCR) remain eligible; the team decision on DL-019 is still open. NCR's missing cities differ between 2019 and 2023, so its recovery index should be read with that caveat.
- **Labels are display rules, not findings.** `possible_emerging` and `under_review` follow DL-006, DL-028 and DL-029; `above_2019` alone does not mean emerging.
- **Cotabato.** Its population includes the Special Geographic Area while its GDP does not (DL-025).
- **Interpretation.** A&F GVA is a proxy for tourism-related activity; findings are associations, not causes (DL-007, DL-008).
