# ProvInsights Business and Analytical Questions

## What are we trying to answer?

At the end of the analysis, we want to be able to answer one simple question:

> **Which provinces stand out, and which ones deserve a closer look?**

For planning purposes, we also want to understand:

> **Which Philippine provinces may merit closer evaluation for tourism development or support, based on their tourism activity, recovery, and relevant economic indicators?**

A province being flagged as a **priority** does **not** mean we have proven that it needs intervention. It only means the available evidence suggests that it deserves further review.

Any recommendation from ProvInsights should therefore be treated as a **starting point for discussion and local validation**, not as an automatic policy or investment decision.

---

## What do we mean by the key terms?

| Term | What we mean |
| --- | --- |
| **Geographic unit** | Province-level analysis using validated PSGC mapping. Province, HUC, and NCR distinctions will be preserved until the team agrees on comparable analytical units. |
| **Core period** | 2019–2023. We use **2019 as the pre-pandemic baseline**, calculate recovery separately for **2022 and 2023**, and use **2023 as the main endpoint** for economic comparisons. |
| **Tourism activity** | Reported overnight travelers, as defined in the DOT source (DS_05). These are reported activity counts, not unique visitors and not all travelers to a province. |
| **Tourism intensity** | Reported overnight travelers per 1,000 residents for the same province and year. This helps show whether tourism activity is large relative to the local population. |
| **Traveler categories** | Domestic, foreign, and overseas Filipino, following the DOT source. **Overseas Filipino does not automatically mean OFW.** |
| **Tourism-related economic activity** | Accommodation and Food Services (A&F) GVA. We use this as a proxy because it is closely related to tourism activity, but it also includes spending by residents and business travelers. |
| **Economic growth** | Change in **constant-price A&F GVA** from 2019 to 2023. Constant prices are used so the comparison reflects real growth rather than inflation. |
| **Economic significance** | **Current-price A&F GVA as a share of current-price provincial GDP** for the same year and geography. The headline year is 2023. |
| **Interpretation** | We describe patterns and associations. If tourism and economic indicators move together, that does **not** prove that one caused the other. |
| **National context** | PTSA may be used for national context only. National tourism GDP share is not directly comparable with provincial A&F sector share. |

---

# BQ1 — Tourism Activity and Recovery

> ## **Which provinces stand out in tourism activity and recovery, and which appear to be lagging?**

Here, **lagging** only means that reported tourism activity remains below a comparable 2019 baseline. It is not a judgment on a province's overall development or whether it needs intervention.

We answer this business question in three parts.

---

## AQ1.1 — Where is tourism activity highest, lowest, and most concentrated?

> **Which provinces have the highest and lowest tourism activity and tourism intensity, and how concentrated is reported activity across provinces?**

This gives us two different views of tourism:

- **Tourism activity** shows the total number of reported overnight travelers.
- **Tourism intensity** adjusts that activity for population size, helping smaller provinces stand out when tourism is large relative to the number of residents.

We will use **2023 as the headline year**, while clearly showing the selected year and source coverage.

### Measures

```text
Tourism intensity =
    reported overnight travelers / population × 1,000

Top-N concentration =
    reported activity in top N included provinces
    / reported activity in all included provinces × 100
```

We will report the share accounted for by the **top 5** and **top 10** provinces.

The denominator must include only **non-overlapping and comparable provincial records**. If some provinces are missing, the included total must be described as the total for the available coverage, not as a complete national total unless that has been verified.

### What this should tell us

- which provinces have the highest and lowest reported activity;
- which provinces rank differently once population size is considered; and
- whether reported tourism activity is concentrated in a small number of provinces or spread more widely.

---

## AQ1.2 — Which provinces returned to their 2019 tourism level?

> **Which provinces have returned to or surpassed their pre-pandemic tourism levels, and which remained below them?**

For this project, **recovery has a very specific meaning**:

> the extent to which a province's reported overnight tourism activity in 2022 or 2023 returned to, remained below, or exceeded its 2019 level.

This is **recovery in reported overnight tourism activity**. It does not mean that jobs, tourism revenue, business profitability, hotel capacity, or the whole tourism sector have fully recovered.

We calculate **2022 and 2023 separately**.

### Measures

```text
Recovery index(year) =
    activity(year) / activity(2019) × 100

Absolute change(year) =
    activity(year) − activity(2019)

Below 2019:
    recovery index < 100

At or above 2019:
    recovery index ≥ 100
```

For the main 2023 view:

```text
Recovery index(2023) =
    activity(2023) / activity(2019) × 100
```

Examples:

- **80** = activity is still 20% below 2019
- **100** = activity is back to the 2019 level
- **125** = activity is 25% above 2019

Use the unrounded value when assigning a province to a group.

### Important handling rules

