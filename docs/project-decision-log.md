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

## Open items

Raised in [#30](../../../pull/30). Resolve each, then log the outcome as a new decision.

| # | Item | Details | Related |
|---|---|---|---|
| OI-1 | PSGC version | Datasets not matched to PSGC codes yet, and the version is not finalized. | DL-002, [#33](../../../pull/33) |
| OI-2 | Sulu | Now in Region IX, but PSA GDP tables (2019–2023) still list it under BARMM. | DL-003 |
| OI-3 | Cotabato City | Now in BARMM, but DOT files still list it under Region XII. | DL-003 |
| OI-4 | Boracay / Aklan | DOT rows change meaning across years: Boracay is separate in 2019–2020, Aklan equals Boracay in 2021–2022, and Aklan is Boracay plus a few towns in 2023–2024. Boracay numbers come from the Caticlan jetty port from 2021. | DL-001, DL-009 |
| OI-5 | Data reliability | Some provinces look unreliable, e.g., Zamboanga Sibugay has identical domestic counts in 2019, 2021, and 2022, then jumps from 8,677 (2023) to 197,053 (2024). | DL-009 |
| OI-6 | Traveler and GVA alignment | Coverage confirmed (DOT 2019–2024, GVA 2019–2023). Consistent PSGC mapping across both not yet confirmed. | DL-002, DL-004 |
| OI-7 | "Emerging" thresholds | Set the minimum 2019 traveler base and what counts as a meaningful increase. | DL-006 |
| OI-8 | Traveler-only comparison year | Use 2024, or exclude these comparisons from the common-year rule. | DL-004 |
