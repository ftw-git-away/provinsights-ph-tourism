# Seeds

Reviewed reference files that Silver notebooks load as-is. Seeds are changed only through pull requests, like code.

## `map_dot_area_to_psgc.csv`

Maps every DOT overnight-traveler row printed at indent level 0 (regions, `GRAND TOTAL`) or 1 (provinces, HUCs, cities, zones) to a PSGC 2Q 2026 reporting unit, per validity period. Loaded by `notebooks/03_silver/01_silver_geography` into `03_silver.map_dot_area_to_psgc`.

| Column | Meaning |
| --- | --- |
| `dot_indent_level` | `0` = region / `GRAND TOTAL`, `1` = province-level row |
| `dot_parent_label` | Region label exactly as printed (empty for level 0) |
| `dot_area_label` | Row label exactly as printed |
| `valid_from_year`, `valid_to_year` | Years the rule applies to; empty `valid_to_year` = still in use |
| `row_role` | `province_unit` (loaded as the unit), `add_to_parent` (summed into `unit_psgc_code`), `exclude` (not loaded), `region_total`, `national_total` (reconciliation only) |
| `unit_psgc_code` | Reporting unit the travelers are loaded to |
| `area_psgc_code` | PSGC code of the printed area itself (e.g. Malay for Boracay) |
| `exclude_reason` | `double_count`, `no_psgc_unit`, `outside_dot_coverage` |
| `breaks_comparability` | `true` only on rows that DOT counts differently from 2019 (currently Boracay 2021–2022 and Boracay (Malay) 2023–). The year-level `comparable_to_2019` and the unit-level `dot_breaks_comparability` are derived from it (DL-013, DL-020) |
| `match_method`, `match_status`, `notes` | How the match was made and why |
| `reviewed_by`, `reviewed_on` | Filled when the row is reviewed |

Key: (`dot_indent_level`, `dot_parent_label`, `dot_area_label`, `valid_from_year`).

**When a new DOT year is loaded**, `01_silver_geography` fails check `DQ-DOT-03` if a label is new or renamed. Add a row here (or close the old row with `valid_to_year` and add the new label), then rerun.

## `map_psa_area_to_psgc.csv`

Maps every row label of the PSA provincial accounts tables (DS_27 to DS_32: 134 labels in DS_27 to DS_31; DS_32 has 133, with no City of Tacloban row) to a reporting unit. Loaded by `notebooks/03_silver/03_silver_psa_economy` into `03_silver.map_psa_area_to_psgc`.

| Column | Meaning |
| --- | --- |
| `psa_label` | Row name as printed, without the leading dots (the number of dots differs between tables, so it is never used, D13). Two NCR cities print "ñ" as a replacement character in the PSA files and are kept as printed |
| `psa_region_code` | Region the row is printed under. The 2019–2023 tables use 17 regions: Negros provinces under VI / VII, Sulu under BARMM |
| `row_role` | `unit` (the unit's value), `add_to_unit` (summed into another unit: Lucena into Quezon, DL-011), `ncr_component` (NCR city or Pateros, already inside the NCR row, DL-012), `region_total` (validation only) |
| `unit_psgc_code` | Reporting unit the value belongs to |
| `area_psgc_code`, `area_psgc_name` | PSGC code and name of the printed area |
| `notes`, `reviewed_by`, `reviewed_on` | Why, and review trail |

Key: `psa_label`, one row per label (check `DQ-PSA-10`; a repeated label would duplicate rows in the join). A new or renamed PSA label fails check `DQ-PSA-01`; add it here and rerun.

## `map_psa_population_area_to_psgc.csv`

Maps every DS_18 population label used by Silver to a PSGC 2Q 2026 reporting unit: the Excel area rows (`psa_ds_18`) and, from the PDF (`psa_ds_18_pdf_rows`), the same areas (for the Excel–PDF check), the region rows and the 16 HUCs. Loaded by `notebooks/03_silver/04_silver_population` into `03_silver.map_psa_population_area_to_psgc`.

DS_18 has its own crosswalk because its labels cover different areas from the PSA economy tables: DS_18 `Cebu` includes Cebu City, Lapu-Lapu and Mandaue.

| Column | Meaning |
| --- | --- |
| `source_table` | `psa_ds_18` (Excel) or `psa_ds_18_pdf_rows` (PDF) |
| `block_label` | PDF HUC and region rows only: the area heading the row is printed under (the PDF also has a municipality named "Caraga") |
| `area_label` | Row label exactly as printed |
| `ds18_area` | The Excel label of the same area |
| `row_role` | Excel: `unit`, `not_a_unit` (Maguindanao before the split, Cotabato City), `region_total`, `national_total`. PDF: `check_total`, `region_total`, `huc` |
| `unit_psgc_code` | Unit the value belongs to |
| `from_unit_psgc_code` | For an HUC: the province unit it is subtracted from |
| `area_psgc_code`, `area_psgc_name` | PSGC code and name of the printed area |
| `notes`, `reviewed_by`, `reviewed_on` | Why, and review sign-off |

Key: (`source_table`, `block_label`, `area_label`).

**When DS_18 is updated**, `04_silver_population` fails check `DQ-POP-01` (Excel) or `DQ-POP-02` (PDF) if a label is new or renamed. Add or fix the row here, then rerun.