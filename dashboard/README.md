# ProvInsights dashboard

A Databricks AI/BI dashboard on tourism across the 100 reporting units. It shows where visitors go, how much tourism-related output each visitor brings, how much each economy relies on tourism, and which provinces outside the usual destinations warrant closer attention. It does not make recommendations or claim causes (DL-008).

**Business question:** Which provinces beyond the usual destinations warrant closer attention, based on their tourism activity and the tourism-related output it generates? (See `docs/business-and-analytical-questions.md`.)

**Rule:** every chart and KPI reads the Analytics tables in `tuklas_dev.05_analytics`. Dataset queries only rename, label, reshape and filter, with one exception: the document's **Query 1–3** (leading destinations, their yearly share, and the 2023 province profile: earnings per visitor, medians, groups, lagging, tourism-dependent). These are used exactly as written in the document, so the dashboard and the document can't disagree. Any other new number goes into `notebooks/05_analytics/01_build_analytics` first.

## Why the pages changed (Oct 19 refocus and mentor feedback)

- The business question changed on Oct 19, with one analytical question (AQ) per page.
- Roselle's feedback: keep a question the data can answer, show rather than prescribe, name the quadrants, and tell the "before ProvInsights" story. So page 4 shows **what stands out** and **what to look at**, not recommended actions or lead agencies. The data can't speak to access, infrastructure, investment or governance.
- The earlier recovery pages are kept as **Appendix A and B** for context. They are not part of the four AQs.

## Status

| Page | Question | Ready? |
| --- | --- | --- |
| Start here | What are we missing when we only look at the usual destinations? | Yes |
| 1. Where visitors go | AQ1: highest and lowest tourism activity, and concentration in the leading destinations | Yes |
| 2. Same visitors, different benefits | AQ2: if two provinces attract the same number of visitors, do they benefit the same way? | Yes |
| 3. Tourism and wealth | AQ3: which provinces rely most on tourism, and are lower-income provinces among them? | Yes |
| 4. Provinces to watch | AQ4: which provinces outside the usual destinations warrant closer attention, and why? | Yes |
| Definitions | Terms, data notes, out of scope, lineage | Yes |
| Appendix A. Tourism recovery | Supporting: places above or below 2019 | Yes |
| Appendix B. Traveler recovery | Supporting: traveler types behind among places below 2019 | Yes |

## Build and update

1. Run the Analytics notebook so `tuklas_dev.05_analytics` exists.
2. **Dashboards → Create dashboard → ⋮ → Import dashboard from file** → `dashboard/provinsights.lvdash.json`.
3. Reconcile the test units below.
4. To change a **query**: edit the file in `datasets/`, run `python dashboard/tools/build_lvdash.py` from the repo root, and re-import. Editing only the `.sql` file changes nothing in Databricks.
5. To change the **layout**: edit in Databricks, then **⋮ → Export dashboard**, save it as `dashboard/provinsights.lvdash.json`, and run `python dashboard/tools/build_lvdash.py --check` to confirm the SQL still matches.

## Datasets

One file per dataset. Each file starts with a header (`-- dataset:`, `-- display:`, `-- source:`, `-- used by:`) that the build script reads. Every dataset reads `tuklas_dev.05_analytics`; catalog and schema are set on the dataset, so the SQL uses table names only.

