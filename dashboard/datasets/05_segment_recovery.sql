-- ds_segments: one row per reporting unit, comparison year and traveler segment (600 rows).
-- Source: 05_analytics.traveler_segment_recovery, unpivoted so one chart can show all three segments.
-- Used by: Traveler Recovery (segment index by unit, composition), Province Explorer.
WITH s AS (
  SELECT * FROM tuklas_dev.`05_analytics`.traveler_segment_recovery
)
SELECT province_psgc, province_name AS reporting_unit, unit_type, region_name, comparison_year,
       'Domestic' AS segment, 1 AS segment_order,
       domestic_travelers_2019 AS travelers_2019, domestic_travelers_comparison AS travelers_comparison,
       domestic_recovery_index AS recovery_index, domestic_recovery_class AS recovery_class,
       domestic_eligible AS eligible, domestic_exclusion_reason AS exclusion_reason,
       overall_recovery_index, below_2019_total_flag, segment_analysis_cohort_flag, comparability_note
FROM s
UNION ALL
SELECT province_psgc, province_name, unit_type, region_name, comparison_year,
       'Foreign', 2,
       foreign_travelers_2019, foreign_travelers_comparison,
       foreign_recovery_index, foreign_recovery_class,
       foreign_eligible, foreign_exclusion_reason,
       overall_recovery_index, below_2019_total_flag, segment_analysis_cohort_flag, comparability_note
FROM s
UNION ALL
SELECT province_psgc, province_name, unit_type, region_name, comparison_year,
       'Overseas Filipinos', 3,
       overseas_filipinos_2019, overseas_filipinos_comparison,
       overseas_filipino_recovery_index, overseas_filipino_recovery_class,
       overseas_filipino_eligible, overseas_filipino_exclusion_reason,
       overall_recovery_index, below_2019_total_flag, segment_analysis_cohort_flag, comparability_note
FROM s