- If the **2019 value is missing**, the recovery index is **not calculable**.
- If the **2019 value is zero**, the recovery index is also **not calculable**.
- Neither case should be treated as **zero recovery**.
- If a geographic or reporting change makes 2019 and 2022/2023 not comparable, mark the result as **not comparable** unless an approved adjustment exists.

### What this should tell us

- which provinces were still below their 2019 reported activity in 2022 and 2023;
- which provinces had returned to or moved above their 2019 level; and
- how large the remaining recovery gap was in both percentage and absolute terms.

---

## AQ1.3 — Who is still missing from the recovery?

> **Among provinces that remained below their 2019 level, how do recovery patterns differ between domestic, foreign, and overseas Filipino travelers?**

For the headline analysis, we focus on provinces with a valid **2023 total recovery index below 100**.

We then look at whether the remaining gap is associated more with domestic, foreign, or overseas Filipino travelers.

### Measures

```text
Domestic recovery(2023) =
    domestic(2023) / domestic(2019) × 100

Foreign recovery(2023) =
    foreign(2023) / foreign(2019) × 100

Overseas Filipino recovery(2023) =
    overseas Filipino(2023) / overseas Filipino(2019) × 100
```

The same comparison may also be shown for 2022.

Only categories with **comparable data and positive 2019 baselines** should be used.

If a DOT source combines foreign and overseas Filipino travelers, keep that combined category. Do not create separate counts that are not present in the source, and do not treat missing overseas Filipino values as zero.

Traveler composition may also be shown as context, but the differences do not tell us **why** a traveler category recovered faster or slower.

### What this should tell us

A province could, for example, already be above its 2019 domestic level while still remaining far below its 2019 foreign level. That gives a more useful picture than saying only that the province is "recovered" or "not recovered."

---

## Data needed for BQ1

- **DS_05:** DOT reported overnight travelers by area, year, and traveler type
- **DS_33 / DS_34:** PSGC references and approved historical mapping
- **Population:** approved annual province-level denominator  
  - candidate inputs: DS_18 workbook and DS_24 Table B
  - final choice must confirm year coverage, census/projection basis, and geographic comparability

### Expected outputs

- tourism activity and intensity rankings
- top 5 / top 10 concentration measures
- separate 2022 and 2023 recovery comparisons
- traveler-type recovery profiles
- clear coverage and comparability flags

---

# BQ2 — Tourism Recovery and Economic Conditions

> ## **How is recovery in tourism activity associated with changes in local tourism-related economic activity across provinces?**

BQ1 tells us **where tourism activity recovered and where it did not**.

BQ2 asks the next question:

> **When reported tourism activity changed, did the tourism-related local economy move with it?**

For this project, the available economic proxy is **Accommodation and Food Services (A&F) GVA**.

A&F GVA is useful because it captures an important tourism-related part of the local economy, but it is **not a direct measure of tourism-generated value**. It also includes activity from residents and business travelers.

---

## AQ2.1 — Did tourism activity and A&F GVA grow together?

> **How does the change in reported tourism activity from 2019 to 2023 compare with growth in A&F GVA across provinces?**

We compare each province's change in reported tourism activity with the change in its **constant-price A&F GVA** over the same period.

Constant prices are used here because we want to compare real growth over time rather than changes caused only by inflation.

### Measures

```text
Tourism activity change (%) =
    (activity(2023) − activity(2019))
    / activity(2019) × 100

Real A&F GVA growth (%) =
    (constant-price A&F GVA(2023)
    − constant-price A&F GVA(2019))
    / constant-price A&F GVA(2019) × 100
```

Both ratios require a **positive baseline**, and the tourism and economic data must refer to comparable geographic units.

The main output may use a scatter plot or table, with absolute changes shown where helpful.

### What this should tell us

- provinces where tourism activity and A&F GVA both grew;
- provinces where both remained below their 2019 level; and
- provinces where the two indicators moved in different directions.

This is a comparison of **co-movement**, not a claim that returning travelers caused the economic change.

---

## AQ2.2 — Where do tourism and the economic proxy tell the same story?

> **Which provinces show tourism activity and A&F GVA moving in the same direction, and which show divergent patterns?**

This uses the same 2019–2023 measures as AQ2.1, but turns them into easy-to-read province profiles.

| Tourism activity | Real A&F GVA | What the pattern means |
| --- | --- | --- |
| Increased | Increased | Both measures are above their 2019 levels |
| Decreased | Decreased | Both measures remain below their 2019 levels |
| Increased | Decreased | Tourism activity is above 2019 while the economic proxy remains below |
| Decreased | Increased | The economic proxy is above 2019 while tourism activity remains below |

If a value is unchanged, show it separately using the unrounded difference.

