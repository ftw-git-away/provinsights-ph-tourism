-- ds_recovery_compare: one row per reporting unit (100 rows), 2022 and 2023 side by side.
-- Source: 05_analytics.tourism_recovery (reshaped only).
-- Used by: Tourism Recovery scatter (2022 index vs 2023 index).
SELECT
  province_psgc,
  province_name                         AS reporting_unit,
  unit_type,
  region_name,
  MAX(CASE WHEN comparison_year = 2022 THEN recovery_index END) AS recovery_index_2022,
  MAX(CASE WHEN comparison_year = 2023 THEN recovery_index END) AS recovery_index_2023,
  MAX(CASE WHEN comparison_year = 2023 THEN recovery_class END) AS recovery_class_2023
FROM tuklas_dev.`05_analytics`.tourism_recovery
GROUP BY province_psgc, province_name, unit_type, region_name
