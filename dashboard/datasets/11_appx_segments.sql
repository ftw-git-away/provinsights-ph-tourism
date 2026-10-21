-- dataset: ds_appx_segments
-- display: Appendix: traveler types, places below 2019 in 2023
-- source: tuklas_dev.05_analytics (traveler_segment_recovery)
-- used by: Appendix B: recovery by traveler type, places below 2019 in 2023
SELECT province_name AS place, region_name, unit_type, 'Domestic' AS traveler_type,
       domestic_eligible AS assessed, ROUND(domestic_recovery_index, 1) AS pct_of_2019
FROM traveler_segment_recovery
UNION ALL
SELECT province_name, region_name, unit_type, 'Foreign', foreign_eligible, ROUND(foreign_recovery_index, 1)
FROM traveler_segment_recovery
UNION ALL
SELECT province_name, region_name, unit_type, 'Overseas Filipino', overseas_filipino_eligible, ROUND(overseas_filipino_recovery_index, 1)
FROM traveler_segment_recovery
