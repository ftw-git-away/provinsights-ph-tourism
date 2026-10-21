# ProvInsights Business and Analytical Questions

## Contents

- [Business question](#business-question)
- [Scope and definitions](#scope-and-definitions)
- [Analytical questions](#analytical-questions)
- [Province groups](#province-groups)
- [Out of scope](#out-of-scope)
- [Caveats](#caveats)

## Business question

> **How can tourism and economic data across Philippine provinces be analysed to identify destinations that may warrant greater attention for tourism development?**

ProvInsights shows *where to look closer*. It does not prescribe interventions, investments or lead agencies (DL-031, DL-037).

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
