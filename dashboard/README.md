# ProvInsights dashboard

A Databricks AI/BI dashboard on tourism across the 100 reporting units. It shows where visitors go, how provinces compare on visitors and tourism-related output per visitor, whether high output per visitor is limited to higher-income provinces, and which provinces beyond the top 10 destinations warrant closer attention. It does not make recommendations or claim causes (DL-008).

**Shared dashboard (PROVINSIGHTS DASHBOARD):** https://dbc-5e346557-03d4.cloud.databricks.com/dashboardsv3/01f1cce3ab3a196c90b5fdc0a8a478a6/published

**Business question:** How can tourism and economic data across Philippine provinces be analysed to identify destinations that may warrant greater attention for tourism development? (See `docs/business-and-analytical-questions.md`.)

**Rule:** every chart and KPI reads the Analytics tables in `tuklas_dev.05_analytics`. Dataset queries only rename, label, reshape and filter, with one exception: the leading destinations, their yearly share, and the 2023 province profile (output per visitor, medians, groups, lagging). That logic lives in `dashboard/datasets/` (`01`, `04` and `05`–`08`), follows the definitions in `docs/business-and-analytical-questions.md` and decision log DL-031 to DL-037, and is the same in every file that uses it (the build script checks this). Any other new number goes into `notebooks/04_analytics/01_build_analytics` first.

## Why the pages changed (Oct 19 refocus and mentor feedback)

- The business question was finalised after the Oct 19 refocus, with one analytical question (AQ) per page.
- Roselle's feedback: keep a question the data can answer, show rather than prescribe, name the quadrants, and tell the "before ProvInsights" story. So page 4 shows **what the data shows** and **what to look at**, not recommended actions or lead agencies. The data can't speak to access, infrastructure, investment or governance.
- Group names are the descriptive ones agreed in the final document (Established, Busy but low-output, Small but high-output, Limited activity). "Emerging" was dropped because the data doesn't show growth: of the 21 provinces in that group, 11 are above their 2019 level and 10 below.
- The earlier recovery pages are kept as **Appendix A and B** for context. They are not part of the four AQs.

## Status

| Page | Question | Ready? |
| --- | --- | --- |
| Start here | What are we missing when we only look at the usual destinations? | Yes |
| 1. Where visitors go | AQ1: Which provinces have the highest and lowest tourism activity, and how is it distributed? | Yes |
| 2. Visitors and output per visitor | AQ2: How do provinces compare on both the number of visitors and the tourism-related output per visitor? | Yes |
| 3. Output and income | AQ3: Is high tourism-related output per visitor found only in higher-income provinces? | Yes |
| 4. Provinces to watch | AQ4: Which provinces beyond the top 10 destinations warrant closer attention, and what does the data show for each? | Yes |
| Definitions | Terms, data notes, out of scope, lineage | Yes |
| Appendix A. Tourism recovery | Supporting: places above or below 2019 | Yes |
| Appendix B. Traveler recovery | Supporting: traveler types behind among places below 2019 | Yes |

## Build and update

