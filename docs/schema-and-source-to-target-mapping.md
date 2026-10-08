# Province-Level Data Model: Tourism and Local Economy

This document defines the data model that supports the tourism recovery and local-economy business questions (BQ1 and BQ2) at **province level**. It sets out the grain, keys, relationships and important fields of each table; the geographic and temporal compatibility of the sources; the source-to-target mappings; and the decisions taken.

---
## 1. Model overview

```mermaid
erDiagram
    dim_province ||--o{ fact_province_year : "province_psgc"
    dim_year ||--o{ fact_province_year : "year"

    dim_province {
        string province_psgc PK
        string province_name
        string unit_type
        string region_psgc
        string region_name
        string city_class
        string comparability_note
        string psgc_snapshot
        bigint census_population_ref
        int census_population_ref_year
    }

    fact_province_year {
        string province_psgc PK, FK
        int year PK, FK
        bigint foreign_travelers
        bigint overseas_filipinos
        bigint domestic_travelers
        bigint total_travelers
        string traveler_value_status
        decimal gdp_total_current
        decimal gdp_total_constant
        decimal gdp_per_capita_current
        decimal afs_gva_current
        decimal afs_gva_constant
        bigint population_total
        string population_source
        boolean comparable_to_2019
        timestamp built_at
    }

    dim_year {
        int year PK
        boolean is_baseline_year
        boolean is_recovery_year
        boolean in_comparison_window
        boolean has_all_sources
        boolean has_dot
        boolean has_psa_economy
        boolean has_population
    }
```

**Column definitions (key, column name, data type)**

### dim_province

| Key | Column Name | Data Type |
|-----|-------------|-----------|
| PK | province_psgc | string |
| | province_name | string |
| | unit_type | string |
| | region_psgc | string |
| | region_name | string |
| | city_class | string |
| | comparability_note | string |
| | psgc_snapshot | string |
| | census_population_ref | bigint |
| | census_population_ref_year | int |

### fact_province_year

| Key | Column Name | Data Type |
|-----|-------------|-----------|
| PK, FK | province_psgc | string |
| PK, FK | year | int |
| | foreign_travelers | bigint |
| | overseas_filipinos | bigint |
| | domestic_travelers | bigint |
| | total_travelers | bigint |
| | traveler_value_status | string |
| | gdp_total_current | decimal |
| | gdp_total_constant | decimal |
| | gdp_per_capita_current | decimal |
| | afs_gva_current | decimal |
| | afs_gva_constant | decimal |
| | population_total | bigint |
| | population_source | string |
| | comparable_to_2019 | boolean |
| | built_at | timestamp |

### dim_year

| Key | Column Name | Data Type |
|-----|-------------|-----------|
| PK | year | int |
| | is_baseline_year | boolean |
| | is_recovery_year | boolean |
| | in_comparison_window | boolean |
| | has_all_sources | boolean |
| | has_dot | boolean |
| | has_psa_economy | boolean |
| | has_population | boolean |

The model is a star schema with one fact table and two dimensions.

| Table | Purpose |
| --- | --- |
| `fact_province_year` | Tourism, economic and population measures for each province-level unit and year |
| `dim_province` | The province-level unit: Philippine Standard Geographic Code (PSGC), name, region and type |
| `dim_year` | The calendar year and flags identifying the baseline and recovery years |

The PSGC gives every place one stable 10-digit code. DOT and PSA identify places by name only, so reviewed mapping tables (kept outside the star) connect their names to PSGC codes. All sources can then be compared for the same province in the same year.

---

## 2. Selected sources

