-- dataset: ds_aq1_year
-- display: AQ1: totals and share going to the leading destinations, by year (Query 2)
-- source: tuklas_dev.05_analytics (tourism_activity)
-- used by: Page 1: totals, provinces reported, share to the leading destinations (Query 2), yearly trend
SELECT
  t.year,
  t.total_travelers,
  t.places_reporting,
  q.leading_destination_share_pct
FROM
  (
    SELECT
      year,
      SUM(total_travelers) AS total_travelers,
      COUNT(*) AS places_reporting
    FROM
      tourism_activity
    WHERE
      year BETWEEN 2019 AND 2023
      AND activity_eligible
    GROUP BY
      year
  ) t
    JOIN (
      WITH province_avg AS (
        SELECT
          province_psgc,
          AVG(total_travelers) AS avg_travelers
        FROM
          tourism_activity
        WHERE
          year BETWEEN 2019 AND 2023
          AND activity_eligible
        GROUP BY
          province_psgc
      ),
      leading AS (
        SELECT
          province_psgc
        FROM
          province_avg
        QUALIFY
          RANK() OVER (ORDER BY avg_travelers DESC) <= 10
      )
      SELECT
        a.year,
        SUM(
          CASE
            WHEN l.province_psgc IS NOT NULL THEN a.total_travelers
            ELSE 0
          END
        )
          * 100.0
          / SUM(a.total_travelers) AS leading_destination_share_pct
      FROM
        tourism_activity a
          LEFT JOIN leading l
            ON a.province_psgc = l.province_psgc
      WHERE
        a.year BETWEEN 2019 AND 2023
        AND a.activity_eligible
      GROUP BY
        a.year
    ) q
      USING (year)
