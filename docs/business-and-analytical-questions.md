# ProvInsights Business and Analytical Questions

**Audience:** business readers: planners, reviewers and anyone who needs to know what ProvInsights answers and what the data can say. No code or table knowledge needed. Technical details are in the [documentation index](README.md#part-b-for-technical-readers).

## Contents

- [The problem](#the-problem)
- [Business question](#business-question)
- [Data at a glance](#data-at-a-glance)
- [Scope and definitions](#scope-and-definitions)
- [Analytical questions](#analytical-questions)
- [Province groups](#province-groups)
- [Out of scope](#out-of-scope)
- [Caveats](#caveats)

## The problem

Tourism is concentrated in a few places: in 2023 the 10 leading destinations received **43.7%** of all overnight travelers. The DOT's National Tourism Development Plan 2023-2028 (Goal 4) aims to spread tourism to more provinces, but the evidence needed to compare provinces is scattered: visitor counts come from DOT as yearly PDFs, economic and population data from PSA in different formats, and place codes from PSGC. The sources cover different years and name places differently, so provinces can't be compared directly. ProvInsights puts them on one consistent province-by-year basis.

## Business question

> **How can tourism and economic data across Philippine provinces be analysed to identify destinations that may warrant greater attention for tourism development?**

ProvInsights shows *where to look closer*. It does not prescribe interventions, investments or lead agencies (DL-031, DL-037).

## Data at a glance

What each source measures, and what it can and cannot tell us. Identifiers and source issues are in [Data sources](consolidated-data-sources.md).

| What we need | Source | Measures | Years used | Level | Used for | What it can't tell us |
| --- | --- | --- | --- | --- | --- | --- |
| How many visitors | DOT Regional Distribution of Overnight Travelers (DS_05) | Overnight stays in accommodation establishments | 2019-2023 (2024 loaded) | Province, HUC, NCR | AQ1 to AQ4 | Unique visitors or day-trippers; places DOT doesn't report (BARMM provinces, Sulu, Abra in 2023) |
| Tourism-related output | PSA provincial accounts: A&F gross value added (DS_31) | Hotel and restaurant output, current prices | 2023 (2019-2023 loaded) | Province, HUC, NCR | Output per visitor (AQ2 to AQ4) | Tourist spending only: it includes residents' and business spending, and misses transport, tours and shopping |
| Income level | PSA GDP per capita (DS_29) | Provincial GDP per person, current prices | 2023 | Province, HUC, NCR | Lower-income flag (AQ3, AQ4) | Poverty or household income |
| Size of the local economy | PSA GDP (DS_27) | Provincial GDP, current prices | 2023 | Province, HUC, NCR | Tourism share of the economy (context) | |
| Population | PSA projected mid-year population (DS_18) | Residents | 2019-2023 | Province, HUC, NCR | Travelers per 1,000 residents (AQ1) | Exact 2019 HUC population (estimated, DL-021) |
| Where each place is | PSGC 2Q 2026 (DS_34) | Official codes and names | One snapshot for all years | Every place | Joins all sources; region of each unit | |

## Glossary

Business terms in plain language. Each one links to the decision that set it.

| Term | Plain meaning |
| --- | --- |
| **Province (reporting unit)** | One of 100 areas we compare: 82 provinces, 16 cities DOT reports separately (HUCs), the City of Isabela and NCR (DL-010). |
| **Leading destinations** | The 10 provinces with the most overnight travelers on average, 2019-2023 (DL-032). |
| **Output per visitor** | Hotel and restaurant output divided by overnight travelers, 2023, in pesos (DL-033). A proxy, not tourist spending. |
| **High / low** | At or above / below the 2023 median among provinces with data (DL-034). Relative, not a national target. |
| **Lower-income (lagging)** | 2023 GDP per capita below the median of all 100 provinces (PHP 140,165, DL-035). An income indicator, not a poverty measure. |
| **Small base** | Fewer than 10,000 travelers in 2023; marked "Check before naming" because a small count can inflate output per visitor (DL-036). |
| **Province groups** | Established, Busy but low-output, Small but high-output, Limited activity (see [Province groups](#province-groups)). |
| **What to look at** | A question each group raises for local follow-up, not a recommendation (DL-037). |

## Scope and definitions

- **Units:** 100 reporting units (provinces, HUCs that DOT reports separately, the City of Isabela and NCR; DL-010), called "provinces" here.
- **Years:** trend 2019-2023, with 2020-2021 labeled as COVID-19 years. AQ2 to AQ4 use 2023, the latest year with both DOT and PSA provincial data.

| Term | Definition |
| --- | --- |
| **Tourism activity** | Number of overnight travelers in a province in a year. |
| **Visitors (overnight travelers)** | Travelers reported by DOT as staying overnight in accommodation establishments (`total_travelers`). They count stays, not unique people, and exclude day-trippers. |
| **Leading destinations (top 10 destinations)** | The 10 provinces with the highest average annual overnight travelers, 2019-2023, averaged over the years each province has data (DL-032). |
| **Tourism-related output** | Accommodation and food services (A&F) gross value added, current prices (`afs_gva_current_2023`). Our tourism-related economic proxy (DL-007). |
| **Output per visitor** | A&F GVA (published in thousand PhP, so × 1,000) ÷ overnight travelers, 2023, in PhP (DL-033). |
| **Higher/lower income** | 2023 GDP per capita at or above/below the median of all reporting units with 2023 GDP per capita (DL-035). |
| **Small base** | Fewer than 10,000 overnight travelers in 2023. Output per visitor may be inflated by the small count, so these provinces are marked "Check before naming" (DL-036). |

## Analytical questions

The four questions build the answer in order: find the gap, compare output per visitor, check the pattern, then point to where to look.

| AQ | Question | What it tells us | Analytics tables |
| --- | --- | --- | --- |
| **AQ1** | Which provinces have the highest and lowest tourism activity, and how is it distributed? | How uneven tourism is, how much goes to the leading destinations, and which provinces receive the fewest visitors | `tourism_activity`, `tourism_concentration` |
| **AQ2** | How do provinces compare on both the number of visitors and the tourism-related output per visitor? | Whether provinces with similar visitor numbers generate similar output per visitor | `tourism_economy` |
| **AQ3** | Is high tourism-related output per visitor found only in higher-income provinces? | Whether the AQ2 pattern goes beyond income | `tourism_economy` |
| **AQ4** | Which provinces beyond the top 10 destinations warrant closer attention and what does the data show for each? | A named list of provinces, each with the gap the data shows | `tourism_economy`, `tourism_activity` |

**AQ2 starts from a simple question:** *if two provinces attract the same number of visitors, do they generate the same tourism-related output from them?* The answer is often no, and the [province groups](#province-groups) show how they differ.

**AQ3 is a check on AQ2.** Higher-income provinces have more hotel and restaurant activity from their own residents, so they could show high output per visitor without more tourism. If lower-income provinces also appear among the high-output groups, the pattern goes beyond income, and those provinces deserve a closer look.

**AQ4 lists every province beyond the leading destinations that has a group**, ordered by the gap the data shows (Busy but low-output, then Small but high-output, then Limited activity, then Established, which shows no gap on these two measures), then lower-income provinces first, then by visitors, highest first (DL-037). Small-base provinces stay in the list, marked "Check before naming".

## Province groups

Each province is placed against the 2023 medians of visitors and output per visitor, taken across all provinces with both values. At or above the median counts as high (DL-034).

| Group | Visitors | Output per visitor | What it looks like | Gap the data shows | What to look at |
| --- | --- | --- | --- | --- | --- |
| **Established** | High | High | Visitors come, and each is linked to high local activity | None on these two measures | Do the benefits reach nearby provinces? |
| **Busy but low-output** | High | Low | Visitors come, but each is linked to less local activity | Output per visitor | Where does visitor spending go? |
| **Small but high-output** | Low | High | Few visitors, but high output from each | Visitor numbers | What keeps visitor numbers low? |
| **Limited activity** | Low | Low | Little tourism activity so far | Both | How does tourism compare with other sectors here? |

Groups and medians are derived in the dashboard dataset `ds_profile` (`dashboard/datasets/05_profile_2023.sql`).

## Out of scope

- Causal claims, predicted returns or guaranteed outcomes (DL-008).
- Recommended interventions, investments, infrastructure or lead agencies. ProvInsights does not measure access, carrying capacity, community acceptance or investment viability (DL-037).
- Treating A&F GVA as tourism revenue or tourist spending (DL-007).
- Pre- versus post-pandemic comparison.

## Caveats

- **Output per visitor is a proxy.** A&F includes spending by residents and business travelers. A small or undercounted visitor count can also inflate it, so provinces under 10,000 travelers in 2023 are flagged as a small base (DL-036).
- **Missing is not zero.** Missing values stay NULL (DL-009). Provinces DOT doesn't report (BARMM provinces and Sulu, plus Abra in 2023) get no group.
- **Shares are of reported visitors** in the included provinces, not every visitor to the country.
- **Groups are relative.** Medians and groups describe positions among provinces with 2023 data, not national benchmarks.
- **Recovery is supporting context.** `usual_strong_destination_2019` (DL-026, superseded), `tourism_recovery` and `traveler_segment_recovery` (DL-028, DL-029) stay in Analytics, but they are not used to answer the business question.
