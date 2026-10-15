# ProvInsights Business and Analytical Questions (Revised)

## Table of Contents

- [Client Context](#client-context)
- [Main Business Question](#main-business-question)
- [Question Overview](#question-overview)
- [Shared Definitions](#shared-definitions)
- [BQ1](#bq1)
  - [AQ1.1](#aq11)
  - [AQ1.2](#aq12)
  - [AQ1.3](#aq13)
- [BQ2](#bq2)
  - [AQ2.1](#aq21)
  - [AQ2.2](#aq22)
  - [AQ2.3](#aq23)
  - [AQ2.4](#aq24)
- [Out of Scope](#out-of-scope)
- [Comparison Thresholds](#comparison-thresholds)
- [Confirmed Results](#confirmed-results)
- [Notes and Caveats](#notes-and-caveats)
- [Change Log](#change-log)

---

<a id="client-context"></a>

## Client Context

**Fictional client persona:** Tourism-Economy Convergence Task Force (TECTF).

TECTF is a fictional inter-agency body bringing together the Department of Tourism, the Department of Trade and Industry, and PSA, with technical support from the Asian Development Bank.

TECTF wants to test whether tourism growth reaches beyond the usual top destinations, or whether it is only growing where the economy already is.

ProvInsights answers this by describing patterns in reported overnight tourism and in local tourism-related economic activity. It supports closer investigation. It does not show that tourism causes economic growth, and it does not prescribe interventions or investments.

The two halves of TECTF's question map to the analysis as follows:

| TECTF question | Where it is answered |
| --- | --- |
| Is tourism growth reaching **beyond the usual top destinations**? | AQ1.1 (concentration), AQ1.2 (recovery), AQ1.3 (traveler types), and the usual-destination split in AQ1.2 and AQ2.2 |
| Is it **only growing where the economy already is**? | AQ2.1 to AQ2.3 (tourism and A&F co-movement) and AQ2.4 (tourism versus the 2019 economic base) |

---

## Main Business Question

> **Which Philippine provinces warrant closer attention based on their tourism activity and recovery, how these relate to local economic performance, and whether tourism growth is appearing beyond the usual strong destinations?**

ProvInsights is designed as a **decision-support tool** through which tourism and economic indicators are used to surface provinces and patterns that warrant closer investigation.

---

## Question Overview

| Business Question | Analytical Question | Analytical Table |
| --- | --- | --- |
| **BQ1: Tourism Activity and Recovery** | **AQ1.1:** Activity, intensity, and concentration | `tourism_activity`, `tourism_concentration` |
|  | **AQ1.2:** Recovery relative to 2019 | `tourism_recovery` |
|  | **AQ1.3:** Recovery by traveler type among provinces below 2019 | `traveler_segment_recovery` |
| **BQ2: Tourism and Economic Conditions** | **AQ2.1:** Tourism change and real A&F growth | `tourism_economy` |
|  | **AQ2.2:** Alignment and divergence | `tourism_economy` |
|  | **AQ2.3:** Economic significance of A&F | `tourism_economy` |
|  | **AQ2.4:** Tourism outcomes versus the 2019 economic base | `tourism_economy` |

---

## Shared Definitions

| Term | Definition |
| --- | --- |
| **Province** | Used as the main client-facing term. Selected separately reported HUCs, City of Isabela, and NCR are also included in the analytical model where required by source reporting. The model covers 100 reporting units (DL-010). |
| **Baseline year** | 2019 (DL-004) |
| **Recovery years** | 2022 and 2023, each compared separately with 2019 |
| **Tourism activity** | Reported overnight travelers in accommodation establishments |
| **Tourism intensity** | Reported overnight travelers per 1,000 residents |
| **Traveler categories** | Domestic, foreign, and overseas Filipino |
| **Economic proxy** | Accommodation and Food Services (A&F) GVA (DL-007) |
| **Real A&F growth** | Change in constant-price A&F GVA from 2019 to 2023 |
| **Economic significance** | Current-price A&F GVA as a share of current-price GDP (2023). A measure of how large the A&F sector is locally, not of overall economic strength. |
| **Usual strong destinations** *(proposed, DL-025)* | The 10 reporting units with the most reported overnight travelers in **2019**, fixed as a pre-pandemic reference. All other provinces are described as "other places". Stored in Analytics as the flag `usual_strong_destination_2019`, which matches the 2019 `tourism_rank` of 10 or better (checked in the build and validation notebooks). |
| **Baseline economic strength** *(proposed, DL-026)* | GDP per capita in 2019, current prices (stored `gdp_per_capita_current_2019`). A 2019 value, so it does not reflect the 2019 to 2023 tourism change it is compared with. |
| **Baseline under review** *(proposed, DL-028)* | A unit whose 2020 traveler count is higher than its 2019 count. 2020 was a pandemic year, so a higher count suggests an undercounted 2019 base. The stored values are not changed. |

---

<a id="bq1"></a>

## BQ1: Which provinces stand out in tourism activity and recovery, and which appear to be lagging?

The tourism landscape is described through activity, intensity, concentration, recovery relative to 2019, and traveler-segment recovery among provinces that remain below their 2019 level.

For TECTF, BQ1 also shows whether recovery and activity are limited to the usual strong destinations or also appear in other places.

<a id="aq11"></a>

### AQ1.1: Which provinces have the highest and lowest tourism activity and tourism intensity, and how concentrated is it across provinces?

**2023 is used as the headline year.**

```text
Tourism activity =
reported overnight travelers

Tourism intensity =
reported overnight travelers / population × 1,000

Tourism share (%) =
province travelers / total eligible travelers × 100

Top-N concentration (%) =
travelers in top N provinces / total eligible travelers × 100
```

The following are reported:

- activity ranking;
- intensity ranking;
- Top 5 concentration; and
- Top 10 concentration.

**Analytical tables:**  
`tourism_activity`, `tourism_concentration`

---

<a id="aq12"></a>

### AQ1.2: Which provinces have returned to or surpassed their pre-pandemic tourism levels, and which remain below them?

Recovery is calculated separately for:

- 2022 vs. 2019; and
- 2023 vs. 2019.

```text
Recovery Index =
comparison-year travelers / 2019 travelers × 100
```

| Recovery Index | Classification |
| --- | --- |
| > 100 | Above 2019 |
| = 100 | Unchanged |
| < 100 | Below 2019 |

Results are also shown separately for the usual strong destinations (top 10 in 2019) and for other places, so that it is visible whether recovery above 2019 is happening beyond the usual strong destinations. This split is a display grouping based on stored values. It does not change the recovery calculation.

Provinces that meet the possible emerging destination rule set out under Comparison Thresholds are labelled as such. Provinces above 400, or with a baseline under review, are shown as "Under review". All other provinces above 2019 are shown as above 2019 only.

**Analytical table:**  
`tourism_recovery`

---

<a id="aq13"></a>

### AQ1.3: Among provinces that remained below their 2019 level, how do recovery patterns differ between domestic, foreign, and overseas Filipino travelers?

The analysis is restricted to provinces with:

- a valid and comparable 2019 baseline; and
- overall 2023 tourism activity below the 2019 level.

Recovery is then calculated separately for:

- domestic travelers;
- foreign travelers; and
- overseas Filipino travelers.

```text
Segment Recovery Index =
comparison-year segment travelers / 2019 segment travelers × 100
```

Coverage is reported alongside every segment result (for example, the number of provinces for which a valid segment figure exists out of all provinces in scope). A missing segment figure reflects a missing or non-comparable baseline. It does not mean there was no tourism in that segment.

**Analytical table:**  
`traveler_segment_recovery`

---

<a id="bq2"></a>

## BQ2: How are changes in tourism activity associated with changes in local tourism-related economic activity across provinces?

Changes in tourism activity are compared with changes in A&F GVA so that provinces where tourism and local tourism-related economic activity align or diverge can be identified.

For TECTF, BQ2 tests whether tourism growth is linked to the local economy in a consistent way, and whether that link looks different in the usual strong destinations and in other places. Findings are co-movement only.

<a id="aq21"></a>

### AQ2.1: How does the change in reported tourism activity from 2019 to 2023 compare with growth in A&F GVA across provinces?

```text
Tourism change (%) =
(2023 travelers - 2019 travelers) / 2019 travelers × 100

Real A&F GVA growth (%) =
(2023 constant-price A&F GVA - 2019 constant-price A&F GVA)
 / 2019 constant-price A&F GVA × 100
```

Tourism change equals the Recovery Index minus 100 (DL-022).

The number of provinces compared is reported. A correlation is shown only if Analytics stores it, because computing it in the dashboard would be a new calculation.

Tourism change is unstable where the 2019 base is small or unreliable. For example, Davao Occidental moved from 188 to 32,375 reported overnight travelers (+17,121%), and Camarines Sur's 2019 count is under review (DL-028). Such values are shown separately and are not read as evidence of a strong destination.

**Analytical table:**  
`tourism_economy`

---

<a id="aq22"></a>

### AQ2.2: Which provinces show tourism activity and A&F GVA moving in the same direction, and which show divergent patterns?

The following classifications are used:

| Classification | Interpretation |
| --- | --- |
| `tourism_up_economy_up` | Tourism activity increased; real A&F GVA increased |
| `tourism_up_economy_down` | Tourism activity increased; real A&F GVA decreased |
| `tourism_down_economy_up` | Tourism activity decreased; real A&F GVA increased |
| `tourism_down_economy_down` | Tourism activity decreased; real A&F GVA decreased |

Unchanged cases are kept separate from the four main quadrants.

Patterns are also shown separately for the usual strong destinations (top 10 in 2019) and for other places.

**Analytical table:**  
`tourism_economy`

---

<a id="aq23"></a>

### AQ2.3: How does the economic significance of A&F Services differ among provinces with different tourism recovery patterns?

**2023 is used as the headline year.**

Economic significance is calculated as:

```text
A&F share of GDP (%) =
current-price A&F GVA / current-price GDP × 100
```

**Analytical table:**  
`tourism_economy`

---

<a id="aq24"></a>

### AQ2.4: Is tourism activity and recovery stronger in provinces whose local economy was already stronger in 2019?

This addresses the second half of TECTF's question: whether tourism is only growing where the economic base was already strong.

The following stored values are compared across provinces:

- 2019 GDP per capita, current prices (`gdp_per_capita_current_2019`), as the baseline economic strength indicator;
- 2023 tourism intensity (`tourism_intensity_per_1000_2023`); and
- tourism change from 2019 to 2023 (`tourism_change_pct`).

Stored values are displayed side by side, grouped by usual strong destinations and other places. No new formulas are introduced.

A&F share of GDP is not used as a baseline. It is a 2023 value and describes the size of one sector, so it partly reflects the tourism growth being compared with it. A sector-size baseline would require a 2019 A&F share in Analytics.

**Analytical table:**  
`tourism_economy`

---

## Out of Scope

- Causal claims about the effect of tourism on local economies (DL-008).
- ROI, "best place to invest", or promotion-focus rankings (DL-008).
- Treating A&F GVA as a measure of tourism output or revenue (DL-007).
- Treating national tourism satellite account (PTSA) values as provincial values (DL-007).

---

## Comparison Thresholds

These thresholds are display rules. They decide which label a province is shown with. They do not change any stored calculation, and a label is a prompt for closer investigation, not a finding. They are recorded in decisions DL-027 and DL-028 as working defaults, refining DL-006.

**Small base**

A figure is described as resting on a small base when the 2019 count behind it is small, because percentage changes on small counts are unstable.

| Measure | Small base when |
| --- | --- |
| Overall recovery index and tourism change | 2019 overnight travelers are below 10,000 |
| Segment recovery index (domestic, foreign, overseas Filipino) | 2019 segment travelers are below 1,000 |

Small-base values are shown with their underlying traveler counts. A small base does not mean the value is wrong, and it is not a reason to remove a province.

**Under review**

A province is shown as "Under review", with no label, when either of the following holds:

- its 2023 recovery index is above 400, because a multiple that large more often reflects a data problem than emergence; or
- its 2019 baseline is under review, meaning its 2020 traveler count is higher than its 2019 count (DL-028).

The stored values are still displayed, and the province is still counted in the recovery classes.

**Possible emerging destination**

A province is described as a possible emerging destination when all of the following hold:

1. It is not a usual strong destination (not in the top 10 for 2019).
2. Its recovery class is above 2019 in both 2022 and 2023.
3. Its 2019 overnight travelers are at least 10,000.
4. Its 2023 recovery index is at least 120 and at most 400.
5. Its 2023 traveler count is at least 25,000 above its 2019 count.
6. It is comparable to 2019 and its traveler value is neither partial nor missing in both years.
7. Its 2019 baseline is not under review.

The label describes a pattern in reported overnight travelers in accommodation establishments. It does not say the province has reached any level of tourism, that its growth will continue, or that it merits investment. Provinces that are above 2019 but do not meet every condition are shown as above 2019 without the label.

Analytics now stores these flags and labels (`usual_strong_destination_2019`, `baseline_under_review_2019`, the small-base flags and `destination_label`), and the dashboard uses the stored values without applying any other calculation. The thresholds are set in the build notebook: usual top N = 10, small base 10,000 overall and 1,000 per segment, possible emerging base at least 10,000, index 120 to 400, and increase of at least 25,000.

---

<a id="confirmed-results"></a>

## Confirmed Results

These results come from the persisted Analytics tables after the full run of `01_build_analytics` (36 checks) and `02_analytics_validation` (all checks passed, no failures) on 2026-10-14. Gold inputs were pinned at `dim_province` v83, `dim_year` v55 and `fact_province_year` v72. They are descriptions of reported overnight travelers, not causal findings.

### AQ1.1: Concentration (2023 vs. 2019)

| Measure | 2019 | 2023 |
| --- | --- | --- |
| Top 5 share of included overnight travelers | 24.16% | 31.75% |
| Top 10 share of included overnight travelers | 40.40% | 44.59% |

Each year's top 10 is ranked in that year. The 2019 top 10 used for "usual strong destinations" is fixed (see below).

### Usual strong destinations (10, DL-025)

Aklan, Albay, Batangas, Bohol, City of Cebu, City of Davao, City of Lapu-Lapu, Davao de Oro, National Capital Region (NCR), Rizal.

### AQ1.2: Recovery (2023 vs. 2019)

| Result | Count |
| --- | --- |
| Above 2019 | 39 |
| Below 2019 | 52 |
| Eligible for comparison | 91 |
| Not comparable | 9 |
| Total reporting units | 100 |

Of the 39 above 2019, 3 are usual strong destinations: NCR (index 231.4), Batangas (154.1) and Rizal (113.2). The other 36 are other places.

**Possible emerging destinations (13):** Antique, Aurora, Bukidnon, Bulacan, City of Iligan, City of Zamboanga, Guimaras, Lanao del Norte, Northern Samar, Pampanga, Sarangani, Sultan Kudarat, Surigao del Sur.

**Under review (6):**

| Unit | 2023 recovery index | Reason |
| --- | --- | --- |
| Camarines Sur | 2,884.0 | Baseline under review |
| City of Isabela | 667.8 | Baseline under review |
| Davao del Sur | 275.4 | Baseline under review |
| Davao Occidental | 17,220.7 | Index above 400 |
| Davao Oriental | 419.9 | Index above 400 |
| Romblon | 860.6 | Index above 400 |

Baseline under review flags three units (Camarines Sur, City of Isabela, Davao del Sur). Samar (119.3), Masbate (114.0) and Kalinga (109.9) are below the index of 120 and carry no label.

### Small bases

- Eight units have a 2019 overall base below 10,000.
- Domestic segment: 0 of 52 eligible provinces are on a small base.
- Foreign segment: 7 of 47 eligible provinces are on a small base.
- Overseas Filipino segment: 17 of 26 eligible provinces are on a small base, so most overseas Filipino results need the small-base caveat.

### AQ2.2: Alignment (travelers vs. real A&F GVA, 2019 to 2023)

43 of 91 eligible units moved in opposite directions:

| Pattern | Count |
| --- | --- |
| Travelers up, real A&F GVA down | 13 |
| Travelers down, real A&F GVA up | 30 |

### Example provinces (AQ2.1 and AQ2.3)

| Province | Travelers vs. 2019 | Real A&F GVA vs. 2019 | A&F share of GDP (2023) | Pattern |
| --- | --- | --- | --- | --- |
| Aurora | +168.83% | -25.05% | 1.27% | Travelers up, business down |
| Camiguin | -67.81% (32% of 2019) | -15.35% | 11.80% | Both down |
| Pampanga | +81.83% | +6.50% | 2.65% | Both up |

Aurora is a possible emerging destination by the rule above, and its real A&F GVA fell. This is a prompt to ask what changed (stays, spending, coverage or reporting), not an explanation.

---

## Notes and Caveats

- **Provinces** is used as the main client-facing term, although selected separately reported HUCs, City of Isabela, and NCR are also included in the analytical model.
- Tourism activity is measured using **reported overnight travelers in accommodation establishments**, not unique visitors or all tourists. Figures are DOT-reported and can differ from arrival counts published by local governments, which often include same-day visitors.
- Recovery is defined specifically as **reported overnight tourism activity relative to 2019**.
- A valid 2019 baseline and `comparable_to_2019 = true` are required for recovery (DL-020).
- Missing values are retained as NULL and are not replaced with zero. Missing does not mean zero (DL-009).
- Valid ranks or classifications are not assigned to missing or ineligible values.
- Special handling of individual areas is recorded in the decision log: unit definitions and BARMM coverage (DL-010), Boracay and Aklan (DL-013), Clark and Pampanga (DL-014), SBMA (DL-015), Cotabato City (DL-016), the treatment of `-` values (DL-019), per-year comparability (DL-020) and baselines under review (DL-028).
- **Constant-price A&F GVA** is used for growth.
- **Current-price A&F GVA and GDP** are used for A&F share of GDP.
- A&F GVA is treated as a tourism-related economic proxy, not as a direct measure of tourism revenue. A&F output also includes activity unrelated to tourism.
- Co-movement between tourism and economic indicators is interpreted as **association, not causation**. ProvInsights cannot show that tourism drives local economic growth.
- Tourism change is unstable for small or unreliable 2019 bases and should be read with the underlying traveler counts.
- Counts of provinces above 2019 follow the stored data and include provinces shown as "Under review". Of the 39 above 2019 in 2023, 3 are usual strong destinations (see Confirmed Results).
- Recovery above 2019 does not by itself mean a province is an emerging destination. The "possible emerging destination" label applies only where every condition under Comparison Thresholds is met.
- The usual strong destinations grouping is a display grouping based on 2019 stored values. It is not a judgement about destination quality or potential.
- Figures in Confirmed Results come from the full run of `01_build_analytics` and `02_analytics_validation` on 2026-10-14, with no failed checks. They remain preliminary until the eligibility rules, treatment of partially reported data and the Proposed decisions (DL-025 to DL-028) are accepted.
- Results are intended to support closer investigation; interventions or investment decisions are not prescribed.

---

## Change Log

This log compares the document with `main` (finalized in #30).

| Section | Change |
| --- | --- |
| Structure | The three business questions were consolidated into two. The former BQ1 and BQ2 form the new BQ1, and the former BQ3 forms the new BQ2. |
| Main Business Question | The question was reworded as a decision-support question. Prescriptive wording about where promotion should be focused and what support or intervention should follow was removed. "Emerging beyond" became "appearing beyond". |
| Client Context | Added. It introduces the fictional TECTF client and maps its two-part question to the analytical questions. |
| Question Overview | The supporting-analysis row became AQ2.4, a numbered question. |
| Shared Definitions | Added "Usual strong destinations" (top 10 in 2019, DL-025), "Baseline economic strength" (2019 GDP per capita, current prices, DL-026) and "Baseline under review" (DL-028). Economic significance was clarified as a measure of sector size, not overall economic strength. The 100 reporting units were stated (DL-010). |
| AQ1.2 and AQ2.2 | Results are also shown for usual strong destinations and for other places. This is a display grouping. The calculations are unchanged. AQ1.2 also carries the possible emerging destination label and the "Under review" mark where their conditions are met. |
| AQ1.3 | Added coverage reporting and the statement that a missing segment figure does not mean there was no tourism in that segment. The calculation is unchanged. |
| AQ2.1 | Added the link between tourism change and the Recovery Index (DL-022), the statement that only the number of provinces compared is reported unless Analytics stores a correlation, and a note that tourism change is unstable for small or unreliable 2019 bases (Davao Occidental, Camarines Sur). |
| AQ2.4 | Added as a numbered question comparing tourism intensity and tourism change with 2019 economic strength. A&F share is described as a sector-size measure, not a baseline. |
| Out of Scope | Retained from `main` in shortened form, with decision references. |
| Comparison Thresholds | Added. Working defaults in DL-027 and DL-028 (refining DL-006): small-base thresholds for overall and segment figures, an "Under review" rule, and a seven-condition rule for the "possible emerging destination" label. |
| Confirmed Results | Added. Verified counts and lists from the 2026-10-14 full run: concentration, usual strong destinations, recovery classes, possible emerging and under review lists, small-base counts, alignment, and the Aurora, Camiguin and Pampanga examples. |
| Notes and Caveats | Added notes that findings are association and not causation, that recovery above 2019 does not indicate an emerging destination, that tourism change is unstable for small or unreliable bases, that counts include provinces under review, that the destination grouping is a display grouping, that DOT figures can differ from local government counts, and that figures are preliminary. Added references to the decision log entries on special handling. |
| AQ1.1 and AQ2.3 | Question text and formulas are unchanged. |
