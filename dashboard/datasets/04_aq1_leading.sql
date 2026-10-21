-- dataset: ds_aq1_leading
-- display: AQ1: the leading destinations (Query 1)
-- source: tuklas_dev.05_analytics (tourism_activity, tourism_economy)
-- used by: Page 1: the 10 leading destinations (Query 1)
SELECT q.province_name AS `Province`, e.region_name, e.unit_type, q.avg_travelers_rank AS `Rank (2019-2023 average)`,
       ROUND(q.avg_travelers_2019_2023, 0) AS `Average overnight travelers per year, 2019-2023`
FROM (
SELECT province_psgc,
       province_name,
       AVG(total_travelers)                                    AS avg_travelers_2019_2023,
       RANK() OVER (ORDER BY AVG(total_travelers) DESC)        AS avg_travelers_rank,
       RANK() OVER (ORDER BY AVG(total_travelers) DESC) <= 10  AS is_leading_destination
FROM tourism_activity
WHERE year BETWEEN 2019 AND 2023
  AND activity_eligible
GROUP BY province_psgc, province_name
) q JOIN tourism_economy e USING (province_psgc)
WHERE q.is_leading_destination
ORDER BY q.avg_travelers_rank
