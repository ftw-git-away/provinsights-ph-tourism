-- dataset: ds_aq1_rank
-- display: AQ1: top and bottom 10 by overnight travelers
-- source: tuklas_dev.05_analytics (tourism_activity)
-- used by: Page 1: top 10 and bottom 10 by overnight travelers, per year
SELECT * FROM (
  SELECT province_name AS place, region_name, unit_type, year, total_travelers, tourism_rank,
         RANK() OVER (PARTITION BY year ORDER BY total_travelers ASC) AS rank_from_bottom,
         CASE WHEN tourism_rank <= 10 THEN 'Top 10' ELSE 'Bottom 10' END AS rank_group
  FROM tourism_activity WHERE year BETWEEN 2019 AND 2023 AND activity_eligible)
WHERE tourism_rank <= 10 OR rank_from_bottom <= 10
