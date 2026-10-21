# ProvInsights Data Sources

This document lists the government sources ProvInsights uses, what each one feeds, how the known source problems were handled, and what the sources can't tell us. The business question and its definitions are in [business-and-analytical-questions.md](business-and-analytical-questions.md). How the files are read into Bronze, including Google Drive folders and file IDs, is in the [Bronze ingestion guide](bronze-ingestion-guide.md).

## Contents

- [Sources used in the pipeline](#sources-used-in-the-pipeline)
- [Ingested for reference only](#ingested-for-reference-only)
- [Considered and not used](#considered-and-not-used)
- [How to read overnight travelers](#how-to-read-overnight-travelers)
- [Known source issues and how they were handled](#known-source-issues-and-how-they-were-handled)
- [Limitations](#limitations)

## Sources used in the pipeline

Every source is identified by a dataset ID (`DS_XX`) that is used in file names, Bronze tables and the `_source_dataset_id` column.

| ID | Source | Publisher | Years | Format | Bronze tables | Feeds |
| --- | --- | --- | --- | --- | --- | --- |
| DS_05 | Regional Distribution of Overnight Travelers | DOT | 2019-2024 | PDF, one per year | `dot_ds_05_<year>`, `dot_ds_05_report_text`, `dot_ds_05_pdf` | `dot_travelers_unit_year`: tourism activity, intensity, leading destinations, recovery (supporting) |
| DS_18 | Updated Projected Mid-Year Population, based on the 2015 POPCEN | PSA | Excel 2015-2025, PDF 2020-2025 | Excel and PDF | `psa_ds_18`, `psa_ds_18_pdf`, `psa_ds_18_pdf_rows`, `psa_ds_18_pdf_report_text` | `population_unit_year`: tourism intensity (DL-021) |
| DS_26 | Table 3.63, A&F gross value added by region, current prices | PSA | 2022-2024 | CSV | `psa_ds_26` | Reconciliation only: DQ-PSA-06 compares its national total with DS_31 and DS_32 |
| DS_27 | Table 3.72, GDP, current prices | PSA | 2019-2023 | CSV | `psa_ds_27` | `gdp_total_current` |
| DS_28 | Table 3.73, GDP, constant 2018 prices | PSA | 2019-2023 | CSV | `psa_ds_28` | `gdp_total_constant` |
| DS_29 | Table 3.74, GDP per capita, current prices | PSA | 2019-2023 | CSV | `psa_ds_29` | `gdp_per_capita_current`: the lower-income flag (DL-035) |
| DS_31 | Table 3.94, A&F gross value added, current prices | PSA | 2019-2023 | CSV | `psa_ds_31` | `afs_gva_current`: output per visitor and tourism share of the economy (DL-007, DL-033) |
| DS_32 | Table 3.95, A&F gross value added, constant 2018 prices | PSA | 2019-2023 | CSV | `psa_ds_32` | `afs_gva_constant` |
| DS_34 | PSGC 2Q 2026 Publication Datafile | PSA | 2Q 2026 | Excel | `psgc_ds_34_<sheet>` | `geo_psgc`, `geo_reporting_unit`, `dim_province`: the single geographic key for every year (DL-002, DL-010) |

A&F means accommodation and food services (hotels and restaurants). PSA publishes the provincial economy tables in thousand PhP, except GDP per capita, which is in PhP.

**Common years.** DOT covers 2019-2024 and the PSA provincial accounts cover 2019-2023, so Gold holds 2019-2024 and every measure that needs both sources uses 2019-2023. AQ2 to AQ4 use 2023, the latest year with both.

**Geography.** Every source is mapped to one of the 100 reporting units (82 provinces, 16 HUCs that DOT reports separately, the City of Isabela and NCR) using PSGC 2Q 2026 for every year (DL-010). The mappings from each source's labels to PSGC codes are reviewed seed files in [`resources/seeds/`](../resources/seeds/): `map_dot_area_to_psgc.csv`, `map_psa_area_to_psgc.csv` and `map_psa_population_area_to_psgc.csv`.

## Ingested for reference only

These files are loaded into Bronze so they are kept with the rest of the evidence, but no Silver, Gold or Analytics table reads them.

| ID | Source | Why it is kept |
| --- | --- | --- |
| DS_01 | Philippine Tourism Satellite Account (PTSA) statistical tables, 2000-2025 | National tourism context, such as tourism's share of GDP and employment in the README. PTSA has no provincial figures. |
| DS_02 | Tourism Statistical Classification, 2025 | Definitions of tourism industries and products |
| DS_08 to DS_17 | Philippine Statistical Yearbook, Tables 8.1 to 8.10 | National tourism statistics, such as foreign arrivals (Table 8.1), used to show that DOT overnight travelers aren't arrivals |
| DS_30 | Table 3.75, GDP per capita, constant 2018 prices | Not needed; the analysis uses current prices |
| DS_33 | PSGC 2Q 2026 National and Provincial Summary | PSGC summary counts, kept for reference |

## Considered and not used

| Source | Why not |
| --- | --- |
| Census population tables (Table B and Tables 1, 2, 3, 5, 6) | Census years only (2010, 2015, 2020, 2024) or national level. DS_18 gives a value for every year. |
| DOH barangay population | Wrong grain, and its provenance could not be confirmed |
| Hotel occupancy, NCR | One region only |
| Outbound tourism tables | Measures Filipinos travelling abroad, not visitors to provinces |
| Monthly inbound tourism updates | Single months, national level |
| DOT overnight traveler reports before 2019 | Outside the 2019-2023 window. They also use older region boundaries (for example the 2008 Region IV-A and IV-B split). |

## How to read overnight travelers

DOT's overnight traveler counts are **stays recorded by accommodation establishments**, not unique visitors and not border arrivals. For example, the 2024 DOT regional report totals 7.63 million foreign travelers, while the Philippine Statistical Yearbook (Table 8.1) reports 5.44 million foreign arrivals and DOT's 2024 citizenship table reports 5.93 million. DOT doesn't publish how establishments tally travelers, so the reason for the gap can't be confirmed.

ProvInsights therefore treats overnight travelers as a measure of **tourism activity**, never as a headcount (DL-005). Same-day visitors aren't counted at all.

## Known source issues and how they were handled

| Issue | Affected | How it was handled | Ref |
| --- | --- | --- | --- |
| DOT prints sub-rows inside provinces, so adding every row double-counts | Boracay in Aklan, Lucena in Quezon, Clark in Pampanga, others | Each DOT row has a role in the crosswalk seed (counted, added to its parent, or excluded), so every traveler is counted once | DL-011 to DL-017 |
| Boracay changed counting method | Aklan, 2019-2024 | Boracay is added to Aklan in 2019-2020 and not loaded from 2021, when Aklan's row already includes it. Aklan is marked not comparable with 2019 from 2021. | DL-013, DL-020 |
| `-` in DOT tables | Many units, every year | Read by position: a `-` cell in a row with a printed total is 0; a row whose total is `-` is missing. Missing stays NULL, never 0. | DL-009, DL-019 |
| DOT coverage widens over time | 14 units, 2020-2024 (for example Camarines Sur and Romblon) | Towns that printed `-` in 2019 report in later years, so part of the rise reflects wider reporting. Kept as printed and noted on the dashboard. | OI-5 |
| Region II prints foreign travelers and overseas Filipinos together | Five Region II units | Flagged with `foreign_includes_overseas_filipinos` so the split isn't compared with other regions | DL-030 |
| Cotabato City is in BARMM in PSGC but under Region XII in DOT | Cotabato City | DOT rows excluded, because DOT doesn't report the rest of BARMM | DL-016 |
| BARMM provinces and Sulu have no DOT data | Six units, every year | Kept as units with NULL travelers. They get no group in AQ2 to AQ4. | DL-009 |
| Sulu is in Region IX in PSGC but under BARMM in PSA's economy tables | Sulu | Region always comes from the PSGC code | DL-003, OI-2 |
| Makati and Taguig boundary change (EMBO barangays) | NCR | NCR is analysed as one unit, so the transfer between the two cities doesn't affect results | DL-012 |
| Name collisions, such as Isabela (city, province and a Negros Occidental town) | City of Isabela, Isabela | Matched by PSGC code, never by name alone | DL-002, DL-010 |
| HUCs are excluded from their parent province in PSA's economy tables but included in DS_18 province totals | 16 HUCs and their provinces | HUCs are separate units. Population for HUCs comes from the DS_18 PDF; 2019 HUC values are estimated. | DL-010, DL-021 |
| A single PSA value is missing in a region | City of Tacloban, `afs_gva_constant` | Derived from the printed region total and flagged in `derived_values` | DL-024 |
| Cotabato's population area includes barangays moved to BARMM in 2024 | Cotabato | Kept, not adjusted. Its per-capita and intensity figures use a slightly larger population than its GDP area. | DL-025 |
| Unusual DOT values | For example Zamboanga Sibugay (identical counts in several years, then a large jump in 2024) and the City of Isabela | Kept as printed. Small 2023 bases are marked "Check before naming", and the supporting recovery tables flag extreme values for review. | OI-5, DL-028, DL-036 |

## Limitations

- **Tourism activity is reported overnight stays**, not unique visitors or same-day trips.
- **A&F GVA is a proxy.** It includes spending by residents and business travelers, and it misses transport, tours and shopping. PSA publishes tourism's own value added only at the national level (PTSA).
- **The latest common year is 2023.** DOT has 2024, but the PSA provincial accounts stop at 2023.
- **Population for 2019 HUCs is estimated**, and all DS_18 values are projections based on the 2015 census (DL-021).
- **Files are placed in Google Drive by hand.** DOT and PSA publish on different schedules and in different formats, so there is no automatic download. A replaced or edited file is detected by its SHA-256 fingerprint (`_source_sha256`).
