-- ds_activity: one row per reporting unit and year (600 rows).
-- Source: 05_analytics.tourism_activity. Labels only; no metric is recalculated.
-- Used by: Tourism Overview (top units, intensity, excluded units), Province Explorer (trend).
SELECT
  province_psgc,
  province_name                         AS reporting_unit,
  unit_type,
  region_name,
  year,
  latitude,                             -- map point (Gold dim_province, COD-AB)
  longitude,
  total_travelers,                      -- NULL when DOT did not report; never shown as 0
  population_total,
  tourism_intensity_per_1000,
  tourism_rank,
  intensity_rank,
  tourism_share_pct,
  CASE traveler_value_status
    WHEN 'reported'         THEN 'Reported'
    WHEN 'dash_as_zero'     THEN 'Reported (blank categories counted as 0)'
    WHEN 'reported_partial' THEN 'Partly reported'
    WHEN 'not_reported'     THEN 'Not reported by DOT'
  END                                   AS data_status,
  comparable_to_2019,
  comparability_note,
  activity_eligible,
  activity_exclusion_reason,
  intensity_eligible,
  intensity_exclusion_reason
FROM tuklas_dev.`05_analytics`.tourism_activity
