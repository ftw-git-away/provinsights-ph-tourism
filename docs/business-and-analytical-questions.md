# Tuklas Pinas Business and Analytical Questions

> **Status: Finalized based on PR #30 team review.**
>
> The team has agreed on the three core business questions (BQ) and analytical questions (AQ) which will define the project’s analytical scope and will guide data requirements, transformations, validation, and Gold-layer design.

## Purpose

BQs and AQs will guide the Tuklas Pinas analytics scope, data requirements, transformations, metrics, and Gold-layer design.

Each AQ should directly support its corresponding BQ and be answerable using data the team can verify.

## Overall Question

> **Which provinces stand out in tourism activity, post-pandemic change, and their relationship with local economic conditions, and which patterns merit closer study?**

The project is intended to support descriptive and comparative analysis.

A province or pattern that “merits closer study” is one that stands out in the available evidence and may warrant further investigation. The available data **does not** establish where investment should be directed, where tourism development is inadequate, or where intervention would produce the greatest return.

---

## Shared Scope and Definitions

| Topic | Agreed definition |
| --- | --- |
| **Geographic unit** | Province-level analysis, joined using PSGC codes. Regional totals may be derived from normalized province records after geography mapping is validated. |
| **Time window** | **2019–2023** is the common province-level window. **2019** is the pre-pandemic baseline and **2022–2023** is post-pandemic. Comparisons are 2019 vs. 2022+, not year-over-year growth. |
| **Tourism activity** | Reported overnight travelers in accommodation establishments (DOT, DS-05), by traveler type (domestic, foreign, overseas Filipino). Counts are check-ins, not unique people or all visitors, and are not interchangeable with border "arrivals". Measured as volume and intensity below. |
| **Tourism volume** | Total reported overnight travelers for a province and year. Shows how much reported activity occurs in a province. |
| **Tourism intensity** | Reported overnight travelers per 1,000 residents. Shows how large that activity is relative to the population. |
| **Economic indicators** | Provincial GDP, GDP per capita, and **accommodation and food service GVA** (PSA). Accommodation and food GVA is an **economic proxy**, not a direct tourism measure, because it includes local and business spending. |
| **Interpretation** | Findings describe distributions, changes, and associations. They **do not** establish causation, investment returns, or unmet development needs. |
| **National context** | Philippine Tourism Satellite Account (PTSA) data may provide national context but is not treated as a province-level measure. |

---

# Business Problem 1: Distribution of Tourism Activity

### Business Problem

*Tourism activity is spread unevenly, and there is no single trusted view of where it is concentrated.*

National and local tourism planners cannot easily see which provinces carry most of the country's tourism and which get very little. The data is published across separate DOT and PSA reports at different geographic levels. Without a combined view, promotion budgets and support tend to follow well-known destinations rather than the evidence.

## Business Question

> **Where should tourism promotion and development be focused, based on how tourism activity is actually distributed across provinces?**

## Analytical Questions

1. Which provinces have the highest and lowest reported overnight travelers, and what share do the top 5 and top 10 account for?
2. How does the ranking change per 1,000 residents? (This helps smaller provinces with high tourism for their size, such as Camiguin or Siquijor, show up.)
3. What is each province's domestic, foreign, and overseas Filipino mix?

### Data Needed

- DOT overnight travelers by province, year, and traveler type (DS-05)
- Population by province and year (DS-24 Table B, and/or GDP ÷ GDP per capita from DS-27 to DS-30)
- PSGC codes for province identity (DS-33, DS-34)

### Answerability

Answerable for 2019–2023 once the DS-05 extraction is verified. Raw counts show **volume** and per-resident measures show **intensity**; neither means a province is "best".

**Known limits:** DOT counts are check-ins (the same person may be counted more than once), Region II reports overseas Filipinos inside Foreign, and some provinces are blank in some years.

Some DOT records may combine geographic areas, omit certain areas, or use traveler-type categories inconsistently across regional files. Missing, incompatible, or unavailable records must not be interpreted as zero.

---

# Business Question 2: Post-Pandemic Change

### Business Problem

*Planners cannot tell early which destinations are gaining momentum and which are losing it*

Tourism figures are released as yearly snapshots in separate reports, so change over time is hard to track. Emerging destinations may not get support until they are already under strain, and declining ones may be noticed too late. The 2020-2021 downturn makes this worse because it is unclear which areas have fully recovered.

Changes in reporting coverage, geographic definitions, and data availability may also create apparent changes that do not represent actual changes in tourism activity.

A common pre-pandemic baseline is therefore needed.

## Business Question

> **Which destinations need early attention, either support for growth or intervention for decline, based on how their tourism activity has changed compared with before the pandemic?**

## Analytical Questions

1. **How do each province's 2022-2023 traveler counts compare with 2019, in absolute terms and as a percentage of the 2019 level?**
2. **Which small-base provinces are now above their 2019 level (emerging destinations)?**
3. **Did domestic or foreign travelers recover faster, and where?** (International borders were closed to tourists until 2022.)

### Data Needed

- DOT overnight-traveler data by province, year, and traveler type, for 2019 and 2022–2023 (DS-05)
- Documentation of missing, revised, provisional, or geographically inconsistent records

### Answerability

