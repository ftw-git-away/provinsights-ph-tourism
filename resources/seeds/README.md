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

Maps every row label of the PSA provincial accounts tables (DS_27 to DS_32; the same 134 labels in each) to a reporting unit. Loaded by `notebooks/03_silver/03_silver_psa_economy` into `03_silver.map_psa_area_to_psgc`.

| Column | Meaning |
| --- | --- |
| `psa_label` | Row name as printed, without the leading dots (the number of dots differs between tables, so it is never used, D13). Two NCR cities print "ñ" as a replacement character in the PSA files and are kept as printed |
| `psa_region_code` | Region the row is printed under. The 2019–2023 tables use 17 regions: Negros provinces under VI / VII, Sulu under BARMM |
| `row_role` | `unit` (the unit's value), `add_to_unit` (summed into another unit: Lucena into Quezon, DL-011), `ncr_component` (NCR city or Pateros, already inside the NCR row, DL-012), `region_total` (validation only) |
| `unit_psgc_code` | Reporting unit the value belongs to |
| `area_psgc_code`, `area_psgc_name` | PSGC code and name of the printed area |
| `notes`, `reviewed_by`, `reviewed_on` | Why, and review trail |

Key: `psa_label`. A new or renamed PSA label fails check `DQ-PSA-01`; add it here and rerun.
