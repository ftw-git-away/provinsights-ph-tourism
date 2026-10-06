# ProvInsights Business and Analytical Questions

> **Status: Updated scope proposed for team review.**
>
> This revision consolidates the three questions finalized in PR #30 into two supporting business questions: tourism activity and recovery, and their association with economic conditions. It guides source requirements, Silver transformations, Gold models, and analytics once approved.

## Purpose and Main Business Question

> **Which Philippine provinces should be prioritized for tourism development or closer intervention based on evidence from tourism activity, recovery, and relevant economic indicators?**

ProvInsights supports this planning question by identifying provinces and patterns that merit closer evaluation. A priority flag means priority for investigation and planning review; it does not establish that a specific intervention is needed or will succeed. Proposed actions are options for further evaluation with local stakeholders and additional evidence.

The analytical synthesis is:

> **Which provinces stand out, and which ones deserve a closer look?**

## Shared Scope and Definitions

| Topic | Definition |
| --- | --- |
| Geographic unit | Province-level analysis using validated PSGC mapping. Preserve province, HUC, and NCR distinctions until the team approves comparable analytical units. |
| Core period | 2019–2023. Use 2019 as the pre-pandemic baseline, calculate 2022 and 2023 recovery separately, and use 2023 as the headline endpoint for economic comparisons. |
| Tourism activity | Reported overnight travelers, as defined in the DOT source (DS_05). These are reported activity counts, not unique people or all visitors, and are not interchangeable with international border arrivals. |
| Tourism intensity | Reported overnight travelers per 1,000 residents, using an approved population denominator for the same geographic unit and year. |
| Traveler categories | Domestic, foreign, and overseas Filipino as reported by DOT. Overseas Filipino is not synonymous with overseas Filipino worker (OFW). |
| Economic proxy | Accommodation and Food Services (A&F) GVA. It includes resident and business spending unrelated to tourism and is not direct tourism-generated value. |
| Economic growth | Change in constant-price A&F GVA from 2019 to 2023. |
| Economic significance | Current-price A&F GVA as a percentage of current-price provincial GDP for the same year and geography; headline year: 2023. |
| Interpretation | Descriptive comparisons and associations. Province-level alignment means direction and magnitude of observed changes, not a province-specific correlation or causal effect. |
| National context | PTSA may provide national context; it is not a provincial measure and its tourism GDP share is not equivalent to the A&F sector share. |

## BQ1 — Tourism Activity and Recovery

> **Which provinces stand out in tourism activity and recovery, and which appear to be lagging?**

Here, “lagging” describes reported activity below a comparable 2019 baseline; it is not a judgment of overall provincial performance or development needs.

### AQ1.1 — Activity, Intensity, and Concentration

**Which provinces have the highest and lowest tourism activity and tourism intensity, and how concentrated is reported activity across provinces?**

Show provincial reported overnight-traveler volumes and intensity, including the top 5 and top 10 provinces' share of the included provincial total. Use 2023 as the headline year and show the selected year and coverage clearly.

```text
Tourism intensity = reported overnight travelers / population × 1,000

Top-N concentration =
    reported activity in top N included provinces
    / reported activity in all included provinces × 100
```

The denominator must include only non-overlapping, comparable provincial records. Missing provinces must be disclosed; the included total must not be labeled complete national coverage unless verified.

### AQ1.2 — Recovery Relative to 2019

**Which provinces have returned to or surpassed their pre-pandemic tourism levels, and which remained below them?**

Calculate each province's 2022 and 2023 values relative to its 2019 baseline, keeping the endpoints separate. Show both absolute differences and recovery indices.

```text
Recovery index(year) = activity(year) / activity(2019) × 100
Absolute change(year) = activity(year) − activity(2019)

Below 2019: recovery index < 100
At or above 2019: recovery index ≥ 100
```

For the headline 2023 view:

```text
Recovery index(2023) = activity(2023) / activity(2019) × 100
```

Classify using unrounded values. A missing or zero 2019 denominator makes the index undefined; report it as not calculable rather than zero recovery. A geographic or reporting break makes the comparison not comparable unless an approved adjustment exists.

