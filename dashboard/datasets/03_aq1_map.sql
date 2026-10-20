-- dataset: ds_aq1_map
-- display: AQ1: map of tourism intensity
-- source: tuklas_dev.05_analytics (tourism_activity)
-- used by: Page 1: map, travelers and travelers per 1,000 residents, per year
SELECT province_name AS place, region_name, unit_type, year, latitude, longitude, total_travelers,
       ROUND(tourism_intensity_per_1000, 0) AS tourism_intensity_per_1000, intensity_rank,
       CASE WHEN tourism_intensity_per_1000 < 100 THEN 'Under 100' WHEN tourism_intensity_per_1000 < 300 THEN '100-300'
            WHEN tourism_intensity_per_1000 < 1000 THEN '300-999' ELSE '1,000 or more' END AS intensity_band
FROM tourism_activity
WHERE year BETWEEN 2019 AND 2023 AND intensity_eligible AND latitude IS NOT NULL
