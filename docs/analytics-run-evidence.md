# Analytics Layer Run Evidence

This document confirms that the BQ1 and BQ2 Analytics tables (`tuklas_dev`, schema `05_analytics`) are correct, consistent with Gold, and safe to use for downstream analysis. The results were produced by `02_analytics_run_evidence`, a read-only notebook that reads the Analytics tables, `04_gold.fact_province_year` and `06_data_quality.dq_results`.

> **Note:** Grain, row counts, duplicate keys, eligibility, classification and Analytics-to-Gold checks run inside `01_build_analytics` and are saved to `dq_results`. This evidence reports those results without repeating them, and adds a comparison against the source files and a summary of exclusions and caveats.

| | |
| --- | --- |
| **Run date** | 12 October 2026 |
| **Run by** | `Haze` |
| **Notebooks** | `01_build_analytics`, `02_analytics_run_evidence` |
| **Run ID** | `analytics_20261012_041307_9c199ff7` (checks saved 2026-10-12 04:15:53) |

## Summary

- **All 57 checks in the latest `01_build_analytics` run passed:** 56 BLOCK and 1 REVIEW. No BLOCK failures and no REVIEW flags.
- **Edge cases match the source files:** 80 of 80 values and 8 of 8 tourism–economy patterns match the values calculated from the DOT PDFs, PSA tables and DS_18.
- **Exclusions behave as intended:** units with a missing baseline, a missing comparison value or a non-comparable year get no recovery metric and are kept with a reason.
- **Headline counts match the presentation:** in 2023, 39 units are above 2019, 52 below and 9 not compared; 43 of 91 eligible units show tourism and A&F GVA moving in opposite directions.
- **One finding to follow up:** foreign and overseas Filipino recovery are blocked for every unit, although Gold now has the field needed to limit the block to five Region II provinces (see Notes).

## Results

### 1. Checks from the latest `01_build_analytics` run

| severity | status | count |
| --- | --- | --- |
| BLOCK | PASS | 56 |
| REVIEW | PASS | 1 |

These cover the Issue #60 items for grain and uniqueness (C1–C3, D1, D6, E1–E3, F1–F2, G1–G2), eligibility and classification (D2–D4, E4–E6, F3–F6, G3–G12) and reconciliation of Analytics to Gold (H1–H8). The full list of checks is shown below.

> `REVIEW | PASS | 1` means the one REVIEW-severity check passed; it is not a REVIEW flag.

<img width="617" height="226" alt="image" src="https://github.com/user-attachments/assets/7b8a925e-3f65-49ce-85f0-689e6ad57207" />
<img width="1178" height="407" alt="image" src="https://github.com/user-attachments/assets/efd76b9c-4415-4774-b2f4-bcdf7d0e6a59" />
<img width="1177" height="412" alt="image" src="https://github.com/user-attachments/assets/5533320a-6bac-4577-ba56-f510351d6795" />
<img width="1172" height="421" alt="image" src="https://github.com/user-attachments/assets/62f43a75-21f1-4cd4-91f3-fa689a546f4e" />
<img width="1173" height="400" alt="image" src="https://github.com/user-attachments/assets/d00e5cbe-1bfc-4881-9f1e-09e42cac00e4" />




### 2. Edge cases: Analytics vs source files

Expected values were calculated directly from DOT *Regional Distribution of Overnight Travelers* (2019, 2022, 2023), PSA Tables 3.72, 3.94 and 3.95, and PSA DS_18, applying DL-011, DL-013, DL-014, DL-019 and DL-021. Traveler and population counts had to match exactly; % and per-1,000 values within 0.01.

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

<img width="1185" height="452" alt="image" src="https://github.com/user-attachments/assets/de459c3d-ac68-44b7-877b-8520c2a1dee7" />

<img width="1183" height="316" alt="image" src="https://github.com/user-attachments/assets/763c1a9e-23e1-4798-9ecd-d97759ee3017" />


**Sample calculations**
- **Pampanga, Recovery Index 2023:** (386,868 Pampanga + 1,269,019 Clark Freeport Zone) ÷ 910,666 × 100 = **181.83** (DL-014).
- **Aklan, travelers 2019:** 217,367 Aklan + 2,034,599 Boracay = **2,251,966**. No Recovery Index for 2022 or 2023, because Aklan is not comparable to 2019 from 2021 (DL-013).
- **Aurora, A&F growth:** 381,167 ÷ 508,545 − 1 = **−25.05%** (Table 3.95, constant prices). A match with the Analytics value confirms growth uses constant prices.
- **Camiguin, A&F share:** A&F GVA ÷ GDP, 2023 (Tables 3.94 and 3.72, current prices) = **11.80%**. A match confirms share uses current prices.

