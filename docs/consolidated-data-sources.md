# Tuklas Pinas — Data Source Notes (Consolidated)

**Status: Data source assessment complete. Target users, main use case, and final BQ still pending team discussion.**
*Built from our Source Inventory assessments.*

---

## 1. Target Users & Main Use Case

**Not yet formally agreed by the team.**

---

## 2. Geographic Unit & Time Window

**Geographic unit: Province.** All provinces and HUCs, whole Philippines. Region-level data used only as a secondary/summary view, not the primary analysis grain. MunCity-level is a stretch goal — not enough of our sources are disaggregated that far down.

**Time window:**
- **Core window: 2022–2023** — the only period where tourism, population, and GDP sources all overlap
- **Extended, province-only trend view: 2019–2023** — if we're okay dropping region-level from the picture
- **Population only: 2010–2024** or further back (1960+) for context, not for the core comparison

---

## 3. Indicators We Actually Need

- **Population and population growth rate** — needed as the denominator for per-resident tourism/economic measures, and as a market-size signal (a province with a large, growing population is a different kind of prioritization case than a small one). *Source: Table B (#24), Table 1 (#19)*
- **Total GDP (province level)** — our baseline for "local economic conditions." Without it, we'd have no way to say whether a province's economy is big or small, growing or shrinking, which is the whole other half of the tourism-economy comparison. *Source: Table 3.72/73 (#27)*
- **Per capita GDP (province/HUC level)** — normalizes GDP by population, so we're not just favoring provinces that are big by default. Lets us compare economic strength fairly across provinces of very different sizes. *Source: Table 3.74/75 (#28)*
- **Tourism-sector proxy: Accommodation & Food Service GVA** — this is our stand-in for "how much tourism activity is happening" in economic terms, since a direct regional Tourism Satellite Account isn't confirmed available. Needed to compute tourism's share of the local economy (tourism GVA ÷ total GDP), which is the core ratio our BQ candidates depend on. *Source: Table 3.94/95 (#29), Table 3.63 (#26)*
- **Pending verification: overnight traveler counts** — would let us measure actual tourist volume directly, instead of only inferring it through economic proxy. Needed to answer "where is tourism activity itself concentrated" (not just its economic footprint), and to cross-check whether the GVA proxy is actually tracking real tourism or just general food/lodging spending. *Source: Overnight Travelers (#05) — not yet opened/tested*

---

## 4. Candidate Data Sources — Availability, Coverage, Format, Accessibility, Metadata

### Geo / reference

| ID | Owner | Dataset | Grain | Time | Format | Verdict |
|---|---|---|---|---|---|---|
| 25 | Cole | PSGC | Region→Province→City/Mun→Brgy | current (Q2 2026) | XLSX/CSV | USE — the join key + source for our province→region crosswalk |

### Population

| ID | Owner | Dataset | Grain | Time | Format | Verdict |
|---|---|---|---|---|---|---|
| 24 | Cole | Table B (Pop + PGR) | Region/Province/City | 2010/15/20/24 | XLSX | USE — our main pop source |
| 19 | Cole | Table 1 (census years) | Region/Province/City | 1960–2020 | XLSX | USE — good for long trend, old region boundaries pre-2015ish though |
| 21 | Cole | Table 3 | Region/Province/City | 2020 only | XLSX | MAYBE — fine but single-year, Table B covers this + more |
| 23 | Cole | Table 6 | Region/Province/City | 2020 only | XLSX | MAYBE — household pop not total pop, don't mix with Table 3 |
| 18 | Cole | 2015 projections | Region/Province/City | 2020–2025 | PDF | SKIP — Table B replaces this, uses current regions |
| 20 | Cole | Table 2 | National only | 2020 | XLSX | SKIP — no area breakdown |
| 22 | Cole | Table 5 | National only | 2020 | XLSX | SKIP — no area breakdown |

### Tourism — demand side

| ID | Owner | Dataset | Grain | Time | Format | Verdict |
|---|---|---|---|---|---|---|
| 05 | Haze | Overnight Travelers | Region/Province/City | 2000–2024 | PDF, 1/yr | PENDING — **TODO: open this, confirm it's parseable.** Uses "overnight travelers," not "arrivals." Missing BARMM/ARMM entirely. Region column uses 17-region convention — don't trust it, remap via PSGC |
| 03 | Haze | Visitor arrivals by country | National | 2008–2026 | PDF, 1/yr | MAYBE — national only, context/background |
| 08–12 | Haze | PSY 8.1–8.5 | National | varies | XLSX/CSV | MAYBE — national only, decent for intro slide numbers |
| 13 | Haze | Hotel occupancy (NCR) | NCR only | 2000–2023 | XLSX/CSV | SKIP — one region only |
| 06 | Haze | Inbound update, Jul 2024 | National | 1 month | PDF | SKIP — too narrow |
| 07, 14–17 | Haze | Outbound stuff | National | varies | PDF/XLSX | SKIP — wrong direction (outbound, not inbound) |

### Tourism — economic side

| ID | Owner | Dataset | Grain | Time | Format | Verdict |
|---|---|---|---|---|---|---|
| 29 | Cole | Table 3.94/95 (GVA, province) | Province/HUC | 2019–2023 | XLSX/CSV | USE — **our main tourism variable.** Uses 17-region convention — remap via PSGC, don't use as-is |
| 26 | Cole | Table 3.63 (GVA, region) | Region | 2022–2024 | XLSX/CSV | USE — region-level, 18-region convention (has NIR). Secondary/summary use only |
| 01, 04 | Gab, Haze | PTSA tables | National only | varies | CSV/PDF | MAYBE — context only |
| 02 | Gab | Tourism classification system | N/A | 2025 | CSV | USE — reference doc, defines what counts as "tourism" |

### Economy — total

| ID | Owner | Dataset | Grain | Time | Format | Verdict |
|---|---|---|---|---|---|---|
| 27 | Cole | Table 3.72/73 (GDP, province) | Province | 2019–2023 | XLSX/CSV | USE — our denominator for everything |
| 28 | Cole | Table 3.74/75 (per capita GDP) | Province/HUC | 2019–2023 | XLSX/CSV | USE — pre-calculated, saves us a step |

### Selected / Needs Verification / Rejected — summary

**Selected:** PSGC (#25), Table B (#24), Table 1 (#19), Table 3.63 (#26), Table 3.72/73 (#27), Table 3.74/75 (#28), Table 3.94/95 (#29), Tourism classification (#02)

**Needs further verification:**
- #05 (Overnight Travelers) — not yet opened/tested; needs format check (PDF extraction), name-matching to PSGC, confirmation it covers province level consistently
- PSGC codes across all selected sources — need a spot-check pass before building joins, to catch renamed/merged provinces and NIR/BARMM edge cases
- Claim that PSGC (Q2 2026) has 2024 population attached to its codes — need the exact file/column before relying on it instead of Table B

**Rejected, with reasons:**

| Rejected | Reason |
|---|---|
| 2015 projections (#18) | Superseded by Table B (current region structure, more recent data) |
| Table 2, Table 5 (#20, #22) | National-only, no sub-national breakdown |
| Hotel Occupancy NCR (#13) | Single region only, not usable for cross-province comparison |
| Outbound tables (#07, #14–17) | Measure outbound travel — out of scope |
| Inbound Update, single month (#06) | Too narrow, no trend possible |

---

## 5. Data-Quality Issues, Missing Data, Geographic/Time Mismatches, Limitations

**Time-coverage mismatch:** region-level tourism proxy (#26) covers 2022–2024; province-level tables (#27–29) cover 2019–2023. Full overlap across everything is only 2022–2023.

**17-vs-18 region mismatch:** some sources (#26) use the current 18-region split (NIR separated out); others (#29, #05) use the older 17-region grouping. Only breaks things when totaling at the regional level — province-level data is unaffected, since PSGC codes don't change per province.
> **Fix:** build one `province → region` crosswalk from current PSGC. Ignore whatever "region" column each source ships with. Match every source to PSGC by province name/code. Attach region labels only at the end, from our own crosswalk.

**BARMM/ARMM gap:** #05 excludes these entirely. Those provinces will have GDP data (#27/28) but no overnight-traveler data. Still need a team decision: exclude BARMM from tourism-linked analysis, or mark tourism fields N/A (not zero — zero would wrongly imply "no tourism" rather than "no data").

**Tourism proxy limitation:** Accommodation & Food Service GVA includes non-tourist spending (business travel, local dining) — it's a stand-in for tourism activity, not a direct measure.

**HUC vs. province double-counting risk:** #28/#29 report HUCs separately from their parent province; #27 reports province-only. Needs reconciliation before merging.

**New series limitation:** province-level GDP (Provincial Product Accounts) is a newly institutionalized PSA series, rolled out 2021–2025 — limits how far back we can go.

**Terminology mismatches to watch:**
- "Overnight travelers" (#05, accommodation check-ins) ≠ "arrivals" (#03/#08, national border crossings) — not interchangeable
- "Province," not "destination" — municipality-level rows in #05 aren't consistently filled across years

---

## 6. What Our Data Can Support, and What We Should Not Claim

### Can do / Can't do, regardless of which BQ we pick

| Can do | Can't do (yet) |
|---|---|
| Province-level comparison | MunCity-level comparison |
| 2022–2023 core window (all sources overlap) | Anything needing data past 2023 at province level |
| Tourism measured via GVA proxy (#26/#29) | Tourism measured via actual visitor counts (until #05 is verified) |
| Association / correlation language | Causal claims ("tourism drives growth") |
| GDP, per capita GDP, population by province | Investment amounts, ROI, capital spent per province |
| All provinces except BARMM for tourism-linked questions | BARMM provinces for anything needing overnight-traveler data |

*No final BQ picked yet.*

### Explicitly out of scope / not to be claimed
- Municipality/city-level analysis (stretch goal only)
- "Return on investment" or causal economic-impact claims
- Data before 2019 for the core tourism-economy comparison
- Outbound tourism (not relevant to this project's direction)
- Any causal language — all findings are association/pattern-based only

### Key assumptions underlying all of the above
- GVA is our tourism proxy unless/until #05 is verified
- Province PSGC code is the stable identifier; a source's own "region" label is never trusted directly
- Correlation ≠ causation — other factors (infrastructure, existing development) may explain both tourism and GDP independently
- BARMM provinces will have GDP but no tourism-demand data — handling still pending a team decision

---

## Still Open
1. Open and test #05 (Overnight Travelers PDFs) — top priority
2. Verify PSGC codes match correctly across all sources
3. Confirm the PSGC 2024-population claim (exact file/column)
4. Decide BARMM handling (exclude vs. mark N/A)
5. Build the province→region crosswalk table
6. Agree on target users & main use case
7. Land on a final BQ