| Source | Bronze table | Used for |
| --- | --- | --- |
| PSGC 2Q 2026, DS_34 main sheet | `psgc_ds_34_psgc` (43,768 rows) | Authoritative list of places and codes; builds `dim_province` |
| PSGC DS_33 Provincial Summary; DS_34 National Summary | `psgc_ds_33_provincial_summary` (139), `psgc_ds_34_national_summary` (22) | Reconciliation only |
| PSGC report text | `psgc_report_text` | Snapshot label |
| DOT DS_05, overnight travelers 2019 to 2024 | `dot_ds_05_<year>` | Tourism columns |
| PSA DS_27 Total GDP, current prices | `psa_ds_27` | `gdp_total_current` |
| PSA DS_28 Total GDP, constant prices | `psa_ds_28` | `gdp_total_constant` |
| PSA DS_26 A&F GVA by region, 2022–2024 | `psa_ds_26` | Reconciliation only (validation rule 6) |
| PSA DS_29 Per capita GDP, current prices | `psa_ds_29` | `gdp_per_capita_current` |
| PSA DS_31 A&F GVA, current prices | `psa_ds_31` | `afs_gva_current` |
| PSA DS_32 A&F GVA, constant prices | `psa_ds_32` | `afs_gva_constant` |
| PSA DS_18 Projected mid-year population, province totals 2015–2025 (Excel; each province total includes its HUCs) | `psa_ds_18` | `population_total` for every unit without an HUC split, 2019–2024; province totals for the split below |
| PSA DS_18 Projected mid-year population by city/municipality, 2020–2025 (PDF; province totals match the Excel) | `psa_ds_18_pdf_rows` | HUC populations 2020–2024, used to separate the 16 HUCs from their provinces |

Not used: the PSGC `Prov Sum` sheet (dated "as of 30 June 2020") and PSA DS_30, DS_01, DS_02 and DS_08 to DS_17, which no business question requires.

---

## 3. Grain, keys and relationships

| Table | Grain (one row per) | Primary key | Foreign keys |
| --- | --- | --- | --- |
| `fact_province_year` | Province-level unit per year | (`province_psgc`, `year`) | `province_psgc` to `dim_province`; `year` to `dim_year` |
| `dim_province` | Province-level unit | `province_psgc` | none |
| `dim_year` | Calendar year, 2019 to 2024 | `year` | none |

**Relationships.** Each dimension row relates to many fact rows. The fact table joins directly to each dimension; the dimensions do not join to each other.

**Key rules**

1. `province_psgc` holds the PSGC code of the unit (a province code, an HUC city code, or the NCR region code) as 10-character text. Leading zeros are restored where the source has lost them.
2. The 10 digits are structured RR PPP MM BBB: region (digits 1 to 2), province (1 to 5), city or municipality (1 to 7), barangay (1 to 10).
3. The natural PSGC key is used, with no surrogate keys or history tracking, because a single PSGC snapshot applies to all years.
4. The fact table has exactly one row for every unit and every year from 2019 to 2024 (2025 is dropped: only DS_18 covers it). A value that no source published is NULL and is never replaced by 0.

---

## 4. Important fields

### 4.1 `dim_province`

| Field | Description |
| --- | --- |
| `province_psgc` | Primary key |
| `province_name` | Official PSGC name |
| `unit_type` | Province, HUC, Independent city (City of Isabela) or NCR |
| `region_psgc`, `region_name` | Region derived from the unit |
| `city_class` | HUC, independent component city or component city, where relevant |
| `comparability_note` | Why the unit's DOT coverage changes across years (e.g. Aklan: Boracay counted at the Caticlan jetty port from 2021). The year-level flag is `fact_province_year.comparable_to_2019` |
| `psgc_snapshot` | `2Q 2026` |
| `census_population_ref`, `census_population_ref_year` | PSGC 2024 census population and its year. This is a fixed census count that describes the unit, not a yearly measurement, so it stays in the dimension. Reference only; never used as a denominator (use `fact_province_year.population_total`) |

### 4.2 `dim_year`

`year`, `is_baseline_year` (2019), `is_recovery_year` (2022, 2023), `in_comparison_window` (2019 to 2023, DL-004), `has_all_sources` (2019 to 2023, when DOT, PSA economy and population all exist), `has_dot`, `has_psa_economy`, `has_population`.

### 4.3 `fact_province_year`

| Group | Columns | Source | Additivity |
| --- | --- | --- | --- |
| Tourism | `foreign_travelers`, `overseas_filipinos`, `domestic_travelers`, `total_travelers` | DOT DS_05 | Additive |
| Economy | `gdp_total_current` | PSA DS_27 | Additive |
| | `gdp_total_constant` | PSA DS_28 | Additive within a price basis |
| | `gdp_per_capita_current` | PSA DS_29 | Non-additive (ratio) |
| | `afs_gva_current`, `afs_gva_constant` | PSA DS_31, DS_32 | Additive within a price basis |
| Population | `population_total`, `population_source` | PSA DS_18 (Excel and PDF) | Additive across provinces, not across years |
| Comparability | `comparable_to_2019` | Derived from `map_dot_area_to_psgc` | Flag, not additive |

