-- ds_segments: one row per reporting unit and traveler segment (units below 2019 in 2023: 52 units x 3 segments).
-- Source: 05_analytics.traveler_segment_recovery (2023 vs 2019 only), unpivoted so one chart can show all three segments.
-- Used by: Traveler Recovery (segment index by unit, traveler mix, coverage), Province Explorer.
WITH s AS (
  SELECT * FROM tuklas_dev.`05_analytics`.traveler_segment_recovery
)
SELECT province_psgc, province_name AS reporting_unit, unit_type, region_name, comparison_year,
       'Domestic' AS segment, 1 AS segment_order,
       domestic_travelers_2019 AS travelers_2019, domestic_travelers_2023 AS travelers_comparison,
       domestic_recovery_index AS recovery_index, domestic_recovery_class AS recovery_class,
       domestic_eligible AS eligible, domestic_exclusion_reason AS exclusion_reason,
       CASE WHEN domestic_eligible THEN 'Assessed' ELSE 'Not assessed' END AS coverage_status,
       overall_recovery_index, foreign_includes_overseas_filipinos, comparability_note
FROM s
UNION ALL
SELECT province_psgc, province_name, unit_type, region_name, comparison_year,
       'Foreign', 2,
       foreign_travelers_2019, foreign_travelers_2023,
       foreign_recovery_index, foreign_recovery_class,
       foreign_eligible, foreign_exclusion_reason,
       CASE WHEN foreign_eligible THEN 'Assessed' ELSE 'Not assessed' END,
       overall_recovery_index, foreign_includes_overseas_filipinos, comparability_note
FROM s
UNION ALL
SELECT province_psgc, province_name, unit_type, region_name, comparison_year,
       'Overseas Filipinos', 3,
       overseas_filipino_travelers_2019, overseas_filipino_travelers_2023,
       overseas_filipino_recovery_index, overseas_filipino_recovery_class,
       overseas_filipino_eligible, overseas_filipino_exclusion_reason,
       CASE WHEN overseas_filipino_eligible THEN 'Assessed' ELSE 'Not assessed' END,
       overall_recovery_index, foreign_includes_overseas_filipinos, comparability_note
FROM s