“Recovered” means returned to the reported 2019 activity level under this rule; it does not establish recovery in jobs, profitability, capacity, or all tourism outcomes.

### AQ1.3 — Traveler-Type Recovery

**Among provinces that remained below their 2019 level, how do recovery patterns differ between domestic, foreign, and overseas Filipino travelers?**

Use provinces with a valid total recovery index below 100 in 2023 for the headline subset. Calculate the same traveler-type comparisons for 2022 when shown.

```text
Domestic recovery(2023) = domestic(2023) / domestic(2019) × 100
Foreign recovery(2023) = foreign(2023) / foreign(2019) × 100
Overseas Filipino recovery(2023) =
    overseas Filipino(2023) / overseas Filipino(2019) × 100
```

Use only comparable categories with positive baselines. Preserve combined categories: where overseas Filipinos are included in foreign travelers, do not invent separate counts or interpret missing overseas Filipino values as zero.

Traveler composition can be displayed as context. Recovery differences do not establish why a traveler category changed.

### Required Sources and Outputs

- **DS_05:** DOT reported overnight travelers by area, year, and traveler type.
- **DS_33/DS_34:** PSGC references and approved historical mapping.
- **Population:** approved annual province-level denominator; DS_18 workbook and DS_24 Table B are candidate inputs. Confirm actual year coverage, census/projection basis, and geographic comparability before choosing a method.

Expected outputs: activity/intensity rankings, concentration measures, 2022/2023 recovery comparisons, traveler-type recovery profiles, and explicit coverage/comparability flags.

## BQ2 — Tourism Recovery and Economic Conditions

> **How is recovery in tourism activity associated with changes in local tourism-related economic activity across provinces?**

The available economic measure is A&F GVA. Every visualization must identify it as an economic proxy with broader coverage than tourism spending.

### AQ2.1 — Tourism Change and A&F Growth

**How does the change in reported tourism activity from 2019 to 2023 compare with growth in A&F GVA across provinces?**

```text
Tourism activity change (%) =
    (activity(2023) − activity(2019)) / activity(2019) × 100

Real A&F GVA growth (%) =
    (constant-price A&F GVA(2023) − constant-price A&F GVA(2019))
    / constant-price A&F GVA(2019) × 100
```

Compare the two changes across provinces using a scatter plot or table. Show absolute changes where useful. Ratios require positive baseline values and consistent geography, units, and price base.

This asks whether reported activity and the economic proxy moved together. It does not attribute economic growth to travelers.

### AQ2.2 — Alignment and Divergence

**Which provinces show tourism activity and A&F GVA moving in the same direction, and which show divergent patterns?**

Compare 2023 with 2019:

| Tourism activity | Real A&F GVA | Descriptive pattern |
| --- | --- | --- |
| Increased | Increased | Both measures above their 2019 levels |
| Decreased | Decreased | Both measures below their 2019 levels |
| Increased | Decreased | Activity above 2019 while the economic proxy remains below |
| Decreased | Increased | Economic proxy above 2019 while activity remains below |

Show unchanged values separately, using unrounded differences. Missing or incompatible pairs remain not comparable. Do not force them into a quadrant.

AQ2.2 interprets the same measures as AQ2.1; it does not require a separate per-province correlation calculation. A mismatch is a reason for closer investigation, not proof of leakage, business failure, or a particular causal explanation.

### AQ2.3 — Economic Significance

**How does the economic significance of A&F Services differ among provinces with different tourism recovery patterns?**

```text
A&F share of provincial GDP (%) =
    current-price A&F GVA / current-price provincial GDP × 100
```

Use 2023 for the headline comparison, matching numerator and denominator geography, units, year, and price basis. GDP must be positive.

Compare these shares across the valid recovery/alignment groups. A 1% sector share and a 12% sector share represent different economic structures; neither alone determines tourism dependence, jobs, intervention need, or priority.

### Additional Context — GDP per Capita

**How does tourism intensity compare with GDP per capita across provinces?**

Show a 2023 cross-province comparison with a clearly labeled GDP-per-capita price basis. This is contextual analysis supporting BQ2, rather than another core business question.

### Required Sources and Outputs

