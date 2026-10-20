-- dataset: ds_aq3_corr
-- display: AQ3: correlation, 2023
-- source: tuklas_dev.05_analytics (tourism_activity, tourism_economy)
-- used by: Page 3: correlation of GDP per capita and tourism share (same Query 3 logic)
SELECT CORR(gdp_per_capita_current_2023, afs_share_of_gdp_pct) AS correlation, COUNT(*) AS provinces
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
         median(gdp_per_capita_current_2023)                                        AS median_gdp_per_capita,
         median(afs_share_of_gdp_pct)                                               AS median_tourism_share
  FROM base
),
classified AS (
  SELECT b.*,
         b.gdp_per_capita_current_2023 < m.median_gdp_per_capita AS is_lagging,
         b.afs_share_of_gdp_pct > m.median_tourism_share          AS is_tourism_dependent,
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
           WHEN 'Many visitors, high earnings per visitor' THEN 'Tourism Leaders'
           WHEN 'Many visitors, low earnings per visitor'  THEN 'Visitor Magnets'
           WHEN 'Few visitors, high earnings per visitor'  THEN 'High-Value Niches'
           WHEN 'Few visitors, low earnings per visitor'   THEN 'Emerging Tourism Areas'
           ELSE 'Insufficient data'
         END AS group_label,
         CASE
           WHEN quadrant = 'Insufficient data' THEN 'Not enough data to place in a group'
           WHEN quadrant = 'Many visitors, high earnings per visitor' THEN 'Many visitors, and each brings in a lot'
           WHEN quadrant = 'Many visitors, low earnings per visitor'  THEN 'Many visitors come, but each brings in little'
           WHEN quadrant = 'Few visitors, high earnings per visitor'  THEN 'Each visitor brings in a lot, but visitors are few'
           WHEN is_tourism_dependent THEN 'Few visitors, but tourism is already a big part of the economy'
           ELSE 'Few visitors, and tourism is still a small part of the economy'
         END AS what_stands_out,
         CASE
           WHEN quadrant = 'Insufficient data' THEN NULL
           WHEN is_leading_destination THEN 'Do its visitors also reach nearby provinces?'
           WHEN quadrant = 'Many visitors, high earnings per visitor' THEN 'Do the benefits reach nearby provinces?'
           WHEN quadrant = 'Many visitors, low earnings per visitor'  THEN 'Where does visitor spending go?'
           WHEN quadrant = 'Few visitors, high earnings per visitor'  THEN 'What keeps visitor numbers low?'
           WHEN is_tourism_dependent THEN 'Tourism already matters here: what holds visitors back?'
           ELSE 'How does tourism compare with other sectors here?'
         END AS what_to_look_at
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
WHERE afs_share_of_gdp_pct IS NOT NULL AND gdp_per_capita_current_2023 IS NOT NULL