**Units:** `gdp_total_*` and `afs_gva_*` are in thousand PhP as published (constant prices at 2018 prices); `gdp_per_capita_current` is in PhP; traveler counts are persons-trips as reported by DOT. Units and price basis are stored in `ref_indicator` and as column comments.

The fact table stores base measures only. Ratios are non-additive and are defined once in Gold views over the star:

| Metric | Definition |
| --- | --- |
| Tourism activity | `total_travelers` |
| Tourism intensity | `total_travelers / population_total x 1,000`, from 2019. For the 16 HUCs and their 14 provinces the 2019 population is estimated (see 7.4 and `population_source`) |
| Concentration | Share of the provincial total per year, rank, top-N share and Herfindahl-Hirschman index |
| Recovery Index | `total_travelers (year) / total_travelers (2019) x 100`, for 2022 and 2023, each judged with that year's `comparable_to_2019`. Using the unrounded value: below 2019 if < 100, unchanged if = 100, above 2019 if > 100 |
| Segment recovery | Recovery Index for `domestic_travelers`, `foreign_travelers` and `overseas_filipinos` |
| Tourism change | `(total_travelers (2023) - total_travelers (2019)) / total_travelers (2019) x 100` (= Recovery Index - 100), so tourism and A&F are compared on the same % growth scale (AQ2.1) |
| A&F GVA growth | `(afs_gva_constant (2023) - afs_gva_constant (2019)) / afs_gva_constant (2019) x 100`; 0 = no growth, 25 = 25% growth (AQ2.1) |
| GDP growth | `(gdp_total_constant (2023) - gdp_total_constant (2019)) / gdp_total_constant (2019) x 100`, to compare A&F growth with the whole local economy |
| Quadrant | Tourism change and A&F GVA growth, each classed on the unrounded value as increased (> 0), decreased (< 0) or unchanged (= 0). The four quadrants use increased/decreased; a unit with either value unchanged is shown separately (AQ2.2) |
| Economic significance | `afs_gva_current / gdp_total_current x 100` for the same year |

Views: `vw_tourism_concentration`, `vw_tourism_intensity`, `vw_province_recovery`, `vw_tourism_economy_link`.

---

## 5. Geographic compatibility

