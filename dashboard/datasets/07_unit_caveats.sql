-- ds_caveats: one row per reporting unit and year that needs a caveat.
-- Source: 05_analytics.tourism_activity (status and comparability already set in Silver/Gold).
-- Used by: Province Explorer caveat table; Tourism Overview "units not included" table.
SELECT
  province_name                         AS reporting_unit,
  unit_type,
  region_name,
  year,
  CASE
    WHEN traveler_value_status = 'not_reported' THEN 'DOT did not report travelers for this unit and year; shown as blank, not 0.'
    WHEN comparable_to_2019 IS NOT TRUE        THEN 'DOT changed how this unit is counted after 2019, so it is not compared with 2019.'
    WHEN traveler_value_status = 'reported_partial' THEN 'Only part of the unit was reported.'
  END                                   AS caveat,
  comparability_note                    -- source wording, for reviewers
FROM tuklas_dev.`05_analytics`.tourism_activity
-- dash_as_zero is not listed per unit: it applies to most units and is explained once in the definitions text.
WHERE traveler_value_status IN ('not_reported', 'reported_partial') OR comparable_to_2019 IS NOT TRUE
