-- ds_recovery: one row per reporting unit and comparison year (2022, 2023; 200 rows).
-- Source: 05_analytics.tourism_recovery.
-- Used by: Tourism Recovery (class counts, recovery index bars, units not assessed), Province Explorer.
SELECT
  province_psgc,
  province_name                         AS reporting_unit,
  unit_type,
  region_name,
  comparison_year,
  travelers_2019,
  travelers_comparison_year,
  traveler_change_absolute,
  recovery_index,
  CASE recovery_class
    WHEN 'above_2019' THEN 'Above 2019'
    WHEN 'unchanged'  THEN 'Same as 2019'
    WHEN 'below_2019' THEN 'Below 2019'
    ELSE 'Not assessed'
  END                                   AS recovery_status,
  recovery_eligible,
  recovery_exclusion_reason,
  comp_comparison                       AS comparable_to_2019,   -- comparison year comparable to 2019
  comparability_note
FROM tuklas_dev.`05_analytics`.tourism_recovery
