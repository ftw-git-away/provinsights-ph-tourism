-- dataset: ds_aq4_table
-- display: AQ4: provinces outside the leading destinations, 2023
-- source: tuklas_dev.05_analytics (tourism_activity, tourism_economy)
-- used by: Page 4: filters, map and table for provinces beyond the top 10 (same Query 3 logic)
SELECT place AS `Province`, region_name, unit_type, latitude, longitude, group_label AS `Group`, what_the_data_shows AS `What the data shows`, what_to_look_at AS `What to look at`, CASE WHEN is_lagging THEN 'Yes' ELSE 'No' END AS `Lagging`, CASE WHEN is_high_output THEN 'Yes' ELSE 'No' END AS `High output per visitor`, ROUND(afs_share_of_gdp_pct, 1) AS `Tourism share (%)`, travelers_2023 AS `Overnight travelers`, ROUND(earnings_per_visitor, 0) AS `Output per visitor (PHP)`, ROUND(gdp_per_capita_current_2023, 0) AS `GDP per capita (PHP)`, CASE WHEN small_base_2023 THEN 'Check before naming: under 10,000 travelers' END AS `Small base`
FROM (
WITH leading AS (
  SELECT province_psgc,
         RANK() OVER (ORDER BY AVG(total_travelers) DESC) <= 10 AS is_leading_destination
  FROM tourism_activity
  WHERE year BETWEEN 2019 AND 2023 AND activity_eligible
  GROUP BY province_psgc
),
base AS (
  SELECT e.province_psgc, e.province_name, e.region_name,
         e.travelers_2023, e.status_2023,
         e.afs_gva_current_2023, e.afs_share_of_gdp_pct, e.gdp_per_capita_current_2023,
         COALESCE(l.is_leading_destination, false) AS is_leading_destination,
         CASE WHEN e.status_2023 <> 'not_reported'
                   AND e.travelers_2023 > 0
                   AND e.afs_gva_current_2023 IS NOT NULL
              THEN e.afs_gva_current_2023 * 1000.0 / e.travelers_2023
         END AS earnings_per_visitor
  FROM tourism_economy e
  LEFT JOIN leading l ON e.province_psgc = l.province_psgc
),
medians AS (
  SELECT median(CASE WHEN earnings_per_visitor IS NOT NULL THEN travelers_2023 END) AS median_travelers,
         median(earnings_per_visitor)                                               AS median_earnings_per_visitor,
         median(gdp_per_capita_current_2023)                                        AS median_gdp_per_capita
  FROM base
),
classified AS (
  SELECT b.*,
         b.gdp_per_capita_current_2023 < m.median_gdp_per_capita AS is_lagging,
         b.travelers_2023 < 10000                                 AS small_base_2023,
         CASE
           WHEN b.earnings_per_visitor IS NULL THEN 'Insufficient data'
           WHEN b.travelers_2023 >= m.median_travelers
                AND b.earnings_per_visitor >= m.median_earnings_per_visitor THEN 'Many visitors, high earnings per visitor'
           WHEN b.travelers_2023 >= m.median_travelers                     THEN 'Many visitors, low earnings per visitor'
           WHEN b.earnings_per_visitor >= m.median_earnings_per_visitor    THEN 'Few visitors, high earnings per visitor'
           ELSE 'Few visitors, low earnings per visitor'
         END AS quadrant
  FROM base b
  CROSS JOIN medians m
),
labelled AS (
  SELECT *,
         CASE quadrant
           WHEN 'Many visitors, high earnings per visitor' THEN 'Established'
           WHEN 'Many visitors, low earnings per visitor'  THEN 'Busy but low-output'
           WHEN 'Few visitors, high earnings per visitor'  THEN 'Small but high-output'
           WHEN 'Few visitors, low earnings per visitor'   THEN 'Limited activity'
           ELSE 'Insufficient data'
         END AS group_label,
         CASE
           WHEN quadrant = 'Insufficient data' THEN 'Not enough data to place in a group'
           WHEN quadrant = 'Many visitors, high earnings per visitor' THEN 'Many visitors, and high output per visitor'
           WHEN quadrant = 'Many visitors, low earnings per visitor'  THEN 'Many visitors, but low output per visitor'
           WHEN quadrant = 'Few visitors, high earnings per visitor'  THEN 'Few visitors, but high output per visitor'
           ELSE 'Few visitors, and low output per visitor'
         END AS what_the_data_shows,
         CASE
           WHEN quadrant = 'Insufficient data' THEN NULL
           WHEN is_leading_destination THEN 'Do its visitors also reach nearby provinces?'
           WHEN quadrant = 'Many visitors, high earnings per visitor' THEN 'Do the benefits reach nearby provinces?'
           WHEN quadrant = 'Many visitors, low earnings per visitor'  THEN 'Where does visitor spending go?'
           WHEN quadrant = 'Few visitors, high earnings per visitor'  THEN 'What keeps visitor numbers low?'
           ELSE 'How does tourism compare with other sectors here?'
         END AS what_to_look_at,
         quadrant IN ('Many visitors, high earnings per visitor', 'Few visitors, high earnings per visitor') AS is_high_output
  FROM classified
)
SELECT l.*, e.unit_type, e.latitude, e.longitude,
       l.province_name AS place,
       CASE WHEN l.is_leading_destination THEN 'Leading destinations' ELSE 'Beyond the leading destinations' END AS destination_group,
       CASE WHEN l.is_leading_destination THEN 'Leading destination' ELSE l.group_label END AS map_group,
       CASE WHEN l.is_lagging THEN 'Lagging (below-median GDP per capita)' ELSE 'Not lagging' END AS wealth_group,
       ROUND(l.gdp_per_capita_current_2023 / 1000, 1) AS gdp_per_capita_thousand
FROM labelled l
JOIN tourism_economy e USING (province_psgc)
) p
WHERE NOT is_leading_destination AND group_label <> 'Insufficient data'
ORDER BY CASE group_label WHEN 'Busy but low-output' THEN 1 WHEN 'Small but high-output' THEN 2
                          WHEN 'Limited activity' THEN 3 ELSE 4 END,
         is_lagging DESC, travelers_2023 DESC