- **DS_05:** reported tourism activity.
- **DS_32:** constant-price provincial A&F GVA for growth.
- **DS_31 and DS_27:** current-price A&F GVA and provincial GDP for sector shares.
- **DS_29 or DS_30:** GDP per capita for contextual comparisons; declare the selected price basis.
- Approved population denominator and PSGC mapping.
- **DS_28:** optional broader real-GDP context.
- **DS_26 and DS_01:** regional checks and national context where definitions support the comparison.

Expected outputs: tourism/economic change comparison, alignment/divergence groups, A&F sector shares by recovery pattern, and contextual intensity/GDP-per-capita comparisons.

## Proposed Solution and Final Synthesis

ProvInsights will develop an **evidence-based tourism prioritization and recommendation framework** that assembles provincial profiles for planning review.

```text
Tourism activity + recovery + visitor composition
    + population context + economic context
    → province-level assessment
    → situation identification and priority for closer evaluation
    → proposed actions to explore with local stakeholders
```

A profile may stand out because it:

- surpassed its comparable 2019 reported tourism level;
- has unusually high tourism intensity;
- shows growth in both tourism activity and real A&F GVA;
- shows stronger domestic recovery than foreign or overseas Filipino recovery; or
- shows divergence between traveler recovery and the economic proxy.

The final synthesis addresses:

> **What appears to be happening in this province, why should decision-makers pay attention, and what action could reasonably be explored?**

Present each proposed action with its supporting observations, limitations, and additional evidence required. For example, a divergent profile may motivate review of reporting coverage and consultation with local businesses before an intervention is considered.

A prioritization flag is a transparent screening result. It is not an automatic investment ranking or proof that an intervention will work. Any composite score, weights, or “unusually high/low” thresholds require documented team approval before use.

## Decisions and Quality Checks Before Analysis

These decisions do not prevent preserving source files in Bronze, but they must be resolved before publishing comparable analytics.

- **Geography:** choose the PSGC reference and historical crosswalk; resolve province/HUC/NCR treatment, combined DOT labels, and relevant geographic changes.
- **Population:** approve the denominator source and annual method, including 2019 coverage and consistency with the tourism/economic unit.
- **Missing values:** distinguish zero, missing, unavailable, suppressed, and geographically incompatible records. Preserve not-calculable and not-comparable flags.
- **Coverage:** disclose excluded provinces and unmatched sources; represent unavailable BARMM tourism data as unavailable.
- **Reporting breaks:** investigate Aklan/Boracay and other source anomalies; flag, exclude, or present separately under approved rules.
- **Traveler categories:** apply regional source caveats, including combined foreign/overseas Filipino categories.
- **Economic consistency:** use constant prices for growth and matched current prices for shares. Check units and series revisions.
- **Screening:** document the 100-point recovery boundary, valid denominators, treatment of unchanged values, and any additional thresholds before interpretation.
- **Traceability:** retain source IDs, provenance, transformation rules, and exclusions through the analytical outputs.

## Scope Boundaries

The project does not establish:

- that tourism caused economic change or economic conditions caused tourism recovery;
- job recovery or tourism employment without an additional verified employment source;
- investment returns, unmet infrastructure needs, or the effectiveness of an intervention;
- unique-visitor counts from reported overnight-traveler activity;
- direct tourism-generated value from A&F GVA; or
- provincial tourism values from national PTSA figures.

Proposed actions must remain conditional on local validation and evidence beyond the project where needed.

## References

- [Consolidated source assessment](consolidated-data-sources.md)
- [Bronze ingestion guide](bronze-ingestion-guide.md)
- [Project decision log](project-decision-log.md)
- [Source inventory](https://docs.google.com/spreadsheets/d/18tTQHJLcJrIFVfNzgvT97ZMM6PfJNnAL/edit)
- [Prior scope review — PR #30](https://github.com/ftw-git-away/provinsights-ph-tourism/pull/30)
- [Source assessment review — PR #33](https://github.com/ftw-git-away/provinsights-ph-tourism/pull/33)

DS identifiers follow the source inventory; display labels such as DS-05 refer to the same source as implementation identifiers such as DS_05.
