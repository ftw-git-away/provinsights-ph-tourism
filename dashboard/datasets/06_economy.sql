-- ds_economy: one row per reporting unit (100 rows), 2019 vs 2023.
-- Source: 05_analytics.tourism_economy. The pattern and its label both come from Analytics.
-- Used by: Tourism x Economy (scatter, pattern counts, A&F share), Province Explorer KPIs.
SELECT
  province_psgc,
  province_name                         AS reporting_unit,
  unit_type,
  region_name,
  travelers_2019,
  travelers_2023,
  recovery_index_2023,
  tourism_change_pct,
  -- Chart-only copies, capped so a few very large changes from small 2019 bases do not flatten the scatter.
  -- Exact values stay in tourism_change_pct / recovery_index_2023 and are listed in a table next to the chart.
  LEAST(tourism_change_pct, 300)        AS tourism_change_pct_chart,
  LEAST(recovery_index_2023, 400)       AS recovery_index_2023_chart,
  coalesce(tourism_change_pct > 300, false) AS shown_at_chart_cap,
  afs_gva_growth_pct,
  afs_share_of_gdp_pct,
  gdp_per_capita_current_2019,
  gdp_per_capita_current_2023,
  tourism_intensity_per_1000_2023,
  coalesce(tourism_economy_pattern_label, 'Not assessed') AS pattern,   -- approved wording from Analytics (#65)
  CASE tourism_economy_pattern
    WHEN 'tourism_up_economy_up'     THEN 1
    WHEN 'tourism_up_economy_down'   THEN 2
    WHEN 'tourism_down_economy_up'   THEN 3
    WHEN 'tourism_down_economy_down' THEN 4
    ELSE 9
  END                                   AS pattern_order,
  CASE WHEN tourism_economy_pattern IN ('tourism_up_economy_up', 'tourism_down_economy_down')
       THEN 'Same direction'
       WHEN tourism_economy_pattern IN ('tourism_up_economy_down', 'tourism_down_economy_up')
       THEN 'Opposite directions'
       WHEN tourism_economy_pattern = 'unchanged' THEN 'No change'
       ELSE 'Not assessed'
  END                                   AS alignment,
  alignment_eligible,
  alignment_exclusion_reason,
  afs_share_eligible,
  intensity_gdp_context_eligible,
  comparable_to_2019,
  comparability_note,
  population_source_2023
FROM tuklas_dev.`05_analytics`.tourism_economy
