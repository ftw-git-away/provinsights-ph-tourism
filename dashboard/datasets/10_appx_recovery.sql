-- dataset: ds_appx_recovery
-- display: Appendix: recovery compared with 2019
-- source: tuklas_dev.05_analytics (tourism_recovery)
-- used by: Appendix A: recovery compared with 2019
SELECT province_name AS place, region_name, unit_type, comparison_year, recovery_eligible,
       ROUND(recovery_index, 1) AS pct_of_2019,
       CASE WHEN recovery_index > 400 THEN 400 ELSE ROUND(recovery_index, 1) END AS pct_of_2019_chart,
       CASE recovery_class WHEN 'above_2019' THEN 'Above 2019' WHEN 'below_2019' THEN 'Below 2019' ELSE 'Not assessed' END AS status,
       travelers_2019, travelers_comparison_year,
       recovery_exclusion_reason AS why_not_assessed
FROM tourism_recovery
