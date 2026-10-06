# Decision Log

A single, running record of the project's significant decisions: what was decided, why, and what to watch out for. The log is the project's reference for why its data, scope, and methods are set up the way they are.

**On this page:** [Purpose](#purpose) · [How to use](#how-to-use) · [Decisions](#decisions) · [Open items](#open-items) 

## Purpose

The log covers decisions that affect **scope, architecture, data modeling, analytics, tooling, or implementation**. Routine choices that can be reversed in minutes are not logged.

Each entry records the final agreement only. The discussion stays in the linked PR or issue, and the business and analytical questions themselves are tracked in the consolidated questions issue.

## How to use

1. Add a row at the bottom of the [Decisions](#decisions) table with the next ID (`DL-010`, `DL-011`, ...). IDs are sequential and never reused.
2. Fill in every column. Write dates as `YYYY-MM-DD`.
3. Link the PR or issue where the decision was made.
4. To change a past decision, don't edit or delete its row. Set it to `Superseded` and add a new row that links back to it.
5. When an open item is resolved, log the outcome as a new decision and tick the item off.

**Row template**

```markdown
| DL-XXX | YYYY-MM-DD | What was decided | Why | #N | Proposed | Limits, assumptions, follow-ups |
```

**Status values**

| Status | Meaning |
|---|---|
| `Proposed` | Suggested, not yet agreed by the team |
| `Accepted` | Agreed and in effect |
| `Open` | Needs more information or a decision |
| `Superseded` | Replaced by a later decision (link to it) |

## Decisions

| ID | Date | Decision | Rationale | PR / Issue | Status | Notes / Caveats |
|---|---|---|---|---|---|---|
| DL-001 | 2026-09-30 | **Province is the primary analytical grain.** | DOT traveler data and PSA GVA are both available by province. | [#30](../../../pull/30) | Accepted | HUCs have their own codes and can be combined with provinces if needed. |
| DL-002 | 2026-09-30 | **Join all datasets on PSGC codes.** | One consistent geographic key across sources. | [#30](../../../pull/30), [#33](../../../pull/33) | Accepted | PSGC version not yet chosen (see [open items](#open-items)). The 2Q 2026 "Correspondence Code" column can crosswalk old codes. |
| DL-003 | 2026-09-30 | **Derive regions from province-level data.** Normalize province identities, assign a consistent PSGC mapping, then compute regional totals. | Sources mix 17 and 18 regions and change classifications (NIR, BARMM), which could create fake regional growth. | [#30](../../../pull/30) | Accepted | To be documented in the methodology: "Historical observations are normalized to a consistent province-level PSGC geography before regional aggregation." Specific mappings are documented as well, e.g., Negros Occidental 2019 → NIR. |
| DL-004 | 2026-09-30 | **2019 is the fixed pre-pandemic baseline.** Compare against the latest common post-pandemic year across the datasets an indicator needs. | Avoids pandemic distortion and turns "2022+" into an exact rule. | [#30](../../../pull/30) | Accepted | Traveler data runs to 2024 but GVA to 2023, so comparisons needing both use 2023. Year for traveler-only comparisons is open. |
| DL-005 | 2026-09-30 | **Raw traveler count = tourism volume. Travelers per 1,000 residents = tourism intensity.** Show both. | The highest count does not mean best performing. | [#30](../../../pull/30) | Accepted | Each conclusion states which one it rests on. |
| DL-006 | 2026-09-30 | **"Emerging" = above 2019 level AND above a minimum 2019 traveler base AND a meaningful absolute increase.** Show recovery % and absolute increase. | Stops small-base provinces with tiny gains from being flagged. | [#30](../../../pull/30) | Accepted | Thresholds not set yet. |
| DL-007 | 2026-09-30 | **Accommodation and food services GVA is a proxy for tourism-related local activity, not a pure tourism measure.** | Includes resident spending. PTSA covers a broader tourism economy (transport and shopping too). | [#30](../../../pull/30) | Accepted | To be stated in the methodology/limitations. Not equivalent to PTSA's tourism share of GDP. |
| DL-008 | 2026-09-30 | **Report associations, not causation. No ROI or investment claims.** | The data describes what is, not where investment would pay off. | [#30](../../../pull/30) | Accepted | Findings do not claim these are definitively the provinces with the highest tourism returns. |
| DL-009 | 2026-09-30 | **Missing travelers = insufficient/unavailable data, never 0.** Silver DQ rules separate: true zero, missing record, suppressed data, incompatible geographic record. | Treating missing as 0 would make a province look like it has no tourism. | [#30](../../../pull/30) | Accepted | To be implemented in the Silver DQ rules. |
| DL-010 | 2026-10-07 | **A reporting unit is a province, an HUC that DOT reports separately, the City of Isabela, or NCR.** All geography uses PSGC 2Q 2026 for every year. This gives 100 units: 82 provinces, 16 HUCs, City of Isabela, NCR. | Each unit has to cover the same area in DOT and in PSA, so the unit follows the level DOT reports at. One PSGC version for all years stops boundary and region changes from looking like growth (DL-003). | [#SILVER](../../../pull/SILVER) | Proposed | Refines DL-001. Resolves OI-1. The 5 BARMM provinces and Sulu are units with no DOT data (not reported, never 0, DL-009). City of Isabela is a component city with no province in PSGC ("Not a Province"), and Basilan is in BARMM, so it is its own unit. |
| DL-011 | 2026-10-07 | **Lucena (HUC) is counted inside Quezon.** Its PSA rows are added to Quezon in Silver. | DOT has no Lucena row; Lucena's travelers are inside Quezon's DOT figure. Keeping Lucena separate in PSA would make Quezon's DOT and PSA figures cover different areas. | [#SILVER](../../../pull/SILVER) | Proposed | Quezon per-capita GDP is recomputed as total GDP ÷ population, not summed. Quezon's census reference population = 1,980,338 + 280,331 (Lucena). Dagupan, Santiago, Naga and Ormoc (ICCs) are already inside their provinces' PSGC totals, so no action is needed for them. |
| DL-012 | 2026-10-07 | **NCR is one unit.** DOT's NCR city rows and Pateros are summed into NCR. | NCR has no provinces, so city-level units would compare single cities with whole provinces. Several NCR cities print `-` in DOT (e.g. Caloocan and Las Piñas, 2019). | [#SILVER](../../../pull/SILVER) | Proposed | City-level NCR analysis is out of scope. City label variants across years (e.g. "Caloocan City" 2019–21, "City of Caloocan" 2022–24) map to the same code. |
| DL-013 | 2026-10-07 | **Boracay: added to Aklan in 2019–2020; not loaded in 2021–2024.** Aklan is flagged as not comparable across years. | In 2019–2020 Aklan excludes Boracay (2019: Aklan 217,367 vs Boracay 2,034,599). From 2021 Aklan already includes it (2021–22 Aklan = Boracay; 2023–24 Aklan includes "Boracay (Malay)"). Excluding Boracay every year would remove about 2 million travelers from Aklan's 2019 baseline. | [#SILVER](../../../pull/SILVER) | Proposed | Resolves OI-4. DOT counts Boracay at the Caticlan jetty port from 2021, so Aklan's 2019 vs 2023 change still mixes two counting methods. Report Aklan with a caveat. |
| DL-014 | 2026-10-07 | **Clark Freeport Zone is added to Pampanga from 2023.** | DOT printed Clark as a sub-row inside Pampanga in 2019–2022 (2022: Clark 926,372 of Pampanga's 1,124,190). From 2023 Clark is a separate row and Pampanga drops to 386,868. Adding Clark back keeps Pampanga covering the same area in 2019 and 2023. | [#SILVER](../../../pull/SILVER) | Proposed | The zone also covers Capas, Tarlac, but DOT counted all of it under Pampanga until 2022, so the same rule is kept. Pampanga is flagged `breaks_comparability`. Revisit if DOT changes reporting again. |
| DL-015 | 2026-10-07 | **SBMA / Subic Bay Freeport Zone is excluded from province units** and kept in the exceptions list. | The zone spans Zambales (Olongapo, Subic) and Bataan (Morong, Hermosa) and has no single PSGC unit. DOT prints it as its own row in every year (renamed in 2023), so excluding it is consistent across years. | [#SILVER](../../../pull/SILVER) | Proposed | About 1.0 million travelers in 2019 and 0.96 million in 2023 are not assigned to any province. National totals still reconcile (DQ-DOT-15). |
| DL-016 | 2026-10-07 | **DOT rows for Cotabato City are excluded.** | PSGC places Cotabato City (ICC, `1908703000`) in BARMM, which DOT does not report. DOT prints it under Region XII in 2019–2022 only (2019: 207,394; 2020–22: `-`), so loading it would give one BARMM area data for some years only. | [#SILVER](../../../pull/SILVER) | Proposed | Resolves OI-3. Documented as a coverage gap together with BARMM (DL-009). |
| DL-017 | 2026-10-07 | **Masbate City and Sorsogon City are added to Masbate and Sorsogon provinces.** | Both are component cities, part of their province in PSGC and in PSA's provincial accounts. DOT prints them separately. | [#SILVER](../../../pull/SILVER) | Proposed | 2019: Masbate City 101,612; Sorsogon City 86,658. |
| DL-018 | 2026-10-07 | **"Tarlac City" in the 2020 DOT report is treated as the Tarlac province total.** | It is printed in Tarlac's place, and there is no "Tarlac" row and no sub-rows that year. Its value (45,175) fits between 2019 (108,706) and 2021 (38,142). | [#SILVER](../../../pull/SILVER) | Proposed | If a check of the 2020 PDF or DOT shows it is the city only, Tarlac 2020 becomes `not_reported`. |

## Open items

Raised in [#30](../../../pull/30). Resolve each, then log the outcome as a new decision.

| # | Item | Details | Related |
|---|---|---|---|
| ~~OI-1~~ | ~~PSGC version~~ | Resolved by DL-010: PSGC 2Q 2026 is used for every year. | DL-002, DL-010 |
| OI-2 | Sulu | Now in Region IX, but PSA GDP tables (2019–2023) still list it under BARMM. | DL-003 |
| ~~OI-3~~ | ~~Cotabato City~~ | Resolved by DL-016: DOT rows for Cotabato City are excluded (BARMM in PSGC). | DL-003, DL-016 |
| ~~OI-4~~ | ~~Boracay / Aklan~~ | Resolved by DL-013: Boracay added to Aklan in 2019–2020, not loaded in 2021–2024; Aklan flagged as not comparable. | DL-001, DL-009, DL-013 |
| OI-5 | Data reliability | Some provinces look unreliable, e.g., Zamboanga Sibugay has identical domestic counts in 2019, 2021, and 2022, then jumps from 8,677 (2023) to 197,053 (2024). | DL-009 |
| OI-6 | Traveler and GVA alignment | Coverage confirmed (DOT 2019–2024, GVA 2019–2023). Consistent PSGC mapping across both not yet confirmed. | DL-002, DL-004 |
| OI-7 | "Emerging" thresholds | Set the minimum 2019 traveler base and what counts as a meaningful increase. | DL-006 |
| OI-8 | Traveler-only comparison year | Use 2024, or exclude these comparisons from the common-year rule. | DL-004 |
