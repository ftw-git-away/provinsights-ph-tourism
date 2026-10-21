-- Duplicate check for every key in docs/data-dictionary.md.
-- ds_profile is a dashboard dataset, not a table: check it by running dashboard/datasets/05_profile_2023.sql
-- and comparing COUNT(*) with COUNT(DISTINCT place) (both 100).
-- Each row shows a table and how many key values appear more than once. Expect 0 everywhere.
SELECT 'ingestion_run_log' AS t, COUNT(*) AS dup_keys FROM (SELECT run_id FROM tuklas_dev.`01_ingestion`.ingestion_run_log GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'file_manifest', COUNT(*) FROM (SELECT run_id, source_dataset_id, source_file, COALESCE(source_sheet,''), destination_table FROM tuklas_dev.`01_ingestion`.file_manifest GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'silver_run_log', COUNT(*) FROM (SELECT run_id FROM tuklas_dev.`03_silver`.silver_run_log GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'gold_run_log', COUNT(*) FROM (SELECT run_id FROM tuklas_dev.`04_gold`.gold_run_log GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'geo_psgc', COUNT(*) FROM (SELECT psgc_code FROM tuklas_dev.`03_silver`.geo_psgc GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'map_dot_area_to_psgc', COUNT(*) FROM (SELECT dot_indent_level, COALESCE(dot_parent_label,''), dot_area_label, valid_from_year FROM tuklas_dev.`03_silver`.map_dot_area_to_psgc GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'map_psa_area_to_psgc', COUNT(*) FROM (SELECT psa_label FROM tuklas_dev.`03_silver`.map_psa_area_to_psgc GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'map_psa_population_area_to_psgc', COUNT(*) FROM (SELECT source_table, COALESCE(block_label,''), area_label FROM tuklas_dev.`03_silver`.map_psa_population_area_to_psgc GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'ref_indicator', COUNT(*) FROM (SELECT measure FROM tuklas_dev.`03_silver`.ref_indicator GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'dot_travelers_row', COUNT(*) FROM (SELECT _source_file, year, page_number, pdf_line_number FROM tuklas_dev.`03_silver`.dot_travelers_row GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'dot_excluded_rows', COUNT(*) FROM (SELECT _source_file, year, page_number, pdf_line_number FROM tuklas_dev.`03_silver`.dot_excluded_rows GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'psa_economy_row', COUNT(*) FROM (SELECT dataset_id, psa_label, year FROM tuklas_dev.`03_silver`.psa_economy_row GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'population_row', COUNT(*) FROM (SELECT source_table, COALESCE(source_row_number,-1), COALESCE(page_number,-1), COALESCE(pdf_line_number,-1), year FROM tuklas_dev.`03_silver`.population_row GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL SELECT 'analytics_run_log', COUNT(*) FROM (SELECT * FROM (SELECT run_id FROM tuklas_dev.`05_analytics`.analytics_run_log) GROUP BY ALL HAVING COUNT(*) > 1)
ORDER BY t;