| File | Dataset | Grain (rows) | Source | Used by |
| --- | --- | --- | --- | --- |
| `01_aq1_year.sql` | `ds_aq1_year` | year (5) | `tourism_activity` (Query 2) | Page 1 counters and trend |
| `02_aq1_rank.sql` | `ds_aq1_rank` | unit × year, top and bottom 10 (100) | `tourism_activity` | Page 1 bar |
| `03_aq1_map.sql` | `ds_aq1_map` | unit × year (442) | `tourism_activity` | Page 1 map |
| `04_aq1_leading.sql` | `ds_aq1_leading` | unit (10) | `tourism_activity`, `tourism_economy` (Query 1) | Page 1 table |
| `05_profile_2023.sql` | `ds_profile` | unit (100) | Query 3 + group names | Pages 2-4 |
| `06_aq3_corr.sql` | `ds_aq3_corr` | one row | Query 3 | Page 3 correlation |
| `07_aq3_table.sql` | `ds_aq3_table` | lagging unit (50) | Query 3 | Page 3 table |
| `08_aq4_table.sql` | `ds_aq4_table` | unit beyond the leading 10, with a group (83) | Query 3 | Page 4 filters, map, table |
| `09_lineage.sql` | `ds_lineage` | one row | `tourism_activity` | Definitions |
| `10_appx_recovery.sql` | `ds_appx_recovery` | unit × comparison year (200) | `tourism_recovery` | Appendix A |
| `11_appx_segments.sql` | `ds_appx_segments` | unit × traveler type (156) | `traveler_segment_recovery` | Appendix B |

Files 05-08 carry the same Query 3 block. `build_lvdash.py` stops if they differ, so change them together. Row counts are from a local run on the current `05_analytics`.

## Filters

| Filter | Field | Applies to | Type |
| --- | --- | --- | --- |
| Region | `region_name` | all pages (global) | multi-select |
| Type of unit | `unit_type` (Province, HUC, Independent city, NCR) | all pages (global) | multi-select |
| Year | `year` | Page 1 (not the trend line) | single-select, default 2023 |
| Group | `map_group` | Page 2 | multi-select |
| Show | `destination_group` (leading destinations / beyond) | Page 3 | multi-select |
| Group, Lagging, Tourism-dependent | `Group`, `Lagging`, `Tourism-dependent` | Page 4 | multi-select |
| Comparison year | `comparison_year` | Appendix A | single-select, default 2023 |

## Pages

**1. Where visitors go.** Counters: total overnight travelers, share to the 10 leading destinations, provinces reported. Map: travelers (size) and travelers per 1,000 residents (colour). Bar: top and bottom 10. Line: travelers 2019-2023. Table: the 10 leading destinations.

**2. Same visitors, different benefits.** Counters: provinces beyond the leading destinations in each group. Example callout (Bataan vs Southern Leyte). Scatter: travelers vs earnings per visitor with the 2023 medians (279,150; ₱8,652), leading destinations in grey. Group guide. Bar: earnings per visitor, sorted.

**3. Tourism and wealth.** Counters: lagging and tourism-dependent (the answer), lagging, median tourism share, correlation (supporting). Scatter: GDP per capita vs tourism share. Bar: average share by income group. Table: lagging provinces by tourism share.

**4. Provinces to watch.** Filters and counters (provinces shown; lagging and tourism-dependent). Map by group. "What to look at" guide. Table: group, what stands out, what to look at, lagging, tourism-dependent, share, travelers, earnings per visitor, small base.

**Appendix A and B.** Recovery against 2019 (counters, sorted bar drawn up to 400 with exact values in the table, places not assessed with the reason), and traveler types among the 52 places below 2019 (coverage, median by type, table).

**Groups** (2023 medians of travelers and earnings per visitor):

| Group | What the data shows | What to look at |
| --- | --- | --- |
| Tourism Leaders | Many visitors, high earnings per visitor | Do the benefits reach nearby provinces? |
| Visitor Magnets | Many visitors, low earnings per visitor | Where does visitor spending go? |
| High-Value Niches | Few visitors, high earnings per visitor | What keeps visitor numbers low? (Check that the output isn't mostly residents' spending.) |
| Emerging Tourism Areas | Few visitors, low earnings per visitor | If tourism-dependent: what holds visitors back? Otherwise: how does tourism compare with other sectors? |

Wording on every page: "moves with", "stands out", "warrants a closer look". Never "drives", "causes" or "should invest".

## Text widgets

### Definitions (Definitions page)