Answerable where a province has reported values in both 2019 and at least one post-pandemic year. Provinces without both are shown as **not comparable**, not as zero recovery. The project should not use labels such as **recovered** or **emerging** until the comparison rules and thresholds are explicitly defined. Known reporting changes, including the Aklan/Boracay series and other unusual records identified during source review, must be investigated, flagged, or excluded from affected comparisons.

The analysis can show **how reported tourism activity changed**. It cannot establish why that change occurred.

---

# Business Question 3: Tourism and Local Economic Conditions

### Business Problem

*It is unclear where tourism activity goes together with stronger local economies, and where it does not.*

Tourism and economic data come from separate agencies at different geographic levels. Without combining them at a consistent geographic and temporal grain, it is difficult to examine whether provinces with greater reported tourism activity also show different economic characteristics or whether changes in tourism activity move alongside changes in relevant local economic indicators.

## Business Question

> How does tourism activity relate to local economic conditions, and where is that link strongest or weakest?

## Analytical Questions

1. **How does reported traveler intensity compare with GDP per capita across provinces?**
2. **How does change in reported traveler activity compare with growth in accommodation and food service GVA over the same period?**
3. **How does each province's accommodation and food service share compare with the national share?** (PTSA is shown as national context only.)

### Data Needed

- DOT overnight travelers by province and year (DS-05)
- Provincial GDP, current and constant prices (DS-27, DS-28)
- Provincial GDP per capita, current and constant (DS-29, DS-30)
- Provincial accommodation and food service GVA, current and constant (DS-31, DS-32)
- Population by province and year
- Regional table (DS-26, Table 3.63) and PTSA (DS-01, DS-04) as cross-checks and context only

### Answerability

The reviewed PSA tables provide provincial accommodation and food service GVA through 2023, excluding BARMM provinces (no DOT data). AP2 compares one 2019-to-2023 change per province across provinces, so it supports a scatter or rank comparison rather than a trend claim. Accommodation and food service GVA is part of GDP, so relating it to GDP is partly circular; if DOT counts cannot be verified, use:

- **current-price values** when calculating economic shares, where relevant;
- **constant-price values** when comparing economic growth over time.

Accommodation and food service GVA is not equivalent to tourism-generated economic value. It also captures spending by residents and businesses unrelated to tourism.

Any observed relationship should therefore be interpreted as an **association**, not evidence that tourism caused economic growth or that economic conditions caused tourism activity.

---

# Derived Screening Output

The former fourth question, "Which destinations warrant further investigation?", is no longer a separate business question. It is a **screening output** built from BQ1 to BQ3, flagging provinces that stand out on one or more of:

- high or low traveler volume or intensity (BQ1)
- recovery well above or below the 2019 level (BQ2)
- traveler activity that diverges from local economic indicators (BQ3)

Screening criteria must be defined before final results are interpreted.

A flag means:

> **This province or pattern merits closer study.**

A flag does **not** mean:

- the province is underserved;
- tourism investment should be increased;
- infrastructure should be expanded;
- the province is performing poorly;
- tourism caused its economic performance; or
- a specific intervention should be implemented.

Those conclusions require additional evidence (such as accommodation capacity, infrastructure, environmental conditions, and local plans) beyond the scope of this project.

---

# Our Source Assessment

- [GitAway - Scope and Source Feasibility](https://docs.google.com/spreadsheets/d/18tTQHJLcJrIFVfNzgvT97ZMM6PfJNnAL/edit?usp=sharing&ouid=109728975218616355743&rtpof=true&sd=true)
- Findings and verdicts: [PR #33](https://github.com/ftw-git-away/tuklas-pinas-data-platform/pull/33)

Source IDs (DS-xx) follow the Source Inventory as of Sep 30, 2026.

---

# Out of Scope

The following are outside the core scope of the project:

- claims that tourism caused economic growth or economic growth caused tourism;
- ROI or investment-return analysis;
- “best place to invest” rankings;
- recommendations for tourism infrastructure or capacity expansion;
- treating accommodation and food service GVA as direct tourism output;
- treating national PTSA figures as province-level values;
- municipality- or city-level analysis unless the required sources support a consistent extension; and
- conclusions about tourism development needs that require evidence not included in the current dataset.

---

## Implementation and Data Quality Decisions Before Analysis

The following items do not change the agreed business questions but must be resolved before publishing comparable results.

### Geographic Mapping

- Select the PSGC version to be used as the canonical geographic reference.
- Build and document a crosswalk for historical source labels.
- Define how highly urbanized cities are handled.
- Review combined DOT labels that refer to a city and province together.
- Address geographic changes involving areas such as the Negros provinces, Sulu, Cotabato City, and regional boundaries.

### Missing and Incompatible Records

Preserve the distinction between:

- a true zero;
- a missing value;
- unavailable data;
- suppressed data; and
- an incompatible geographic record.

Missing or unavailable tourism data must not be converted to zero.

### BARMM

Where DOT regional files do not provide provincial traveler data, the relevant tourism values should be represented as unavailable unless another verified source is adopted.

### Aklan/Boracay

Periods affected by changes in tourism-reporting methodology must be flagged, excluded, or presented separately until a valid comparison rule is approved.

### Comparison Thresholds

Any labels used in the screening output, including terms such as:

- recovered;
- small base;
- emerging; or
- unusually high or low

must have predefined rules or thresholds before final results are interpreted.
