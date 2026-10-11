# ProvInsights Business and Analytical Questions

## Table of Contents

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
- [Notes and Caveats](#notes-and-caveats)

---

## Main Business Question

> **Which Philippine provinces warrant closer attention based on their tourism activity and recovery, how these relate to local economic performance, and whether tourism growth is emerging beyond the usual strong destinations?**

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
| **Supporting analysis** | Tourism outcomes versus baseline economic strength | `tourism_economy` |

---

## Shared Definitions

| Term | Definition |
| --- | --- |
| **Province** | Used as the main client-facing term. Selected separately reported HUCs, City of Isabela, and NCR are also included in the analytical model where required by source reporting. |
| **Baseline year** | 2019 |
| **Recovery years** | 2022 and 2023, each compared separately with 2019 |
| **Tourism activity** | Reported overnight travelers in accommodation establishments |
| **Tourism intensity** | Reported overnight travelers per 1,000 residents |
| **Traveler categories** | Domestic, foreign, and overseas Filipino |
| **Economic proxy** | Accommodation and Food Services (A&F) GVA |
| **Real A&F growth** | Change in constant-price A&F GVA from 2019 to 2023 |
| **Economic significance** | Current-price A&F GVA as a share of current-price GDP |

---

<a id="bq1"></a>

## BQ1: Which provinces stand out in tourism activity and recovery, and which appear to be lagging?

The tourism landscape is described through activity, intensity, concentration, recovery relative to 2019, and traveler-segment recovery among provinces that remain below their 2019 level.

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

**Analytical table:**  
`traveler_segment_recovery`

---

<a id="bq2"></a>

## BQ2: How are changes in tourism activity associated with changes in local tourism-related economic activity across provinces?

Changes in tourism activity are compared with changes in A&F GVA so that provinces where tourism and local tourism-related economic activity align or diverge can be identified.

<a id="aq21"></a>

### AQ2.1: How does the change in reported tourism activity from 2019 to 2023 compare with growth in A&F GVA across provinces?

```text
Tourism change (%) =
(2023 travelers - 2019 travelers) / 2019 travelers × 100

Real A&F GVA growth (%) =
(2023 constant-price A&F GVA - 2019 constant-price A&F GVA)
 / 2019 constant-price A&F GVA × 100
```

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

## Notes and Caveats

- **Provinces** is used as the main client-facing term, although selected separately reported HUCs, City of Isabela, and NCR are also included in the analytical model.
- Tourism activity is measured using **reported overnight travelers in accommodation establishments**, not unique visitors or all tourists.
- Recovery is defined specifically as **reported overnight tourism activity relative to 2019**.
- A valid 2019 baseline and `comparable_to_2019 = true` are required for recovery.
- Missing values are retained as NULL and are not replaced with zero.
- Valid ranks or classifications are not assigned to missing or ineligible values.
- **Constant-price A&F GVA** is used for growth.
- **Current-price A&F GVA and GDP** are used for A&F share of GDP.
- A&F GVA is treated as a tourism-related economic proxy, not as a direct measure of tourism revenue.
- Co-movement between tourism and economic indicators is interpreted as **association, not causation**.
- Results are intended to support closer investigation; interventions or investment decisions are not prescribed.
