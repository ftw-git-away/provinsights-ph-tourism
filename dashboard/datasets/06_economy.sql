-- ds_economy: one row per reporting unit (100 rows), 2019 vs 2023.
-- Source: 05_analytics.tourism_economy. Pattern labels only; the pattern itself comes from Analytics.
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
  afs_gva_growth_pct,
  afs_share_of_gdp_pct,
  gdp_per_capita_current_2019,
  gdp_per_capita_current_2023,
  tourism_intensity_per_1000_2023,
  CASE tourism_economy_pattern
    WHEN 'tourism_up_economy_up'     THEN 'Tourism up, A&F up'
    WHEN 'tourism_up_economy_down'   THEN 'Tourism up, A&F down'
    WHEN 'tourism_down_economy_up'   THEN 'Tourism down, A&F up'
    WHEN 'tourism_down_economy_down' THEN 'Tourism down, A&F down'
    WHEN 'unchanged'                 THEN 'No change'
    ELSE 'Not assessed'
  END                                   AS pattern,
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