The shared dashboard lives in Databricks and keeps one link. It is **not** deployed by the bundle: the `refresh_dashboard` job task (#85) refreshes it at the end of every pipeline run, using `dashboard_id` and `warehouse_id` in `databricks.yml`. This folder keeps the exported JSON and the dataset SQL so the queries are versioned and reviewable.

1. **Change a query:** edit the file in `datasets/`, then paste the same SQL into that dataset on the shared dashboard's **Data** tab and publish. Run `python dashboard/tools/build_lvdash.py` so the JSON here matches.
2. **Change the layout or text:** edit the shared dashboard in Databricks and publish. Then **⋮ → Export dashboard**, save the file as `dashboard/provinsights.lvdash.json`, and run `python dashboard/tools/build_lvdash.py --check`.
3. **Re-create the dashboard** (only if it was deleted): **Dashboards → Create dashboard → ⋮ → Import dashboard from file** with `provinsights.lvdash.json`. Importing creates a **new** dashboard ID, so update `dashboard_id` in `databricks.yml` in a PR.
4. After a data change, reconcile the test units below.

## Datasets

One file per dataset. **Keep it to 10 datasets or fewer:** on the Free Edition each published dataset uses one of 10 METRIC_VIEW pipelines, and an 11th makes publishing fail (`PIPELINE_TYPE_QUOTA_EXCEEDED`). `build_lvdash.py` stops above 10. The page 3 correlation (0.19) and the Definitions lineage note are therefore text, not datasets. Each file starts with a header (`-- dataset:`, `-- display:`, `-- source:`, `-- used by:`) that the build script reads. Every dataset reads `tuklas_dev.05_analytics`; catalog and schema are set on the dataset, so the SQL uses table names only.

| File | Dataset | Grain (rows) | Source | Used by |
| --- | --- | --- | --- | --- |
| `01_aq1_year.sql` | `ds_aq1_year` | year (5) | `tourism_activity` (leading-destination share) | Page 1 counters and trend |
| `02_aq1_rank.sql` | `ds_aq1_rank` | unit × year, top and bottom 10 (100) | `tourism_activity` | Page 1 bar |
| `03_aq1_map.sql` | `ds_aq1_map` | unit × year (442) | `tourism_activity` | Page 1 map |
| `04_aq1_leading.sql` | `ds_aq1_leading` | unit (10) | `tourism_activity`, `tourism_economy` (leading destinations, DL-032) | Page 1 table |
| `05_profile_2023.sql` | `ds_profile` | unit (100) | `tourism_activity`, `tourism_economy`: 2023 profile and groups (DL-033 to DL-036) | Pages 2-4 |
| `07_aq3_table.sql` | `ds_aq3_table` | lagging unit with output data (43) | 2023 profile | Page 3 table |
| `08_aq4_table.sql` | `ds_aq4_table` | unit beyond the leading 10, with a group (83) | 2023 profile | Page 4 filters, map, table |
| `10_appx_recovery.sql` | `ds_appx_recovery` | unit × comparison year (200) | `tourism_recovery` | Appendix A |
| `11_appx_segments.sql` | `ds_appx_segments` | unit × traveler type (156) | `traveler_segment_recovery` | Appendix B |

Files 05, 07 and 08 carry the same 2023-profile block. `build_lvdash.py` stops if they differ, so change them together. Row counts are from a local run on the current `05_analytics`.

## Filters

| Filter | Field | Applies to | Type |
| --- | --- | --- | --- |
| Region | `region_name` | all pages (global) | multi-select |
| Type of unit | `unit_type` (Province, HUC, Independent city, NCR) | all pages (global) | multi-select |
| Year | `year` | Page 1 (not the trend line) | single-select, default 2023 |
| Group | `map_group` | Page 2 | multi-select |
| Show | `destination_group` (leading destinations / beyond) | Page 3 | multi-select |
| Group, Lagging, High output per visitor | `Group`, `Lagging`, `High output per visitor` | Page 4 | multi-select |
| Comparison year | `comparison_year` | Appendix A | single-select, default 2023 |

## Pages

**1. Where visitors go.** Counters: total overnight travelers, share to the 10 leading destinations, provinces reported. Map: travelers (size) and travelers per 1,000 residents (colour). Bar: top and bottom 10. Line: share of travelers going to the leading destinations, 2019-2023 (not affected by the Year filter). Table: the 10 leading destinations.

**2. Visitors and output per visitor.** Counters: provinces beyond the top 10 in each group. Example callout (Bataan vs Southern Leyte). Scatter "Each province placed in one of four groups": travelers vs output per visitor with the 2023 medians (279,150; ₱8,652), leading destinations in grey. Group guide.

**3. Output and income.** Counters: lagging provinces with high output per visitor (the answer), lagging provinces with output data, higher-income provinces with high output per visitor, correlation (supporting). Scatter: GDP per capita vs output per visitor with both medians. Bar: median output per visitor by income group. Table: lagging provinces by output per visitor, small bases marked.

**4. Provinces to watch.** Filters (Group, Lagging, High output per visitor) and counters (provinces shown; lagging with high output per visitor). Map by group (full width). Table: group, what the data shows, what to look at, lagging, high output per visitor, tourism share, travelers, output per visitor, small base. Ordered by group (Busy but low-output, Small but high-output, Limited activity, then Established last), then lagging first, then most visitors (DL-037). Established provinces stay in the list so the 13 lagging provinces with high output per visitor match page 3.

**Appendix A and B.** Recovery against 2019 (counters, sorted bar drawn up to 400 with exact values in the table, places not assessed with the reason), and traveler types among the 52 places below 2019 (coverage, median by type, table).

**Groups** (2023 medians of travelers and output per visitor):

| Group | What the data shows | What to look at |
| --- | --- | --- |
| Established | Many visitors, high output per visitor | Do the benefits reach nearby provinces? |
| Busy but low-output | Many visitors, low output per visitor | Where does visitor spending go? |
| Small but high-output | Few visitors, high output per visitor | What keeps visitor numbers low? (Check that the output isn't mostly residents' spending.) |
| Limited activity | Few visitors, low output per visitor | How does tourism compare with other sectors here? |

Wording on every page: "moves with", "stands out", "warrants a closer look". Never "drives", "causes" or "should invest".

## Text widgets

### Definitions (Definitions page)

- **Province (reporting unit):** one of 100 areas: 82 provinces, 16 highly urbanized cities, the City of Isabela and NCR.
- **Overnight travelers (visitors):** travelers counted by DOT in accommodation establishments. Not unique visitors, not same-day visitors.
- **Leading tourist destinations:** the 10 provinces with the highest average annual overnight travelers, 2019-2023.
- **Tourism-related output:** A&F GVA at current prices (PSA), a proxy because PSA publishes tourism value added only nationally.
- **Output per visitor:** A&F GVA (thousand PHP) × 1,000 ÷ overnight travelers, 2023. **High output per visitor:** at or above the 2023 median (₱8,652).
- **Tourism share of the economy:** current-price A&F GVA ÷ current-price GDP × 100, 2023. Shown in the priority list for context; not used to order it.
- **Lagging (lower-income):** 2023 GDP per capita below the median (₱140,165). An income indicator, not a poverty measure.
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

| Unit | Type | 2023 travelers | 2023 rank | Intensity / 1,000 | Leading? | Group (page 2) | Output per visitor (₱) | A&F share | Lagging | High output per visitor | Recovery 2023 (App. A) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Quezon | Province | 1,264,181 | 12 | 543.0 | Yes | Established | 10,449 | 4.05% | Yes | Yes | 97.1 |
| Pampanga | Province | 1,655,887 | 5 | 671.6 | Yes | Established | 10,288 | 2.65% | No | Yes | 181.8 |
| Aklan | Province | 2,200,138 | 4 | 3,544.4 | Yes | Busy but low-output | 1,222 | 3.24% | Yes | No | not assessed |
| Basilan | Province | blank | — | blank | No | Insufficient data | blank | 0.10% | Yes | — | not assessed |
| City of Angeles | HUC | 157,666 | 66 | 277.1 | No | Small but high-output | 52,368 | 5.17% | No | Yes | 223.7 |
| City of Isabela | Independent city | 101,238 | 76 | 748.2 | No | Limited activity | 467 | 0.33% | Yes | No | 667.8 |
| NCR | NCR | 7,027,445 | 1 | 492.7 | Yes | Established | 13,890 | 1.29% | No | Yes | 231.4 |
| Mountain Province | Province | 142,219 | 69 | 898.9 | No | Limited activity | 8,295 | 6.11% | Yes | No | 79.6 |

Whole-dashboard checks, 2023:

- 43.7% of travelers went to the 10 leading destinations; 93 provinces reported.
- Beyond the top 10: Established 16, Busy but low-output 21, Small but high-output 25, Limited activity 21 (83). The 10 leading destinations: 6 Established, 4 Busy but low-output. 7 have insufficient data.
- AQ3: 14 of the 43 lagging provinces with output data have high output per visitor (33 of 50 higher-income). Median output per visitor ₱5,634 (lagging) vs ₱11,051. Correlation 0.19 (0.35 by rank).
- AQ4: 13 lagging provinces beyond the top 10 have high output per visitor; 3 of them are small base (Zamboanga Sibugay, Quirino, Apayao).
- Appendix A: 39 above 2019, 52 below, 9 not assessed. Appendix B coverage: domestic 52, foreign 47, overseas Filipino 26 of 52.

## Refresh

The pipeline job refreshes the dashboard with the task `refresh_dashboard`, which runs after `analytics_run_evidence`, so it always shows the latest validated data.

| Setting | Where |
| --- | --- |
| Dashboard ID | `dashboard_id` variable in `databricks.yml` |
| SQL warehouse | `warehouse_id` variable in `databricks.yml` |

**Who runs the refresh.** The job runs as the identity that deploys it: the owner of the deploy token used by `deploy.yml`. That identity needs at least **Can Run** on the dashboard, or the `refresh_dashboard` task fails.

**If the refresh fails.** A failed `refresh_dashboard` marks the whole job run as failed and sends the failure email, even though every table was already written. Check which task failed before assuming the data build failed.

**Editing.** Edit the dashboard in place in Databricks and publish (see *Build and update*). Don't re-import it: every import creates a new dashboard with a new ID. The pipeline only refreshes the data; it does not change the layout. If the dashboard is ever replaced, update `dashboard_id` in `databricks.yml` in a PR.
