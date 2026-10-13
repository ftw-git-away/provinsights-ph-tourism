# ProvInsights decision-support dashboard (Issue #61)

A Databricks AI/BI dashboard that helps the client explore tourism across the 100 reporting units and how it moves with the local economy. It supports decisions; it does not make recommendations or claim causes (DL-008).

**Rule:** every chart and KPI reads the Analytics tables in `tuklas_dev.05_analytics`. The dataset queries in `datasets/` only rename, label and reshape columns. They never recompute a metric. If a chart needs a number that isn't in Analytics, add it to `notebooks/05_analytics/01_build_analytics` first.

## Status

| Page | Can be built now? | Waiting on |
| --- | --- | --- |
| 1. Tourism Overview | Yes | #65 merged |
| 2. Tourism Recovery | Yes | #65 merged |
| 3. Traveler Recovery | Domestic only | #65 fix: foreign and overseas Filipino recovery are blocked (all NULL) until it reads `foreign_includes_overseas_filipinos` from Gold |
| 4. Tourism × Economy | Yes; labels come from Analytics (`tourism_economy_pattern_label`) | Team decision on the quadrant (sign-based in #65 vs. Roselle's high/low split at the median) |
| 5. Province Explorer | Yes | #65 merged |

## Build steps

1. In Databricks, go to **Dashboards → Create dashboard** and name it `ProvInsights PH Tourism`.
2. On the **Data** tab, add one dataset per file in `datasets/`, using the file name as the dataset name (for example, `ds_activity` for `01_activity.sql`). Paste the SQL as written.
3. Build the five pages below. Use the field names exactly as the datasets return them, so a filter on `region_name`, `unit_type` or `reporting_unit` can apply to every dataset at once.
4. Reconcile the test units (see **Test-unit reconciliation** below) before review.
5. Save the dashboard to the repo: **⋮ → Export dashboard** downloads `ProvInsights PH Tourism.lvdash.json`. Commit it as `dashboard/provinsights.lvdash.json`. It can be deployed with the bundle later (see **Deploying with the bundle**).

## Datasets

The core SQL lives in seven files in `datasets/`. Several charts need only part of a query (for example, only units with a recovery index), and AI/BI can't filter rows per chart. So the dashboard JSON wraps some files in a `WHERE` clause to make extra datasets. These wrappers only filter rows; they never change a value.

| File | Grain | Source table | Datasets in `provinsights.lvdash.json` |
| --- | --- | --- | --- |
| `01_activity.sql` | unit × year (600) | `tourism_activity` | `ds_activity`; `ds_top_travelers` and `ds_top_intensity` (rank 1–15); `ds_bottom_travelers` and `ds_bottom_intensity` (lowest 15 ranks per year); `ds_activity_excluded` (not included) |
| `02_concentration.sql` | year (6) | `tourism_concentration` | `ds_concentration` (KPIs, follows the Year filter); `ds_concentration_trend` (same query, ignores the Year filter) |
| `03_recovery.sql` | unit × comparison year (200) | `tourism_recovery` | `ds_recovery`; `ds_recovery_eligible`; `ds_recovery_excluded` |
| `04_recovery_2022_vs_2023.sql` | unit (100) | `tourism_recovery`, 2022 and 2023 side by side | `ds_recovery_compare` (units with both years) |
| `05_segment_recovery.sql` | unit × comparison year × segment (600) | `traveler_segment_recovery`, unpivoted | `ds_segments`; `ds_segments_cohort` (below 2019, assessed); `ds_segments_mix` (below 2019, all segments); `ds_segments_excluded` |
| `06_economy.sql` | unit (100) | `tourism_economy` | `ds_economy`; `ds_economy_aligned` (assessed); `ds_economy_capped` (changes above +300%) |
| `07_unit_caveats.sql` | unit × year with a caveat (75) | `tourism_activity` | `ds_caveats` |

**Edit the SQL in `datasets/`, then rebuild the JSON** with `python dashboard/tools/build_lvdash.py` and re-import it. The JSON keeps its own copy of the SQL, so editing only the `.sql` files does not change the dashboard.

Row counts are from a local run of #65 (commit `a4e6312`) on the Gold tables from #56.

## Filters

| Filter | Field | Applies to | Type |
| --- | --- | --- | --- |
| Region | `region_name` | all pages (global filter) | multi-select |
| Unit type | `unit_type` (Province, HUC, Independent city, NCR) | all pages (global filter) | multi-select |
| Year | `year` | Page 1 | single-select, default 2023 |
| Comparison year | `comparison_year` | Pages 2 and 3 | single-select, default 2023 |
| Pattern | `pattern` | Page 4 | multi-select |
| Reporting unit | `reporting_unit` | Page 5 | single-select, default Quezon |

## Pages

### 1. Tourism Overview: where is tourism activity highest?

| Widget | Dataset | Type | Fields and settings |
| --- | --- | --- | --- |
| Travelers in included units | `ds_concentration` | Counter | `eligible_total_travelers`. Subtitle: "Included reporting units only; not a national total." |
| Units included / not included | `ds_concentration` | Counter ×2 | `eligible_reporting_unit_count`, `excluded_reporting_unit_count` |
| Top 5 / Top 10 share | `ds_concentration` | Counter ×2 | `top_5_share_pct`, `top_10_share_pct` (1 decimal, %) |
| Top 15 units by travelers | `ds_activity` | Bar (horizontal) | Y `reporting_unit`, X `total_travelers`, color `unit_type`; filter `activity_eligible = true`, `tourism_rank <= 15` |
| Top 15 units by tourism intensity | `ds_activity` | Bar (horizontal) | X `tourism_intensity_per_1000`; filter `intensity_eligible = true`, `intensity_rank <= 15` |
| Lowest 15 units by travelers | `ds_bottom_travelers` | Bar (horizontal, ascending) | Lowest 15 ranks among units with reported data (2023: Apayao, Quirino, Zamboanga Sibugay, Batanes, Dinagat Islands...) |
| Lowest 15 units by tourism intensity | `ds_bottom_intensity` | Bar (horizontal, ascending) | Lowest 15 intensity ranks among units with data and population |
| Concentration over time | `ds_concentration` | Line | X `year`, Y `top_5_share_pct` and `top_10_share_pct` |
| Units not included this year | `ds_activity` | Table | `reporting_unit`, `unit_type`, `data_status`, `activity_exclusion_reason`; filter `activity_eligible = false` |

### 2. Tourism Recovery: which units are above or below 2019?

| Widget | Dataset | Type | Fields and settings |
| --- | --- | --- | --- |
| Above / below / not assessed | `ds_recovery` | Counter ×3 | Count of rows where `recovery_status` = Above 2019 / Below 2019 / Not assessed |
| Recovery status by region | `ds_recovery` | Stacked bar | X `region_name`, Y count, color `recovery_status` |
| Recovery index by unit | `ds_recovery` | Bar (horizontal, sorted) | Y `reporting_unit`, X `recovery_index`, color `recovery_status`; filter `recovery_eligible = true`. Title says "100 = same as 2019". |
| 2022 vs 2023 | `ds_recovery_compare` | Scatter | X `recovery_index_2022`, Y `recovery_index_2023`, color `recovery_class_2023`, tooltip `reporting_unit` |
| Not assessed and why | `ds_recovery` | Table | `reporting_unit`, `recovery_exclusion_reason`; filter `recovery_eligible = false` |

### 3. Traveler Recovery: which traveler groups are behind?

Show this page for units below 2019 (`segment_analysis_cohort_flag = true`), with a toggle to show all.

| Widget | Dataset | Type | Fields and settings |
| --- | --- | --- | --- |
| Segment recovery by unit | `ds_segments` | Grouped bar | Y `reporting_unit`, X `recovery_index`, color `segment`; filter `eligible = true` |
| Traveler mix, 2019 vs comparison year | `ds_segments` | 100% stacked bar | X `reporting_unit`, Y `travelers_2019` (and a second chart for `travelers_comparison`), color `segment` |
| Segments not assessed | `ds_segments` | Table | `reporting_unit`, `segment`, `exclusion_reason`; filter `eligible = false` |

Until #65 is fixed, the Foreign and Overseas Filipinos bars are empty, and the table lists them as blocked. Add a text note on the page until then.

### 4. Tourism × Economy: do tourism and the local economy move together?

| Widget | Dataset | Type | Fields and settings |
| --- | --- | --- | --- |
| Units by pattern | `ds_economy` | Bar | X `pattern`, Y count, color `alignment`. `pattern` is `tourism_economy_pattern_label` from Analytics, or "Not assessed" |
| Tourism change vs A&F growth | `ds_economy_aligned` | Scatter | X `afs_gva_growth_pct`, Y `tourism_change_pct_chart` (capped at +300% for display), color `pattern` |
| Very large changes | `ds_economy_capped` | Table | The 5 units above +300% with exact values: Davao Occidental (+17,121%, from 188 travelers in 2019), Camarines Sur, Romblon, City of Isabela, Davao Oriental |
| Same vs opposite direction | `ds_economy` | Bar | X `alignment`, Y count |
| A&F share of GDP by pattern | `ds_economy` | Bar | X `pattern` (sort by `pattern_order`), Y median `afs_share_of_gdp_pct`; filter `afs_share_eligible = true` |
| Is strong tourism only in strong economies? | `ds_economy_aligned` | Scatter | X `gdp_per_capita_current_2019`, Y `recovery_index_2023_chart` (capped at 400), color `unit_type` |
| Units by pattern | `ds_economy` | Table | `reporting_unit`, `pattern`, `tourism_change_pct`, `afs_gva_growth_pct`, `afs_share_of_gdp_pct` |

Wording on this page: "moves with" or "diverges from", never "drives" or "causes".

**Why the cap:** without it, Davao Occidental (+17,121%) stretches the axis and the other 90 units collapse into a line. The cap only affects where a dot is drawn. The exact values stay in `tourism_change_pct` and are listed in the table. Remove the cap once Analytics adds a minimum-2019-base flag (see **Requested from Analytics and Gold**).

### 5. Province Explorer: one unit in one place

| Widget | Dataset | Type | Fields and settings |
| --- | --- | --- | --- |
| Unit type and region | `ds_economy` | Table (1 row) | `reporting_unit`, `unit_type`, `region_name` |
| 2023 KPIs | `ds_economy` | Counter ×6 | `travelers_2023`, `tourism_change_pct` (travelers vs 2019), `recovery_index_2023`, `tourism_intensity_per_1000_2023`, `afs_gva_growth_pct`, `afs_share_of_gdp_pct` |
| Travelers 2019–2024 | `ds_activity` | Line | X `year`, Y `total_travelers` (missing years stay as gaps, not 0) |
| Segment recovery | `ds_segments` | Bar | X `segment`, Y `recovery_index`, filtered by comparison year |
| Caveats for this unit | `ds_caveats` | Table | `year`, `caveat` |
| Year detail | `ds_activity` | Table | `year`, `total_travelers`, `population_total`, `tourism_intensity_per_1000`, `tourism_rank`, `data_status` |

## Map (planned)

Add a **point map**: one dot per reporting unit, size = travelers, colour = recovery status or pattern. Use it on the Overview and Tourism × Economy pages. Use dots rather than shaded province areas, because HUCs, City of Isabela and NCR are separate units that shaded province shapes would hide.

This needs `latitude` and `longitude` per unit, which the data doesn't have yet (see **Requested from Analytics and Gold**). Once Analytics carries them, add the two columns to `01_activity.sql` and `06_economy.sql` and add the map widgets in `tools/build_lvdash.py`.

## Requested from Analytics and Gold

| Request | Owner | Why |
| --- | --- | --- |
| Unit coordinates: seed `map_unit_centroid.csv` → `latitude` / `longitude` in `dim_province` → carried into the Analytics tables | Seed: Gabs; Gold: Charlene; Analytics: Nella | Point map |
| Minimum-2019-base flag in `tourism_recovery` and `tourism_economy` (threshold to agree, as with DL-006 / OI-7) | Nella | Small bases (Davao Occidental: 188 travelers) create extreme percentages |
| `tourism_economy_summary`: number of units, correlation (Pearson and Spearman), and count per pattern | Nella | BQ2 asks how strongly they are associated; the dashboard must not compute it |
| Read `foreign_includes_overseas_filipinos` from Gold | Nella | Traveler Recovery page |
| Quadrant definition (sign vs median split) | Team + Roselle | Tourism × Economy labels |

## Text widgets

### Definitions (pages 1, 2 and 4)

- **Reporting unit:** one of 100 areas: 82 provinces, 16 highly urbanized cities (HUCs), City of Isabela and NCR. HUCs are reported separately from their provinces.
- **Travelers:** overnight travelers counted by DOT in accommodation establishments.
- **Tourism intensity:** travelers per 1,000 residents in the same year.
- **Recovery index:** travelers in the comparison year ÷ travelers in 2019 × 100. 100 means back to the 2019 level.
- **A&F GVA growth:** change in real (constant 2018 prices) Accommodation and Food Services output, 2019 to 2023.
- **A&F share of GDP:** Accommodation and Food Services output as a share of the unit's GDP in 2023 (current prices).

### Data notes (all pages)

- Blank means DOT did not report the unit that year. It is never shown as 0.
- Where DOT printed "-" for a traveler category, it is counted as 0.
- Aklan is not compared with 2019 because DOT changed how it counts Aklan from 2021.
- Totals cover the included reporting units only, not the whole country.
- 2019 populations for HUCs are estimated from the 2020–2021 trend.
- Patterns show association, not cause.

## Test-unit reconciliation

Check these values in the dashboard against `05_analytics` (and Gold, via #65's cross-checks). The expected values below come from the local run.

| Unit | Type | 2023 travelers | 2023 rank | Intensity / 1,000 | Recovery 2022 | Recovery 2023 | Pattern | A&F share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Quezon | Province | 1,264,181 | 12 | 543.0 | 91.2 | 97.1 | Tourism activity decreased; real A&F GVA increased | 4.05% |
| Pampanga | Province | 1,655,887 | 5 | 671.6 | 123.4 | 181.8 | Tourism activity increased; real A&F GVA increased | 2.65% |
| Aklan | Province | 2,200,138 | 4 | 3,544.4 | not assessed (not comparable) | not assessed | Not assessed | 3.24% |
| Basilan | Province | blank | — | blank | not assessed (no 2019 data) | not assessed | Not assessed | 0.10% |
| City of Angeles | HUC | 157,666 | 66 | 277.1 | not assessed (no 2022 data) | 223.7 | Tourism activity increased; real A&F GVA decreased | 5.17% |
| City of Isabela | Independent city | 101,238 | 76 | 748.2 | 82.1 | 667.8 | Tourism activity increased; real A&F GVA decreased | 0.33% |
| NCR | NCR | 7,027,445 | 1 | 492.7 | 155.0 | 231.4 | Tourism activity increased; real A&F GVA decreased | 1.29% |

Whole-dashboard checks for 2023: 39 units above 2019, 52 below and 9 not assessed. The patterns are 26 up/up, 13 tourism up with A&F down, 30 tourism down with A&F up, 22 down/down and 9 not assessed.

## Deploying with the bundle

Once the dashboard is exported, add `resources/dashboards/provinsights.yml`:

```yaml
resources:
  dashboards:
    provinsights:
      display_name: ProvInsights PH Tourism
      file_path: ../../dashboard/provinsights.lvdash.json
      warehouse_id: <SQL warehouse ID>
```

Then add `- resources/dashboards/*.yml` under `include:` in `databricks.yml`. `deploy.yml` already redeploys on changes under `dashboard/**`.