- **Province (reporting unit):** one of 100 areas: 82 provinces, 16 highly urbanized cities, the City of Isabela and NCR.
- **Overnight travelers:** travelers counted by DOT in accommodation establishments. Not unique visitors, not day-trippers.
- **Leading tourist destinations:** the 10 provinces with the highest average annual overnight travelers, 2019-2023.
- **Earnings per visitor:** A&F GVA (thousand PHP) × 1,000 ÷ overnight travelers, 2023.
- **Tourism share of the economy:** current-price A&F GVA ÷ current-price GDP × 100, 2023.
- **Lagging (lower-income):** 2023 GDP per capita below the median. **Tourism-dependent:** 2023 tourism share above the median (1.9%).
- **Small base:** under 10,000 travelers in 2023; kept, marked "Check before naming".

### Data notes (all pages)

- Blank means DOT did not report the unit that year. It is never shown as 0.
- Hotel and restaurant output (A&F) is a proxy for tourism. It includes residents' spending and misses transport, tours and souvenirs.
- Medians and groups are positions among provinces with 2023 data, not national benchmarks.
- Some towns that printed "-" in 2019 reported in 2023, so part of the rise in several places (NCR among them) reflects wider reporting (OI-5).
- Aklan is not compared with 2019 because DOT changed how it counts Aklan from 2021.
- Patterns show association, not cause.
- **Out of scope:** access, infrastructure, investment, governance, safety and workforce readiness.

## Test-unit reconciliation

Check these in the dashboard against `05_analytics`. The expected values come from a local run on the current tables.

| Unit | Type | 2023 travelers | 2023 rank | Intensity / 1,000 | Leading? | Group (page 2) | Earnings per visitor (₱) | A&F share | Lagging | Tourism-dependent | Recovery 2023 (App. A) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Quezon | Province | 1,264,181 | 12 | 543.0 | Yes | Tourism Leaders | 10,449 | 4.05% | Yes | Yes | 97.1 |
| Pampanga | Province | 1,655,887 | 5 | 671.6 | Yes | Tourism Leaders | 10,288 | 2.65% | No | Yes | 181.8 |
| Aklan | Province | 2,200,138 | 4 | 3,544.4 | Yes | Visitor Magnets | 1,222 | 3.24% | Yes | Yes | not assessed |
| Basilan | Province | blank | — | blank | No | Insufficient data | blank | 0.10% | Yes | No | not assessed |
| City of Angeles | HUC | 157,666 | 66 | 277.1 | No | High-Value Niches | 52,368 | 5.17% | No | Yes | 223.7 |
| City of Isabela | Independent city | 101,238 | 76 | 748.2 | No | Emerging Tourism Areas | 467 | 0.33% | Yes | No | 667.8 |
| NCR | NCR | 7,027,445 | 1 | 492.7 | Yes | Tourism Leaders | 13,890 | 1.29% | No | No | 231.4 |
| Mountain Province | Province | 142,219 | 69 | 898.9 | No | Emerging Tourism Areas | 8,295 | 6.11% | Yes | Yes | 79.6 |

Whole-dashboard checks, 2023:

- 43.7% of travelers went to the 10 leading destinations; 93 provinces reported.
- Beyond the leading destinations: Tourism Leaders 16, Visitor Magnets 21, High-Value Niches 25, Emerging Tourism Areas 21 (83). The 10 leading destinations: 6 Tourism Leaders, 4 Visitor Magnets. 7 have insufficient data.
- 50 lagging, 14 of them tourism-dependent (10 outside the leading destinations). Median tourism share 1.88%. Correlation 0.48.
- Appendix A: 39 above 2019, 52 below, 9 not assessed. Appendix B coverage: domestic 52, foreign 47, overseas Filipino 26 of 52.

## Deploying with the bundle

Add `resources/dashboards/provinsights.yml`:

```yaml
resources:
  dashboards:
    provinsights:
      display_name: ProvInsights PH Tourism
      file_path: ../../dashboard/provinsights.lvdash.json
      warehouse_id: <SQL warehouse ID>
```

Then add `- resources/dashboards/*.yml` under `include:` in `databricks.yml`. `deploy.yml` already redeploys on changes under `dashboard/**`.