If a tourism/economic pair is missing or not geographically comparable, leave it as **not comparable** rather than forcing it into a group.

A divergent pattern is a reason to investigate further. It is **not** proof of tourism leakage, weak business performance, or any specific cause.

### What this should tell us

This gives us a province-level list of places where:

- the tourism and economic indicators reinforce each other; or
- the two indicators tell different stories and deserve a closer look.

---

## AQ2.3 — How important is A&F Services within the local economy?

> **How does the economic significance of A&F Services differ among provinces with different tourism recovery patterns?**

A province where A&F Services make up 1% of the economy is structurally different from a province where the same sector makes up 12%.

To add that context, we calculate the A&F sector's share of provincial GDP.

### Measure

```text
A&F share of provincial GDP (%) =
    current-price A&F GVA
    / current-price provincial GDP × 100
```

Use **2023** as the headline year.

The A&F numerator and GDP denominator must use:

- the same geography;
- the same year;
- the same units; and
- the same current-price basis.

GDP must also be positive.

A higher A&F share tells us that the sector has a larger weight in the local economy. It does **not** automatically mean the province is tourism-dependent, has more tourism jobs, needs intervention, or should receive greater priority.

### What this should tell us

This adds economic context to the recovery and alignment profiles.

For example, two provinces may both show tourism and A&F growth, but A&F may represent a much larger part of the economy in one province than in the other.

---

## Additional context — GDP per capita

> **How does tourism intensity compare with GDP per capita across provinces?**

This is useful as a **contextual analysis**, not as another core business question.

A 2023 cross-province comparison can show whether provinces with high tourism intensity also tend to have high GDP per capita, and which provinces depart from the broader pattern.

The GDP-per-capita price basis must be stated clearly.

This comparison does not tell us that tourism caused a province to become wealthier.

---

## Data needed for BQ2

- **DS_05:** reported tourism activity
- **DS_32:** constant-price provincial A&F GVA for growth
- **DS_31 + DS_27:** current-price A&F GVA and provincial GDP for sector shares
- **DS_29 or DS_30:** GDP per capita for contextual analysis; selected price basis must be declared
- approved population denominator and PSGC mapping
- **DS_28:** optional broader real-GDP context
- **DS_26 and DS_01:** regional checks and national context where the definitions support comparison

### Expected outputs

- tourism activity change vs. real A&F GVA growth
- province-level alignment and divergence groups
- 2023 A&F sector shares by recovery pattern
- contextual tourism-intensity vs. GDP-per-capita comparison

---

# How the pieces come together

The final output of ProvInsights is not meant to produce a single "best" or "worst" province.

Instead, it should build a **province-level profile** that combines:

```text
tourism activity
+ recovery
+ traveler composition
+ population context
+ economic context
    ↓
province-level assessment
    ↓
identify what stands out
    ↓
flag provinces that deserve closer evaluation
    ↓
suggest actions or questions to explore with local stakeholders
```

A province may stand out because it:

- surpassed its comparable 2019 reported tourism level;
- has unusually high tourism intensity;
- shows growth in both tourism activity and real A&F GVA;
- shows stronger domestic recovery than foreign or overseas Filipino recovery; or
- shows a clear divergence between traveler recovery and the economic proxy.

The final synthesis should help answer:

> **What appears to be happening in this province, why should decision-makers pay attention, and what should be explored next?**

Any proposed action should be shown together with:

- the observations that support it;
- the limitations of the available evidence; and
- any additional information needed before acting.

For example, if tourism activity recovered but A&F GVA did not, that province may deserve closer review. The next step may be to check reporting coverage or speak with local tourism businesses before assuming there is an economic problem.

A **priority flag** is therefore a screening result, not an investment ranking and not proof that an intervention will work.


---

# What this project does not claim

ProvInsights does **not** establish:

- that tourism caused economic growth;
- that economic conditions caused tourism recovery;
- job recovery or tourism employment without an additional verified employment source;
- investment returns or unmet infrastructure needs;
- whether a specific intervention will work;
- unique visitor counts from reported overnight travelers;
- direct tourism-generated value from A&F GVA; or
- provincial tourism values from national PTSA figures.

Any proposed action should remain conditional on local validation and additional evidence where needed.

---

# References

- [Consolidated source assessment](consolidated-data-sources.md)
- [Bronze ingestion guide](bronze-ingestion-guide.md)
- [Project decision log](project-decision-log.md)
- [Source inventory](https://docs.google.com/spreadsheets/d/18tTQHJLcJrIFVfNzgvT97ZMM6PfJNnAL/edit)
- [Prior scope review — PR #30](https://github.com/ftw-git-away/provinsights-ph-tourism/pull/30)
- [Source assessment review — PR #33](https://github.com/ftw-git-away/provinsights-ph-tourism/pull/33)
