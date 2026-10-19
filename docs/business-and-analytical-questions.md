# ProvInsights Business and Analytical Questions

This document states what ProvInsights answers, how each term is defined, and which Analytics tables answer each question. Every dashboard page and notebook follows these definitions.

## Contents

- [Business question](#business-question)
- [Scope](#scope)
- [Definitions](#definitions)
- [Question overview](#question-overview)
- [AQ1: Where do visitors go?](#aq1)
- [AQ2: Which provinces earn more from each visitor, and which earn less?](#aq2)
- [AQ3: Does tourism only do well in already-wealthy provinces?](#aq3)
- [AQ4: Which provinces beyond the leading destinations should be prioritized, and what do they need?](#aq4)
- [Recommendation framework](#recommendation-framework)
- [Queries](#queries)
- [Dashboard pages](#dashboard-pages)
- [Wording rules](#wording-rules)
- [Out of scope](#out-of-scope)
- [Notes and caveats](#notes-and-caveats)

---

## Business question

> **How can tourism development be planned to benefit provinces beyond the leading tourist destinations?**

We framed the question as a decision, so our answer is a set of recommendations: which provinces to prioritize and what kind of support fits each one.

- **"Tourism development"** is broader than investment. It covers access, promotion, links to local suppliers, and the option of focusing on other industries first.
- **"Benefit"** covers both ways a province can gain from tourism: more visitors, or more earnings from each visitor.

Our four analytical questions build the answer in order. AQ1 shows that tourism is concentrated. AQ2 sorts provinces by what they need. AQ3 checks whether tourism is a realistic path outside the stronger economies. AQ4 turns these into named priorities.

---

## Scope

| Item | Value |
| --- | --- |
| Trend years | 2019–2023 |
| Analysis year for AQ2 to AQ4 | 2023, the latest year with both DOT and PSA provincial data |
| Units | 100 reporting units: provinces, HUCs that DOT reports separately, the City of Isabela, and NCR (DL-010). In this document, "province" means a reporting unit. |
| Pre- versus post-pandemic comparison | Not used. 2019–2023 is shown as a plain trend, and 2020–2021 are labeled as COVID-19 years. |

---

## Definitions

| Term | Definition | How it is computed |
| --- | --- | --- |
| **Overnight travelers** | Reported overnight travelers in accommodation establishments (DOT). Not unique visitors, and not day-trippers. | `total_travelers` |
| **Tourism intensity** | Overnight travelers relative to population | Overnight travelers ÷ population × 1,000 (`tourism_intensity_per_1000`) |
| **Leading tourist destinations** | The 10 provinces with the highest **average annual** overnight travelers, 2019–2023 | Average of `total_travelers` over the eligible years 2019–2023, ranked descending; rank ≤ 10. Averaging over the years a province has data means a missing year doesn't lower its rank. A tie at 10th adds an 11th province. |
| **Provinces beyond the leading destinations** | Every province that is not a leading destination | — |
| **Tourism-related output** | Accommodation and food services (A&F) gross value added, current prices. Our proxy for tourism's economic output (DL-007). | `afs_gva_current_2023` |
| **Earnings per visitor** | Tourism-related output generated per overnight traveler, in PhP | A&F GVA (thousand PhP) × 1,000 ÷ overnight travelers, 2023 |
| **Tourism share of the economy** | How much of a province's economy is tourism-related activity | Current-price A&F GVA ÷ current-price GDP × 100, 2023 (`afs_share_of_gdp_pct`) |
| **GDP per capita** | Provincial GDP per person, current prices | `gdp_per_capita_current_2023` |
| **Lagging provinces** | Provinces with below-median GDP per capita | 2023 GDP per capita below the median of all provinces with data |
| **Extending economic benefits** | Increasing tourism-related output in provinces beyond the leading destinations | Through more visitors, more earnings per visitor, or both |

**Proxy note.** We use accommodation and food services as the proxy for tourism's economic output because PSA's tourism value added is only published nationally. Our results describe tourism-related patterns, not exact tourist spending. A&F does not capture jobs, other tourist spending (transport, tours, souvenirs), or where the income goes. Residents also eat out and stay in hotels, so A&F overstates tourism somewhat.

---

## Question overview

| Analytical question | What it shows | Analytics tables |
| --- | --- | --- |
| **AQ1** Where do visitors go? | Tourism is concentrated in the leading destinations | `tourism_activity`, `tourism_concentration` |
| **AQ2** Which provinces earn more from each visitor, and which earn less? | Which provinces need more visitors, and which need visitors to spend more | `tourism_economy`, `tourism_activity` |
| **AQ3** Does tourism only do well in already-wealthy provinces? | Whether tourism is a realistic path outside the stronger economies | `tourism_economy` |
| **AQ4** Which provinces beyond the leading destinations should be prioritized, and what do they need? | The answer to the business question | `tourism_economy`, `tourism_activity` |

All tables are in `tuklas_dev.05_analytics` and are built by `notebooks/05_analytics/01_build_analytics.ipynb`. Leading destinations, earnings per visitor, quadrants and recommended actions are derived from these tables by the queries in [Queries](#queries).

---

<a id="aq1"></a>

## AQ1: Where do visitors go?

**Which provinces receive the most overnight travelers, and how concentrated is tourism in the leading destinations?**

**Why it matters.** It shows that tourism's benefits are concentrated, which is why the business question needs asking. It also identifies the leading destinations used in AQ2 to AQ4.

| Measure | Source |
| --- | --- |
| Overnight travelers per province and year | `tourism_activity.total_travelers` |
| Tourism intensity | `tourism_activity.tourism_intensity_per_1000` |
| Share of all travelers and rank, per year | `tourism_activity.tourism_share_pct`, `tourism_rank`, `intensity_rank` |
| Top-5 and top-10 share in each year | `tourism_concentration.top_5_share_pct`, `top_10_share_pct` |
| Leading destinations | [Query 1](#query-1-leading-destinations) on `tourism_activity` |
| Share of travelers going to the leading destinations, per year | [Query 2](#query-2-share-going-to-the-leading-destinations) on `tourism_activity` |

Only rows with `activity_eligible = true` are counted. Rows not reported by DOT are excluded, never treated as zero.

**Answer template.** "The 10 leading destinations received X% of all overnight travelers in 2023. [Province] and [Province] lead in volume, while [Province] stands out relative to its population."

---

<a id="aq2"></a>

## AQ2: Which provinces earn more from each visitor, and which earn less?

**How do provinces beyond the leading destinations compare in tourism-related earnings per visitor?**

**Why it matters.** It separates provinces that need more visitors from those that need visitors to spend more. This is what makes different recommendations possible.

| Measure | Source |
| --- | --- |
| Overnight travelers, 2023 | `tourism_economy.travelers_2023` |
| A&F GVA, current prices, 2023 | `tourism_economy.afs_gva_current_2023` |
| Earnings per visitor | [Query 3](#query-3-province-profile-2023) |
| Medians and quadrant | [Query 3](#query-3-province-profile-2023) |

Each province is placed against the 2023 medians of overnight travelers and earnings per visitor:

| Quadrant | Overnight travelers | Earnings per visitor |
| --- | --- | --- |
| **Many visitors, high earnings per visitor** | At or above median | At or above median |
| **Many visitors, low earnings per visitor** | At or above median | Below median |
| **Few visitors, high earnings per visitor** | Below median | At or above median |
| **Few visitors, low earnings per visitor** | Below median | Below median |

- **Eligible provinces:** reported by DOT in 2023, more than zero travelers, and a 2023 A&F value. The others are shown as "Insufficient data" and get no quadrant.
- **Small base:** earnings per visitor divides by travelers, so a province with few travelers can look high only because its denominator is small. Provinces with fewer than 10,000 travelers in 2023 are flagged `small_base_2023`, the same level as our small-base rule (DL-028), and their figures are read together with the traveler count.

**Answer template.** "[Province] and [Province] receive many travelers but generate little tourism-related output per traveler. [Province] generates high output per traveler despite few travelers."

---

<a id="aq3"></a>

## AQ3: Does tourism only do well in already-wealthy provinces?

**How does the tourism share of each province's economy compare with its GDP per capita?**

**Why it matters.** It checks whether tourism is a realistic path outside the stronger economies, or whether other industries should come first.

| Measure | Source |
| --- | --- |
| Tourism share of the economy, 2023 | `tourism_economy.afs_share_of_gdp_pct` |
| GDP per capita, 2023 | `tourism_economy.gdp_per_capita_current_2023` |
| Lagging flag | [Query 3](#query-3-province-profile-2023) |

**How to read it.** An upward pattern means tourism-related activity tends to be larger where incomes are higher. No clear pattern means it is not limited to wealthier provinces. Lagging provinces with a high tourism share are candidates for priority.

**Answer template.** "Tourism's share of the economy [rises with / shows no clear relationship with] GDP per capita. [Province] and [Province], both below the median in GDP per capita, rely heavily on tourism-related activity."

---

<a id="aq4"></a>

## AQ4: Which provinces beyond the leading destinations should be prioritized, and what do they need?

**Why it matters.** This is the answer to the business question.

[Query 3](#query-3-province-profile-2023) gives one row per province with its leading-destination flag, lagging flag, quadrant, tourism share and recommended action. The priority list is every province beyond the leading destinations that has a quadrant. It is sorted with lagging provinces first, then by tourism share of the economy, highest first.

**Answer template.** "Priority provinces are [Province] (bring in more visitors), [Province] (help visitors spend more locally), and [Province] (focus on other industries first)."

---

## Recommendation framework

Each province gets an action from its group. Province names come from the results.

| Group | Action | Specific steps | Agencies |
| --- | --- | --- | --- |
| Few visitors, high earnings per visitor | **Bring in more visitors** | Improve road, port and airport links; feature in promotions; link to nearby leading destinations through circuits. First check that the output isn't mostly local demand. | DPWH, DOTr, TIEZA, DOT |
| Many visitors, low earnings per visitor | **Help visitors spend more locally** | Multi-day packages and overnight experiences; connect local farmers and MSMEs to hotels and restaurants; accreditation and financing for local accommodation | DOT, LGUs, DTI, DA |
| Few visitors, low earnings per visitor | **Focus on other industries first** | Prioritize other sectors or basic infrastructure; revisit tourism later | LGUs, NEDA/DEPDev |
| Many visitors, high earnings per visitor | **Sustain and connect** | Maintain current performance; link to neighboring provinces through circuits | DOT, LGUs |
| Leading destinations | **Spread visitors outward** | Regional circuits and joint packages that route visitors to nearby provinces; manage crowding and sustainability | DOT, LGUs |

Overall recommendations:

- **Prioritization:** among provinces beyond the leading destinations, give extra priority to lagging provinces.
- **Promotion balance:** where AQ1 shows high concentration, national promotion should give more space to provinces beyond the leading destinations.
- **Better data:** PSA and DOT should publish provincial tourism economic data, so planning doesn't depend on a proxy.

These are priorities for planning and further study. They are not predictions of outcomes.

---

## Queries

The dashboard datasets use these queries on the Analytics tables.

### Query 1: Leading destinations

```sql
SELECT province_psgc,
       province_name,
       AVG(total_travelers)                                    AS avg_travelers_2019_2023,
       RANK() OVER (ORDER BY AVG(total_travelers) DESC)        AS avg_travelers_rank,
       RANK() OVER (ORDER BY AVG(total_travelers) DESC) <= 10  AS is_leading_destination
FROM tuklas_dev.`05_analytics`.tourism_activity
WHERE year BETWEEN 2019 AND 2023
  AND activity_eligible
GROUP BY province_psgc, province_name;
```

### Query 2: Share going to the leading destinations

```sql
WITH province_avg AS (
  SELECT province_psgc, AVG(total_travelers) AS avg_travelers
  FROM tuklas_dev.`05_analytics`.tourism_activity
  WHERE year BETWEEN 2019 AND 2023 AND activity_eligible
  GROUP BY province_psgc
),
leading AS (
  SELECT province_psgc
  FROM province_avg
  QUALIFY RANK() OVER (ORDER BY avg_travelers DESC) <= 10
)
SELECT a.year,
       SUM(CASE WHEN l.province_psgc IS NOT NULL THEN a.total_travelers ELSE 0 END) * 100.0
         / SUM(a.total_travelers) AS leading_destination_share_pct
FROM tuklas_dev.`05_analytics`.tourism_activity a
LEFT JOIN leading l ON a.province_psgc = l.province_psgc
WHERE a.year BETWEEN 2019 AND 2023 AND a.activity_eligible
GROUP BY a.year
ORDER BY a.year;;
```

### Query 3: Province profile, 2023

```sql
WITH leading AS (
  SELECT province_psgc,
         RANK() OVER (ORDER BY AVG(total_travelers) DESC) <= 10 AS is_leading_destination
  FROM tuklas_dev.`05_analytics`.tourism_activity
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
  FROM tuklas_dev.`05_analytics`.tourism_economy e
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
)
SELECT *,
       CASE
         WHEN is_leading_destination                                   THEN 'Spread visitors outward'
         WHEN quadrant = 'Few visitors, high earnings per visitor'     THEN 'Bring in more visitors'
         WHEN quadrant = 'Many visitors, low earnings per visitor'     THEN 'Help visitors spend more locally'
         WHEN quadrant = 'Few visitors, low earnings per visitor'      THEN 'Focus on other industries first'
         WHEN quadrant = 'Many visitors, high earnings per visitor'    THEN 'Sustain and connect'
         ELSE 'Insufficient data'
       END AS recommended_action
FROM classified
ORDER BY is_leading_destination, is_lagging DESC, afs_share_of_gdp_pct DESC NULLS LAST;
```

Medians are taken across all provinces with data, including the leading destinations, so each province is compared with the whole country.

---

## Dashboard pages

| Page | Answers | Main visuals |
| --- | --- | --- |
| 1. Where visitors go | AQ1 | KPI tiles (total travelers, share going to the leading destinations), map of travelers per 1,000 residents, top and bottom provinces, 2019–2023 trend |
| 2. Earnings per visitor | AQ2 | Quadrant scatter of overnight travelers (log scale) against earnings per visitor, with median lines and the leading destinations marked; sorted bar of earnings per visitor |
| 3. Tourism and wealth | AQ3 | GDP per capita against tourism share of the economy, with lagging provinces highlighted |
| 4. Priority provinces | AQ4 | Recommendation table: province, GDP per capita, lagging flag, quadrant, tourism share, recommended action; KPI tiles by action |

Every page carries the proxy note as a footer.

---

## Wording rules

We say "tourism-related activity", not "tourism", and we describe patterns, not causes.

| Question | Possible phrasing | Intended meaning |
| --- | --- | --- |
| AQ1 | "These provinces get the most tourists." | "These provinces recorded the most overnight travelers." |
| AQ2 | "Tourists spend ₱X per visit." / "Money is leaking out." | "Province Y generates ₱X in accommodation and food services output per overnight traveler, which may indicate low local spending." |
| AQ3 | "Tourism causes growth." / "Tourism is X% of the economy." | "Accommodation and food services make up X% of Province Y's GDP." / "Provinces with higher GDP per capita tend to…" |
| AQ4 | "Developing tourism in Province X will aid in its economy." | "Province X's tourism profile suggests [action] can potentially help, to be validated with local data." |

Also:

- For a general audience, "tourism-related output (accommodation and food services)" is written at first mention instead of "A&F".
- GDP per capita is not a measure of wealth/poverty. We say "lagging" or "lower-income".
- We say "earnings per visitor" and "visitors spend more locally", not "value capture" or "leakage".

---

## Out of scope

- Causal claims about the effect of tourism on local economies (DL-008).
- Predicted returns, GDP gains or other guaranteed outcomes from any recommended action (DL-008).
- Comparing pre- and post-pandemic levels.
- Treating A&F GVA as tourism revenue or tourist spending (DL-007).

---

## Notes and caveats

- Overnight travelers are DOT-reported counts in accommodation establishments. They can differ from local government arrival counts, which often include same-day visitors.
- Missing values stay NULL and are never treated as zero (DL-009). Provinces DOT doesn't report (BARMM provinces and Sulu) have no traveler measures, rank or quadrant.
- Provinces with `reported_partial` traveler data (NCR in every year, Sorsogon 2019) are included, with the status shown as a caveat (DL-019).
- DOT's coverage of some provinces changes between years, for example Boracay in Aklan (DL-013) and Clark in Pampanga (DL-014). This affects their trend and their 2019–2023 average.
- Region II foreign travelers include overseas Filipinos (DL-030). This doesn't affect total travelers.
- Tourism share of the economy and earnings per visitor both use current prices from the same year.
- Medians, quadrants and the lagging flag describe the provinces with data in 2023. They are relative positions, not national benchmarks.
- Our results support planning priorities and further study, not investment decisions.
- `tourism_recovery` and `traveler_segment_recovery` are also built in the Analytics layer. They describe recovery against 2019 and are kept as supporting tables, but they are not used to answer the business question.
