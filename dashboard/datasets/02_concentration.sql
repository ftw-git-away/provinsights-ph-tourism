-- ds_concentration: one row per year (6 rows).
-- Source: 05_analytics.tourism_concentration.
-- Used by: Tourism Overview KPIs and the Top 5 / Top 10 share chart.
SELECT
  year,
  eligible_reporting_unit_count,
  excluded_reporting_unit_count,
  eligible_total_travelers,
  top_5_travelers,
  top_5_share_pct,
  top_10_travelers,
  top_10_share_pct,
  coverage_note
FROM tuklas_dev.`05_analytics`.tourism_concentration