**Trace (Analytics → Gold → Silver → source):** Analytics matches Gold (checks H1–H8), Gold matches Silver row by row (Gold run evidence, DQ-GLD-05 to 07), and Analytics matches the source files for the units above (this section).

### 3. Exclusions and caveats

**Recovery: units not compared, by reason**

| comparison_year | reason | count |
| --- | --- | --- |
| 2022 | baseline travelers_2019 is NULL | 7 |
| 2022 | comparison travelers is NULL | 2 |
| 2022 | comparison year not comparable to 2019 | 1 |
| 2023 | baseline travelers_2019 is NULL | 7 |
| 2023 | comparison travelers is NULL | 1 |
| 2023 | comparison year not comparable to 2019 | 1 |

- **Baseline NULL (7):** the 5 BARMM provinces and Sulu (no DOT data) and Olongapo City (`not_reported` in 2019).
- **Comparison NULL:** 2022: Angeles City and Davao Occidental; 2023: Abra (`not_reported`, DL-019).
- **Not comparable (1):** Aklan, from 2021 (DL-013, DL-020).

**Recovery classes**

| comparison_year | recovery_class | count |
| --- | --- | --- |
| 2022 | above_2019 | 24 |
| 2022 | below_2019 | 66 |
| 2022 | not compared (NULL) | 10 |
| 2023 | above_2019 | 39 |
| 2023 | below_2019 | 52 |
| 2023 | not compared (NULL) | 9 |

No unit is exactly at 2019 (`unchanged`). Ineligible units stay NULL and are not forced into a class.

<img width="1182" height="527" alt="image" src="https://github.com/user-attachments/assets/2164d843-c0d3-462a-83d0-4987e9d7adc2" />


**Tourism–economy patterns (2019–2023)**

| tourism_economy_pattern | count |
| --- | --- |
| tourism_up_economy_up | 26 |
| tourism_down_economy_down | 22 |
| tourism_down_economy_up | 30 |
| tourism_up_economy_down | 13 |
| not eligible (tourism change not eligible) | 9 |

48 of 91 eligible units moved in the same direction and 43 in opposite directions. No unit has an `unchanged` direction.

**Gold caveat fields present:** `foreign_includes_overseas_filipinos`, `derived_values`, `per_capita_recomputed`.

**Traveler segments:** `foreign_segment_supported = false` and `overseas_filipino_segment_supported = false` for all 200 rows of `traveler_segment_recovery`.

<img width="1181" height="588" alt="image" src="https://github.com/user-attachments/assets/9e5c79bc-bb4c-4b66-bb52-f34e8f96cf45" />

## Notes

- **Missing is never 0.** Abra 2023 is `not_reported`, so it has no 2023 intensity, recovery or pattern; its 2022 recovery is still calculated (DL-009, DL-019).
- **Non-comparable years are kept and flagged.** Aklan 2022 and 2023 stay in `tourism_recovery` with `recovery_eligible = false` and a reason (DL-013, DL-020).
- **Price basis.** A&F growth uses constant prices; A&F share uses current prices (confirmed in Section 2).
- **Traveler segments (finding):** Gold has `foreign_includes_overseas_filipinos`, `derived_values` and `per_capita_recomputed`, but `traveler_segment_recovery` marks foreign and overseas Filipino recovery as unsupported for all 200 rows, because `01_build_analytics` still treats the Gold field as missing. Since the flag is true only for Batanes, Cagayan, Isabela, Nueva Vizcaya and Quirino, the block could be limited to those five provinces so AQ1.3 can show foreign and overseas Filipino recovery for the other units. Until then, AQ1.3 shows domestic recovery only. To follow up in `01_build_analytics`.
- **Gold caveat fields not yet carried into Analytics:** `derived_values` (City of Tacloban A&F GVA, DL-024) and `per_capita_recomputed` (Quezon, DL-011).
- **Cotabato.** Its population includes the Special Geographic Area while its GDP does not (proposed DL-025).
- **Interpretation.** A&F GVA is a proxy for tourism-related activity; findings are associations, not causes (DL-007, DL-008).