| Topic | Treatment |
| --- | --- |
| Unit definition | A unit is a province, an HUC that DOT reports separately, the City of Isabela, or NCR. Both DOT and PSA rows are mapped to the same units, so each unit covers the same area in every source. |
| Cities DOT prints inside a province | DOT prints Lucena (HUC) and Dagupan, Santiago, Naga and Ormoc (ICC) as sub-rows inside their provinces (for example, Quezon's total is the sum of its sub-rows), not as separate level-1 rows. Their travelers are inside Quezon, Pangasinan, Isabela, Camarines Sur and Leyte. Lucena is therefore **not** a separate unit: its PSA rows are added to Quezon. |
| Component cities DOT prints separately | Masbate City and Sorsogon City are component cities in PSGC. Their DOT rows are added to Masbate and Sorsogon. |
| SBMA / Subic Bay Freeport Zone | Labeled SBMA in 2019–2022 and "Subic Bay Freeport Zone" in 2023–2024. It spans more than one province and has no PSGC code. It is excluded from the fact and listed in an exceptions table. |
| Clark Freeport Zone and Pampanga | In 2019–2022 "Clark" is a sub-row inside Pampanga and Pampanga's total includes it (2019: Pampanga 910,666, Clark 721,567). From 2023 DOT prints "Clark Freeport Zone" as its own level-1 row (1,269,019 in 2023) and Pampanga drops to 386,868. Clark is **added back to Pampanga** for 2023–2024 so Pampanga covers the same area every year and stays comparable (DL-014, #47, #49). |
| Cotabato City | DOT prints it under Region XII in 2019–2022 only; PSGC places it in BARMM, which DOT does not report. It is excluded and the gap is documented. |
| NCR | NCR is a single unit keyed by the NCR region code. Where a source prints NCR by city, the city rows are summed; where it prints an NCR total, that row is used. |
| Boracay | Boracay is printed at DOT level 1 but is a sub-area of Aklan (Malay). Whether Aklan includes it changes by year (OI-4): **2019–2020** Aklan excludes Boracay, so Boracay is **added to Aklan**; **2021–2022** Aklan equals Boracay, so Boracay is **not loaded**; **2023–2024** Aklan includes Boracay (Malay), so Boracay is **not loaded**. Aklan has `comparable_to_2019 = false` for 2021–2024 (and `true` for 2020) because DOT changed how Boracay is counted (Caticlan jetty port from 2021). |
| Units changed between 2019 and 2024 | A unit created, split, merged or counted differently by DOT gets `comparable_to_2019 = false` for each year after the change; those years are excluded from the recovery and BQ2 views, while earlier years stay usable. |
| Region assignment | Region is taken from the PSGC 2Q 2026 snapshot for all years. |
| PSA hierarchy markers | Leading dots differ in depth between PSA tables. Rows are classified by cleaned name matched to `dim_province`, not by dot depth. |
| Encoding | The Unicode replacement character in PSA names (for example `Las Pi\ufffdas`) is repaired in a cleaned name column. |
| Non-place rows | DOT `GRAND TOTAL` and region rows, and PSA region and national rows, are used for checks only. |
| Name matching | Exact name first, then PSGC `old_names`, then manual review. |

---

## 6. Temporal compatibility

| Source | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| DOT overnight travelers | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | |
| PSA GDP, GDP per capita, A&F GVA (DS_27, DS_28, DS_29, DS_31, DS_32) | ✓ | ✓ | ✓ | ✓ | ✓ | | |
| PSA projected population (DS_18: Excel 2015–2025 by province; PDF 2020–2025 by city/municipality) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

- **Geography:** one PSGC snapshot (2Q 2026) applies to all years.
- **Years required:** 2019 (baseline), 2022 and 2023 (recovery), and 2019 to 2023 for BQ2. All are covered by DOT and DS_27 to DS_32. All sources overlap in 2019 to 2023.
- **Population:** DS_18 comes from two compatible PSA projection files whose province totals match exactly. The Excel gives province totals for 2015–2025, but each province total includes its HUCs. The PDF lists every city and municipality for 2020–2025, so it is used to separate HUCs from their provinces. HUCs are not published for 2019, so their 2019 values are estimated from each HUC's projected 2020–2021 growth (DL-021, 7.4). Tourism intensity is therefore available from 2019 (AQ1.1). PSGC population is reference only.
- **Price basis:** growth uses constant prices; shares use current prices. The two are never combined in one ratio.
- **Missing values:** NULL means not published. The DOT `-` marker depends on where it appears (DL-019). A `-` **cell** in a row whose total is printed is loaded as 0 and marked `traveler_value_status = 'dash_as_zero'`, because row and regional totals only reconcile that way (about 1,200–1,900 cells per year). A row whose **total** is `-` is missing, not 0 (DL-009): its unit-year is `not_reported` (NULL) when every DOT row for that unit is `-`, and `reported_partial` when only some are (NCR in every year; Sorsogon 2019). 28 unit-years are `not_reported`, including Olongapo 2019 and Abra 2023.

---

## 7. Source-to-target mappings

Bronze remains as printed. Cleaning and mapping occur in Silver, and the star schema and views are built in Gold.

### 7.1 PSGC to `dim_province`

| Rule | Detail |
| --- | --- |
| Units selected | PSGC rows with geographic level Province; rows with level City and city class HUC, **except Lucena** (counted inside Quezon by DOT); the City of Isabela; and the NCR region row. BARMM provinces and Sulu are included as units with NULL tourism measures (not reported by DOT). |
| `province_psgc` | PSGC code of the selected row, as 10-character text |
| `unit_type` | Province, HUC, Independent city (City of Isabela) or NCR |
| `region_psgc`, `region_name` | First 2 digits of the code followed by zeros; name looked up from the region row |
| `city_class`, `census_population_ref`, `census_population_ref_year` | From the PSGC `City Class` and `2024 Population` fields; year taken from the source header |
| `psgc_snapshot` | From `psgc_report_text` |
| `comparability_note` | From `03_silver.geo_reporting_unit.dot_comparability_note` (the year-level flag is built in the fact, see 7.2) |

### 7.2 DOT to fact columns

| Source | Target | Transformation |
| --- | --- | --- |
| `area_label`, `parent_label`, `indent_level` (levels 0 and 1) | `province_psgc` | Trim; join to `03_silver.map_dot_area_to_psgc` on (`dot_indent_level`, `dot_parent_label`, `dot_area_label`) with the year between `valid_from_year` and `valid_to_year`; `province_psgc` = the map's `unit_psgc_code`. Apply each row's `row_role` (see 7.5): `province_unit` loaded, `add_to_parent` summed into its unit (Boracay 2019–2020, Clark Freeport Zone 2023–2024 into Pampanga, Masbate City, Sorsogon City, NCR cities into NCR), `exclude` not loaded (Boracay 2021–2024, SBMA / Subic Bay Freeport Zone, Cotabato City), `region_total` / `national_total` used only for validation rule 5 |
| `source_year` | `year` | Cast to integer |
| `foreign_travelers`, `overseas_filipinos`, `domestic_travelers`, `total_travelers` | Same names, plus `traveler_value_status` | Remove thousands separators; cast to bigint. Per DL-019: a `-` cell in a row with a printed total → 0; a row whose total is `-` contributes NULL. Unit-year status: `reported` (all rows printed), `dash_as_zero` (all row totals printed, some cells `-`), `reported_partial` (some row totals `-`; value = sum of printed rows), `not_reported` (every row `-`, or the unit is not in DOT, e.g. BARMM and Sulu; value NULL) |
| `breaks_comparability` of the map rows loaded or excluded into the unit that year | `comparable_to_2019` | `false` when any map row for the unit in that year has `breaks_comparability = true` (DOT counts the unit differently from 2019); otherwise `true`. 2019 is always `true`. With the current seed only Aklan is `false`, for 2021–2024 (DL-013) |

### 7.3 PSA to fact columns

| Source | Target | Transformation |
| --- | --- | --- |
| `psa_ds_27` | `gdp_total_current` | Unpivot year columns; remove thousands separators; cast to decimal |
| `psa_ds_28` | `gdp_total_constant` | As above |
| `psa_ds_29` | `gdp_per_capita_current` | As above. The NCR row is used as published (DS_29 prints an NCR value), consistent with D16 |
| `psa_ds_31` | `afs_gva_current` | As above |
| `psa_ds_32` | `afs_gva_constant` | As above |
| City of Tacloban, missing from `psa_ds_32` | `afs_gva_constant` | Derived as the Region VIII total minus the other Region VIII rows, and listed in `derived_values` (DL-024). This is the only PSA value derived this way; any other missing value stays NULL (DL-009) |
| Lucena rows in `psa_ds_28`, `psa_ds_31`, `psa_ds_32` (and `psa_ds_27` if printed) | Added to Quezon | Summed before loading so PSA covers the same area as DOT. The published per-capita value for Quezon no longer covers that area, so it is recomputed as `gdp_total_current x 1,000 / population_total` (GDP is in thousand PhP, per capita in PhP) for 2019 to 2023 (DS_18's Quezon total already includes Lucena, so it matches the Quezon unit). This is the only exception to D16 |
| First column (`Provinces` or `Region`, depending on the table) | `province_psgc` | Remove leading dots and join to `map_psa_area_to_psgc` on the cleaned label (D13). Load `unit` rows; add `add_to_unit` rows to their unit (Lucena into Quezon, DL-011). NCR uses the NCR row; its `ncr_component` rows (cities and Pateros) and the `region_total` rows are validation only (validation rule 6) |
| Revision suffix (for example `2023r`) | Silver `is_revised` | Separate the suffix from the value |

### 7.4 DS_18 to `population_total`

Population follows DL-021. Both DS_18 files are mapped through `map_psa_area_to_psgc` (old labels such as `Compostela Valley`, `Zambonga del Sur`, `Samar (Western Samar)` and `Cotabato (North Cotabato)` are mapped there). Each row records `population_source`:

| Unit | 2019 | 2020 to 2024 | `population_source` |
| --- | --- | --- | --- |
| Province with no separate HUC, Quezon (includes Lucena), City of Isabela | Excel `Total` | Excel `Total` | `ds18_excel` |
| NCR | Excel `National Capital Region` | Excel | `ds18_excel` |
| The 16 HUCs outside NCR | `HUC_2020 x HUC_2020 / HUC_2021` (one-year back-cast using the HUC's own projected growth) | PDF row | `estimated_from_2020_trend` / `ds18_pdf` |
| The 14 provinces with an HUC (Benguet, Pampanga, Zambales, Palawan, Iloilo, Negros Occidental, Cebu, Leyte, Zamboanga del Sur, Misamis Oriental, Lanao del Norte, Davao del Sur, South Cotabato, Agusan del Norte) | Excel total minus its estimated HUCs | Excel total minus its HUCs from the PDF | `estimated_from_2020_trend` / `ds18_excel_minus_huc` |

From the Excel, only the `Total` rows are kept (not the age groups or Male/Female). DS_18 still has a single Maguindanao (before the 2022 split), so Maguindanao del Norte and del Sur stay NULL; Cotabato City is listed separately and is not a unit. A unit with no matching row remains NULL.

### 7.5 Mapping and reference tables (Silver, outside the star)

| Table | Grain | Key | Main fields |
| --- | --- | --- | --- |
| `map_dot_area_to_psgc` | One printed DOT label (region rows at indent level 0, province-level rows at level 1) per validity period | (`dot_indent_level`, `dot_parent_label`, `dot_area_label`, `valid_from_year`) | `valid_to_year` (NULL = still in use), `row_role` (`province_unit`, `add_to_parent`, `exclude`, `region_total`, `national_total`), `unit_psgc_code` (unit the travelers are loaded to), `area_psgc_code` (the printed area itself, e.g. Malay for Boracay), `exclude_reason` (`double_count`, `no_psgc_unit`, `outside_dot_coverage`), `breaks_comparability` (`true` only on rows treated differently from 2019: Boracay 2021–2024), `match_method`, `match_status`, `notes`, `reviewed_by`, `reviewed_on`. Built by `01_silver_geography` from the seed `resources/seeds/map_dot_area_to_psgc.csv` (#47) |
| `map_psa_area_to_psgc` | One PSA row label, the same 134 labels in DS_27 to DS_32 | (`psa_label`) | `psa_region_code` (region the row is printed under; PSA uses 17 regions in 2019–2023), `row_role` (`unit`, `add_to_unit`, `ncr_component`, `region_total`), `unit_psgc_code`, `area_psgc_code`, `area_psgc_name`, `reviewed_by`, `reviewed_on`, `notes`. Built by `03_silver_psa_economy` from the seed `resources/seeds/map_psa_area_to_psgc.csv`; DS_18 labels are added by the population step |
| `ref_indicator` | Fact column | `column_name` | Units, price basis, base year, source table title |

### 7.6 Validation rules

1. PSGC rows loaded equal the Bronze rows (43,768); `psgc_code` is unique and 10 digits; every non-region place has a parent.
2. PSGC counts of cities, municipalities and barangays per province and region agree with DS_33 and the DS_34 National Summary; differences are listed.
3. Star keys are unique, the fact has one row per unit and year (`dim_province` rows x 6 years, 2019 to 2024), and there are no orphan keys.
4. Every DOT level-1 label and every PSA area label has a defined role; the unmapped count is 0.
5. DOT: traveler groups sum to the total in every row. After applying `row_role`, the loaded province-level totals plus the `exclude` rows that are not double counts (SBMA / Subic Bay Freeport Zone and Cotabato City) sum to the DOT region totals and the `GRAND TOTAL` for each year (2019 grand total 56,766,370; 2023 grand total 55,329,974).
6. PSA: province-level sums agree with region or national rows within a stated tolerance; differences are listed.
7. For every unit and comparison year (2022, 2023) with `comparable_to_2019 = true`, tourism columns are non-NULL for 2019 and that year, and economic columns are non-NULL for 2019 and 2023; failures are listed with the reason (REVIEW). Expected under DL-019: Olongapo City (2019, 2022), Angeles City (2022), Davao Occidental (2022) and Abra (2023) are `not_reported`.
8. Shares use current-price columns only; growth uses constant-price columns only.
9. Population: every PDF province total equals the Excel total for 2020–2025 (checked: all 83 provinces and independent cities match exactly); for each province with an HUC, the province unit plus its HUCs equals the DS_18 province total in every year; the 2019 HUC estimates are listed for review (REVIEW).

---

## 8. Decisions

| ID | Decision | Rationale |
| --- | --- | --- |
| D1 | The 10-digit PSGC code, stored as text, is the geography key. | Place names are unstable; codes join sources reliably. |
| D2 | The DS_34 main sheet is the authoritative place list. DS_33 and the DS_34 summary sheets are used for reconciliation only. `Prov Sum` is excluded. | One list and one hierarchy; `Prov Sum` is dated 2020. |
| D3 | A unit is a province, an HUC reported separately by DOT, the City of Isabela, or NCR. Lucena is counted inside Quezon; Masbate City and Sorsogon City are added to their provinces; Clark Freeport Zone is added to Pampanga from 2023 (DL-014); SBMA / Subic Bay Freeport Zone and Cotabato City are excluded. | Each unit must cover the same area in DOT and PSA; DOT reports some cities inside provinces and some component cities separately; adding Clark back keeps Pampanga comparable across 2022 and 2023. |
| D4 | Region is derived from the unit using the PSGC 2Q 2026 assignment and stored in `dim_province`. | Consistent with PR #30; keeps the star free of dimension-to-dimension joins. |
| D5 | One PSGC snapshot applies to all years, with no history tracking. | One consistent geography. |
| D6 | Bronze is kept as printed; cleaning, padding, casting and unpivoting occur in Silver. | Bronze guide and lineage. |
| D7 | Name-to-PSGC mappings are reviewed tables, not fuzzy matching in code. | Every mapping is explainable and signed off. |
| D8 | Boracay is added to Aklan for 2019–2020 and excluded for 2021–2024. Aklan is not comparable to 2019 from 2021 (`comparable_to_2019 = false` for 2021–2024). | DOT counts Boracay separately in 2019–2020 (Aklan 217,367 vs Boracay 2,034,599 in 2019) and inside Aklan from 2021 (OI-4). Excluding it every year would remove about 2 million travelers from Aklan's 2019 baseline. |
| D9 | Tourism measures come from DOT level-1 rows. A `-` cell in a row with a printed total is 0 (`dash_as_zero`); a row whose total is `-` is missing; a unit-year is `not_reported` (NULL) if all its rows are `-` and `reported_partial` if some are (DL-019). | Totals reconcile only when `-` cells count as 0, but a whole-row `-` is not a credible zero (Angeles City: 70,476 in 2019, `-` in 2020–22, 157,666 in 2023), and DL-009 says missing is never 0. |
| D10 | The model is a star with one fact and two dimensions. Mapping tables and the full PSGC list stay in Silver. | Simple to explain and to query. |
| D11 | NULL means not published and is never 0. The fact has a row for every unit and year from 2019 to 2024. | Keeps gaps visible and the grain complete; 2025 has no tourism or economic data. |
| D12 | Only the PSA tables required by the business questions are included (DS_18 Excel and PDF, DS_27, DS_28, DS_29, DS_31, DS_32), plus DS_26 for reconciliation. | Keeps the model small; DS_28 is needed to compare A&F growth with overall GDP growth at constant prices. |
| D13 | PSA rows are classified by cleaned name matched to `dim_province`, not by leading-dot depth. | Dot depth differs between PSA tables. |
| D14 | Ratios are not stored in the fact; they are defined once in Gold views. Growth uses constant prices, shares use current prices, a ratio is NULL where its 2019 base is 0 or missing, and direction uses the unrounded value: increased (> 0 growth, or index > 100), decreased (< 0, or < 100), unchanged (= 0, or = 100). | Ratios cannot be summed or averaged; one definition serves every question. |
| D15 | `comparable_to_2019` is set per unit and year, so 2019→2022 and 2019→2023 are judged separately. Recovery and BQ2 views use a unit-year only when it is comparable to 2019; a ratio is still NULL when either value is missing (D14). | A change that only affects later years should not remove an earlier valid result; a `not_reported` year (DL-019) has no value to compare. |
| D16 | Per-capita GDP is taken from DS_29 as published, including the NCR row. The only exception is Quezon, whose per-capita value is recomputed for 2019 to 2023 after Lucena is added. Population comes from DS_18 for the same year: the Excel for province totals and the PDF to separate HUCs (2020–2024); the 2019 HUC split is estimated from each HUC's projected 2020–2021 growth (`population_source = 'estimated_from_2020_trend'`, DL-021). Intensity is available from 2019. PSGC population is reference only. | Published values follow PSA's own method; DS_18 province totals include HUCs, but DOT reports HUCs separately; 2019 has no published HUC values, and without them the 2019 baseline intensity (AQ1.1) would be missing for most major city destinations. |
| D17 | Units and price basis are recorded in `ref_indicator` and the Gold column comments, taken from each PSA table title (e.g. "In thousand PhP, at constant prices"). | #39 skips the CSV title row on load, so the title text is captured once in `ref_indicator` instead of in Bronze. |