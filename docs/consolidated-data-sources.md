# Tuklas Pinas — Data Source Notes (Consolidated)

## 1. Target Users & Main Use Case

Tourism planners, DOT, and LGU/regional development offices — using integrated tourism, population, and economic data to see which provinces stand out on tourism activity, recovery, and economic linkage. **Secondary audience:** a public-facing site presenting the same findings.

---

## 2. Geographic Unit & Time Window

**Geographic unit: Province.** All provinces and HUCs, whole Philippines. Region-level data used only as a secondary/summary view, not the primary analysis grain. MunCity-level is a stretch goal — not enough of our sources are disaggregated that far down.

**Time window:**
- **Core window: 2019–2023** — corrected from an earlier 2022–2023 estimate. That narrower window only existed because we were requiring the region-level tourism table (Table 3.63, region GVA, starts 2022) to overlap too. Since regions are built by summing provinces (not read from that table directly), it isn't actually needed for the core analysis — all the real province-level tables already cover 2019–2023. **Table 3.63 is now used only as a validation check**, to confirm our province-summed regional totals roughly match PSA's own published regional figures — not as an analysis input.
- **Why this matters:** with only 2022–2023, BQ2 loses its entire pre-vs-post-pandemic comparison, and every trend would rest on just two years. 2019–2023 restores the real comparison BQ2 depends on.
- **Population only: 2010–2024** or further back (1960+) for context, not for the core comparison — see the population year-gap issue in Section 3

---

## 3. Indicators We Actually Need

- **Population and population growth rate** — needed as the denominator for per-resident tourism/economic measures, and as a market-size signal (a province with a large, growing population is a different kind of prioritization case than a small one). *Source: Table B*
 - **Year-gap problem:** Table B only has 2010, 2015, 2020, 2024 — but per-resident measures now need every year 2019–2023 (per the corrected core window above). **Three options, decision pending:**
 - **Option 1:** estimate the in-between years from the census counts (interpolation)
 - **Option 2:** back out population as GDP ÷ per capita GDP — this recovers the exact population figure PSA itself used when computing per capita GDP, so it's simpler than interpolating and stays consistent with PSA's own published numbers
 - **Option 3 (recommended):** use PSA's own **mid-year population** releases, published annually per province — this is PSA's official year-by-year figure rather than something we derive ourselves. We already have this at province level for **2020–2025** (the "2015 projections" dataset listed above, previously marked SKIP only because of its old 2015-census base and pre-NIR region structure — both fixable through the same PSGC crosswalk we're already applying to every other source, not a reason to drop the dataset entirely). **Only 2019 is still uncovered** by this file, so pair it with Option 1 or Option 2 for that single year, and use the actual mid-year releases for 2020–2023.
- **Total GDP (province level)** — our baseline for "local economic conditions." Without it, we'd have no way to say whether a province's economy is big or small, growing or shrinking, which is the whole other half of the tourism-economy comparison. *Source: Table 3.72/73*
- **Per capita GDP (province/HUC level)** — normalizes GDP by population, so we're not just favoring provinces that are big by default. Lets us compare economic strength fairly across provinces of very different sizes. *Source: Table 3.74/75*
- **Tourism-sector proxy: Accommodation & Food Service GVA** — this is our stand-in for "how much tourism activity is happening" in economic terms, since a direct regional Tourism Satellite Account isn't confirmed available. Needed to compute tourism's share of the local economy (tourism GVA ÷ total GDP), which is the core ratio our BQs depend on. *Source: Table 3.94/95; Table 3.63 is validation-only, see Section 2*
 - **Important limitation — read alongside Section 5's circularity note:** because this proxy is itself a component of GDP, relating it directly to total GDP partly measures GDP against a piece of itself. This is exactly why Overnight Travelers (below) matters so much — it's our only tourism measure that sits outside the economic accounts entirely.
- **Overnight traveler counts — tested, usable with real caveats.** Lets us measure tourist activity directly instead of only inferring it through the economic proxy, and answers "where is tourism itself concentrated" (not just its economic footprint). Also our only non-circular tourism measure — see Section 5. **But:** direct testing found it counts check-in/stay events, not unique people (repeat counting confirmed), plus sub-row double-counting risk, coverage-driven pseudo-growth, and several suspicious values needing quarantine — see the full findings in Section 5. Use for relative comparison across provinces/years, not as an absolute visitor headcount. *Source: Overnight Travelers*

### Province Definition — Still Needs an Explicit Team Decision
The doc has repeatedly flagged HUC-vs-province double-counting risk, but we haven't actually picked one definition and applied it everywhere. Needs a team decision:
- **Suggested:** "province" = the province plus the highly urbanized cities (HUCs) located within it, combined into one figure
- **NCR needs separate handling**, since it has no provinces at all — only cities/municipalities. Decide whether NCR is treated as a single unit, broken into its component cities, or handled some other way, and apply that choice consistently across every source (population, GDP, tourism).

---

## 4. Candidate Data Sources — Availability, Coverage, Format, Accessibility, Metadata

### Geo / reference

| Dataset | Grain | Time | Format | Verdict |
|---|---|---|---|---|
| PSGC 2Q 2026 National and Provincial Summary | Region→Province | current (Q2 2026) | — | USE — validation/structural-integrity checks when rolling up to province/region, not a working data table itself |
| PSGC 2Q 2026 Publication Datafile | Region→Province→City/Mun→Brgy | current (Q2 2026) | — | **USE — confirmed critical spatial backbone / master lookup table.** Also **resolves our earlier open question: yes, this file does carry population counts** alongside the geographic hierarchy. Note: "mixed hierarchical levels within a single dimensional attribute" flagged as a parsing quirk to handle carefully |

### Population

| Dataset | Grain | Time | Format | Verdict |
|---|---|---|---|---|
| Table B (Pop + PGR) | Region/Province/City | 2010/15/20/24 | XLSX | USE — our main pop source |
| Table 1 (census years) | Region/Province/City | 1960–2020 | XLSX | MAYBE / context only — not needed for any current BQ; moved down from USE to keep processing scope small (per computing-cost concern) |
| Table 3 | Region/Province/City | 2020 only | XLSX | MAYBE — fine but single-year, Table B covers this + more |
| Table 6 | Region/Province/City | 2020 only | XLSX | MAYBE — household pop not total pop, don't mix with Table 3 |
| 2015 projections (mid-year population) | Region/Province/City | 2020–2025 | PDF | **USE for the 2019–2023 gap-year problem (Section 3) — reconsidered from SKIP.** Table B still wins for the anchor census years (2020, 2024), but this is our best province-level source for the in-between years 2021–2023. Apply the PSGC crosswalk to fix its old 2015-census base and pre-NIR region labels before use; 2019 still isn't covered, so pair with Option 1 or 2 for that one year |
| Table 2 | National only | 2020 | XLSX | SKIP — no area breakdown |
| Table 5 | National only | 2020 | XLSX | SKIP — no area breakdown |

### Tourism — demand side

| Dataset | Grain | Time | Format | Verdict |
|---|---|---|---|---|
| Overnight Travelers | Region/province/city, and increasingly municipality/destination from 2008 (e.g., Boracay, Panglao, individual NCR cities) | 2000–2024 | PDF, 1/yr | **USE WITH CAUTION — now opened and tested.** Text layer is clean and extractable; 2023 total (55.3M) matches public reporting. But several serious issues found, see detailed findings below — this is no longer a simple "actual tourist counts" upgrade over the GVA proxy; it needs real cleaning rules before use |
| Visitor arrivals by country | National | 2008–2026 | PDF, 1/yr | MAYBE — national only, context/background |
| PSY 8.1–8.5 | National | varies | XLSX/CSV | MAYBE — national only, decent for intro slide numbers |
| Hotel occupancy (NCR) | NCR only | 2000–2023 | XLSX/CSV | SKIP — one region only |
| Inbound update, Jul 2024 | National | 1 month | PDF | SKIP — too narrow |
| Outbound stuff | National | varies | PDF/XLSX | SKIP — wrong direction (outbound, not inbound) |

### Tourism — economic side

| Dataset | Grain | Time | Format | Verdict |
|---|---|---|---|---|
| Table 3.94/95 (GVA, province) | Province/HUC | 2019–2023 | XLSX/CSV | USE — **our main tourism variable, and our core window (2019–2023 confirmed matches this table).** Uses 17-region convention — remap via PSGC, don't use as-is |
| Table 3.63 (GVA, region) | Region | 2022–2024 | XLSX/CSV | USE — **validation-only**, not part of core analysis window (2022–2024 doesn't align with province tables' 2019–2023). Use to sanity-check that province-summed regional totals roughly match PSA's own published regional figures |
| PTSA tables | National only | varies | CSV/PDF | USE (context) — upgraded from MAYBE; BQ3.4 needs this as the national tourism-share reference point |
| Tourism classification system | N/A | 2025 | CSV | USE — reference doc, defines what counts as "tourism" |

### Economy — total

| Dataset | Grain | Time | Format | Verdict |
|---|---|---|---|---|
| Table 3.72/73 (GDP, province) | Province | 2019–2023 | XLSX/CSV | USE — our denominator for everything |
| Table 3.74/75 (per capita GDP) | Province/HUC | 2019–2023 | XLSX/CSV | USE — pre-calculated, saves us a step |

### Selected / Needs Verification / Rejected — summary

**Selected:** PSGC, Table B, mid-year population (2020–2025), Overnight Travelers, Table 3.63, Table 3.72/73, Table 3.74/75, Table 3.94/95, PTSA tables, Tourism classification

**Needs further verification:**
- Overnight Travelers — already opened and tested (not a question of access anymore); several real data-quality issues were found (check-in/stay-event counting, sub-row double-counting, coverage-driven pseudo-growth) that still need cleaning rules before use — see Section 5
- PSGC codes across all selected sources — need a spot-check pass before building joins, to catch renamed/merged provinces and NIR/BARMM edge cases

**Rejected, with reasons:**

| Rejected | Reason |
|---|---|
| DOH-EB Recomputed Population, Barangay-Level (2025) | Not needed — our grain is province-level, not barangay; also had a provenance concern |
| Table 2, Table 5 | National-only, no sub-national breakdown |
| Hotel Occupancy NCR | Single region only, not usable for cross-province comparison |
| Outbound tables | Measure outbound travel — out of scope |
| Inbound Update, single month | Too narrow, no trend possible |

---

## 5. Data-Quality Issues, Missing Data, Geographic/Time Mismatches, Limitations

**Time-coverage note (corrected):** the core analysis window is now **2019–2023**, matching all the province-level tables. The region-level tourism table (Table 3.63, region GVA, 2022–2024) is **not** part of the core window — it's used only as a validation check against province-summed regional totals, since we build regions by summing provinces rather than reading Table 3.63 directly.

**Circularity risk in the tourism-GDP comparison (important methodology note):** Accommodation & Food Service GVA is itself a component *inside* total GDP — so directly relating tourism-proxy growth to GDP growth partly measures GDP against a piece of itself, which will show some positive relationship almost by construction, especially where the sector is a meaningful share of the local economy. This is exactly why **the Overnight Travelers dataset is our top-priority verification item** — it's the only tourism measure that sits entirely outside the economic accounts, so it's the one genuinely independent variable available to us.
> **Fallback plan if Overnight Travelers doesn't pan out:** instead of comparing accommodation/food GVA growth to total GDP growth, compare it against growth in **"GDP minus that sector"** (the rest of the economy, excluding accommodation & food service) — this at least removes the direct double-counting. Also prefer accommodation/food's **share of GDP** as the tourism variable over its raw peso amount, since share is less mechanically tied to the total's own movement than an absolute value is.

**17-vs-18 region mismatch:** some sources use the current 18-region split (NIR separated out); others use the older 17-region grouping. Only breaks things when totaling at the regional level — province-level data is unaffected, since PSGC codes don't change per province.
> **Fix:** build one `province → region` crosswalk from current PSGC. Ignore whatever "region" column each source ships with. Match every source to PSGC by province name/code. Attach region labels only at the end, from our own crosswalk.

**BARMM/ARMM gap:** Overnight Travelers excludes these entirely. Those provinces will have GDP data but no overnight-traveler data. Still need a team decision: exclude BARMM from tourism-linked analysis, or mark tourism fields N/A (not zero — zero would wrongly imply "no tourism" rather than "no data").

**Tourism proxy limitation:** Accommodation & Food Service GVA includes non-tourist spending (business travel, local dining) — it's a stand-in for tourism activity, not a direct measure.

**HUC vs. province double-counting risk:** the per-capita-GDP table and the tourism GVA table report HUCs separately from their parent province; the GDP-by-province table reports province-only. Needs reconciliation before merging.

**New series limitation:** province-level GDP (Provincial Product Accounts) is a newly institutionalized PSA series, rolled out 2021–2025 — limits how far back we can go.

**Terminology mismatches to watch:**
- "Overnight travelers" (Overnight Travelers, accommodation check-ins) ≠ "arrivals" (Visitor Arrivals by Country and PSY 8.1, national border crossings) — not interchangeable
- **Refined further (direct testing):** "overnight travelers" itself likely counts **check-in/stay events, not unique people** — the same tourist can be counted multiple times across a trip. Must be labeled and explained as such wherever it's shown, not presented as a headcount of tourists.
- "Province," not "destination" — municipality-level rows in Overnight Travelers aren't consistently filled across years

---

## 6. What Our Data Can Support, and What We Should Not Claim

### Business Questions (finalized PR #30, refined per team review)

**Overall question:** Which provinces stand out on tourism activity, recovery, and economic linkage, and merit **prioritization for closer study**? *(reworded from "...prioritizing for tourism development" — the original promised a decision/investment output the data can't support; "prioritize for closer study" keeps the decision-relevant framing without promising returns.)*

**BQ1 — What does tourism look like now?** *Where is activity concentrated, how intense is it relative to population, and what kind of travelers visit?*
1. Which provinces have the highest and lowest overnight travelers? *(= tourism **volume**)*
2. What share do the top 5 and top 10 provinces account for?
3. How does the ranking change per 1,000 residents? *(= tourism **intensity**; surfaces places like Camiguin and Siquijor — keep volume and intensity as two distinct, separately labeled metrics, not one blended ranking, so we don't imply "highest count = best performing")*
4. What is each province's domestic, foreign, and overseas Filipino mix? — *the domestic/foreign/OFW split structurally exists at province level in Overnight Travelers (PSY 8.1 and PSY 8.2 are national-only, not the source for this); note Region II lumps overseas Filipinos into "Foreign," so that region's split isn't directly comparable — see Section 5/6 data-quality findings*

**BQ2 — How has it changed?** *Who recovered, who declined, and who might be emerging relative to 2019?*
1. How does each province's 2022+ traveler count compare with 2019? *(per PR #30's agreed comparison rule: 2019 vs. 2022+, not year-over-year growth)*
2. What % of its 2019 level has each province recovered?
3. Which small-base provinces are now above their 2019 level (emerging destinations)? — **"Emerging" definition (refined):** above 2019 level **AND** exceeds a minimum 2019 traveler base **AND** shows a meaningful absolute increase (not just recovery % alone — a province going from 10 to 15 travelers is a "50% recovery" but not meaningful)
4. Did domestic or foreign travelers recover faster, and where?

**BQ3 — How is tourism associated with the local economy?** *Do tourism intensity, tourism growth, and tourism-related economic activity tend to appear together?*
1. How do provinces compare on travelers per resident vs. GDP per capita?
2. Do provinces with more travelers have a bigger accommodation and food services share of their economy?
3. Did provinces with more traveler growth (2019 to latest) also grow faster in accommodation and food services GVA? — **Data alignment confirmed (verified directly):**
 - 2019→latest traveler data: **confirmed available**, DOT files have province-level data 2019–2024
 - 2019→latest accommodation/food GVA: **confirmed available**, Tables 3.94/95 cover province and HUC, 2019–2023
 - Consistent PSGC mapping: **not yet done** — see PSGC Crosswalk Findings below for the mechanism and open conflicts to resolve first
4. **Reworded:** How does the accommodation and food services share of regional/provincial GDP compare with national tourism-related economic indicators? *(was: "how do regional tourism shares compare with the national share from the PTSA" — PTSA measures the broader tourism economy — accommodation, transport, food services, shopping — while our GVA proxy only covers accommodation & food service. Directly equating the two would overclaim. State explicitly in methodology: accommodation & food service GVA is a proxy for tourism-related local economic activity, not a pure tourism measure, and it includes local-resident spending, so it isn't directly equivalent to PTSA's tourism share of GDP.)*

**Also agreed:**
- Province level, joined by PSGC code; regions are totals of their provinces
- **Geography normalization order (refined):** normalize province identities first → assign a consistent PSGC mapping → *then* generate regional totals. Never group by whichever region label a source happened to ship with, or apparent regional growth could just reflect classification changes, not real tourism change.
- **Document every remapping decision explicitly** — e.g., "We mapped all Negros Occidental observations, including 2019 observations, to NIR when creating comparable regional totals." Include a standing line in the doc: *"Historical observations are normalized to a consistent province-level PSGC geography before regional aggregation."*
- **Comparison rule (settled per PR #30's Shared Scope and Definitions):** 2019 is the fixed pre-pandemic baseline, compared against **2022–2023** as the post-pandemic period — i.e., **2019 vs. 2022+**, not year-over-year growth. This is now the single standard rule for all BQs, resolving the earlier open question of whether BQ1 should be allowed to run ahead to its most recent available year (2024) independently of BQ3's ceiling — it should not; 2022+ is the agreed comparison point across the board. Table 3.63 (region GVA, 2022–2024) remains validation-only, not a core input (see Section 2).
- An earlier draft fourth question becomes a screening output built from BQ1–3, rather than a separate BQ
- Results show associations, not causation; no ROI/investment claims

### PSGC Crosswalk Findings (verified against PSGC Q2 2026 file; expanded per a full cross-source code check)

**The mechanism exists:** the PSGC file has a **"Correspondence Code" column** carrying each area's old code, so this can be used directly as the old→new crosswalk — no need to build one from scratch by hand.

**Negros Island Region (NIR):**
- Negros Occidental: old code `064500000` → new code `1804500000`
- Negros Oriental: old code `074600000` → new code `1804600000`
- **Rule:** use the Correspondence Code column to crosswalk both, for every year including 2019 (i.e., even pre-NIR-creation years get remapped to NIR for consistency)

**Sulu:** current PSGC reclassifies Sulu under Region IX (`0906600000`), per Supreme Court ruling and EO 91, transitioning from its historical BARMM correspondence code (`156600000`). **Standardize to `0906600000`** and crosswalk historical BARMM-tagged records through `156600000`.

**Cotabato City:** current PSGC codes it as `1908703000` (City of Cotabato, ICC) under Maguindanao del Norte, within BARMM. DOT files instead place it under Region XII in 2019, zero-fill it 2020–2022, and drop it entirely 2023–2024. **Remap to BARMM** via its 10-digit code, using legacy correspondence code `129804000` to crosswalk the historical DOT records. **Data-quality note:** the zero-fill years (2020–2022) need to be treated as missing/unavailable, not true zero — same rule as the general Missing Data Rule below, don't let this one quietly read as "no tourism."

**HUC double-counting:** parent-province rows in the PSA GDP/GVA tables and Population Table B footnote "Excludes HUC," while HUCs appear as their own separate rows — summing both would double-count. **Fix:** keep HUCs as separate rows, and add a `parent_province_code` column so they can be correctly included in (or excluded from) a province-level rollup depending on which total is needed.

**Boracay's actual PSGC mapping:** DOT lists "Boracay" as its own standalone row instead of using its official PSGC municipality name. Boracay is part of **Malay, Aklan**. **Fix:** map the "Boracay" row to Malay's code (`0600412000`). For a true Aklan provincial total in 2019–2020 specifically (before the reporting split), explicitly sum the Aklan row *and* the Boracay row — don't treat them as already combined.

**Zamboanga City:** listed as its own standalone row under Region IX every year, with Basilan province absent from the same files. **Fix:** parse as a standalone city row and map directly to `0931700000` — no merged-string splitting needed (unlike some other combined-unit rows flagged elsewhere in this doc).

**Makati City & Taguig City (NCR):** both are separate HUC rows in PSGC and in DOT reporting. The 10 EMBO (Enlisted Men's Barangay Overrun) barangays' population shifted between these two cities in census data, per Supreme Court ruling G.R. 235316, but historical GDP/GVA tables' area coverage may not reflect that same shift. **Fix:** document this spatial variance explicitly, and aggregate any per-capita metrics affected by it at the **NCR level** rather than the Makati/Taguig city level, where the boundary shift makes a clean city-level comparison unreliable across years.

**Isabela City naming collision:** coded under Region IX (`0990101000`, legacy `099701000`) — PSGC notes its geographic location is in Basilan, but DOT retains it in Region IX every year (as "Isabela City" 2019–2022, then "Isabela City de Basilan" 2023–2024). **Risk:** "Isabela" also refers to a province (`0203100000`) and a separate municipality in Negros Occidental (`1804514000`) — a name-only match would misfile this city under the wrong entity. **Fix:** match strictly by PSGC code, never by string name alone, and build a small string crosswalk specifically to catch the "Isabela City de Basilan" naming variant used from 2023 onward.

### Known DOT Traveler Data Quality Issues

**"overnight travelers" is not the same as "unique visitors":**
DOT doesn't define how travelers are counted, and the same person may be counted more than once (e.g., multiple hotel check-ins during one trip). Evidence: 2024 foreign travelers in Overnight Travelers (7.63M) *exceeds* actual foreign visitor arrivals from Visitor Arrivals by Country and PSY 8.1 (5.44M by residence, 5.93M by citizenship); 2021 shows 488,588 vs. only 146,098 actual arrivals. **This means Overnight Travelers measures check-in/stay events, not a headcount of unique people** — it needs to be defined and labeled that way everywhere it's used (dashboard, README, methodology), not presented as "number of tourists."

**Sub-rows double-count if summed carelessly:** destination sub-rows (e.g., Boracay inside Aklan, Legazpi inside Albay) sit *inside* their parent province's row — summing all rows in a province naively double-counts. Extraction logic must treat sub-rows as already included in the parent, not additive.

**Reporting coverage changes drastically year to year:** NCR is absent 2000–2005, then swings 1.87M (2014) → 0.49M (2016) → 3.04M (2019) → 7.35M (2024). National grand totals go 9.1M (2000) → 56.8M (2019) → 11.9M (2020, pandemic) → 63.9M (2024) — **partly because more places started reporting over time, not purely real growth.** Any "province X grew" claim needs to rule out "province X just started reporting" as the real cause. Region III and XII show totals-only for 2000–2002; many provinces are blank in other years (see Missing Data Rule below).

**Boracay / Aklan reporting inconsistency across years — needs an explicit team decision, same as Sulu/Cotabato:**
- 2019–2020: Boracay reported as its own row; Aklan's row excludes it
- 2021–2022: Aklan's total *equals* Boracay's, because the other towns are blank
- 2023–2024: Aklan = Boracay + a few towns
- **Confirmed by direct testing:** Boracay switched to counting via the Caticlan jetty port starting 2022 — so Aklan isn't comparable before/after that switch.
- **Decision needed:** treat Boracay + Aklan as one combined unit across all years for comparability, or exclude Boracay-specific analysis pre-2022. Left as-is, this breaks province-level comparability for BQ2 (2019 vs. latest).

**Region II lumps overseas Filipinos into "Foreign":** breaks the domestic/foreign/OFW split (BQ1.4) specifically for Region II — that region's "Foreign" figure isn't comparable to every other region's.

**Region IV split into IV-A and IV-B starting 2008:** another region-boundary change over time, same category of issue as the NIR/BARMM crosswalk problems already flagged — needs to go through the same province→region normalization process, not be read directly from whichever label a given year's file uses.

**Combined/non-standard reporting units:** some location names are combined units that don't map to a single PSGC entity (e.g., "Zamboanga City/Basilan Prov."). These need manual handling in the crosswalk, not an automatic name match.

**Zamboanga Sibugay — suspected data anomaly, needs spot-check against source PDF:**
- Domestic traveler count is flat/identical across 2019, 2021, and 2022
- Then jumps from 8,677 (2023) to 197,053 (2024) — a ~22x increase with no comparable jump elsewhere
- Flag for quarantine/manual verification before including in any recovery or growth calculation.

**Other suspicious province-year values flagged during testing — quarantine and verify before use:**
- Quezon 2000: 1.73M domestic (implausibly high)
- Cavite 2001: 595K foreign; Cavite 2010: +1,977% single-year jump
- Laguna 2002: 1.16M foreign
- Mindoro Oriental 2005–2007: ~3.7M domestic
- Mountain Province 2000: Overseas/Domestic columns look possibly swapped
**Missing travelers must never become 0 travelers.** A blank record must be preserved as "insufficient/unavailable data," not silently filled with zero — otherwise a province with no data would visually read as "no tourism," which isn't the same claim and isn't necessarily true. Distinguish explicitly between:
- **True zero** (confirmed no travelers recorded)
- **Missing record** (province just isn't in that year's file)
- **Suppressed data** (value withheld by the source, e.g., for privacy/small-sample reasons)
- **Incompatible geographic record** (e.g., a combined city/province label that doesn't cleanly map to a single PSGC code)

### Can do / Can't do, per the finalized BQs

| Can do | Can't do (yet) |
|---|---|
| Province-level comparison, rolled up to region via PSGC (normalized first, aggregated second) | MunCity-level comparison |
| 2019–2023 core window, with latest-common-year rule per BQ | Anything needing data past each BQ's actual common-year ceiling |
| Tourism measured via overnight travelers (Overnight Travelers, tested — use for relative comparison, not absolute headcounts) or GVA proxy as fallback | Treating Overnight Travelers as a unique-visitor headcount (it counts check-in/stay events, confirmed to include repeat counting) |
| GDP, per capita GDP, population by province (population 2019–2023 gap-year still pending a resolution method) | Investment amounts, ROI, capital spent per province |
| Association / correlation language; identifying which provinces "stand out" | Causal claims ("tourism drives growth"); "prioritize for investment" claims |
| All provinces except BARMM for tourism-linked questions | BARMM provinces for anything needing overnight-traveler data |
| Accommodation & food service GVA as a **proxy** for tourism-related economic activity | Treating GVA growth vs. total GDP growth as a clean, non-circular test (GVA is part of GDP) — use GDP-minus-sector and share-of-GDP framing instead if Overnight Travelers fails |

### Explicitly out of scope / not to be claimed
- Municipality/city-level analysis (stretch goal only)
- "Return on investment" or causal economic-impact claims
- Claims about "unmet development needs" (per PR #30's Shared Scope and Definitions — findings describe distributions, changes, and associations only)
- Data before 2019 for the core tourism-economy comparison
- Outbound tourism (not relevant to this project's direction)
- Any causal language — all findings are association/pattern-based only

### Key assumptions underlying all of the above
- Overnight Travelers counts are check-in/stay events, not unique-visitor headcounts (confirmed during testing) — used for relative comparison across provinces/years, not as an absolute population-style figure
- GVA remains our economic-footprint proxy for tourism regardless of Overnight Travelers' status, since the two measure different things (economic value vs. traveler activity)
- Province PSGC code is the stable identifier; a source's own "region" label is never trusted directly
- Correlation ≠ causation — other factors (infrastructure, existing development) may explain both tourism and GDP independently
- BARMM provinces will have GDP but no tourism-demand data — handling still pending a team decision
- Multi-year DOT trends may partly reflect more locations reporting over time, not purely real tourism growth — this caveat must accompany any long-run trend claim

---

## Still Open / Needs Someone To Do It

**Resolved this round:**
- ~~Confirm the PSGC 2024-population claim~~ — **done**, the PSGC Publication Datafile confirmed to carry population counts
- ~~Open and test Overnight Travelers~~ — **done**, opened and tested; domestic/foreign/OFW split structurally exists per province, but see new items below — the bigger issue is data quality, not availability
- ~~Decide whether BQ1's "latest year" should be capped to match BQ3~~ — **done, per PR #30's Shared Scope and Definitions**: standard comparison is 2019 vs. 2022+ across all BQs, no independent run-ahead

**Newly surfaced (highest priority):**
1. Decide how to handle Overnight Travelers' core measurement problem: it counts check-in/stay events, not unique visitors (2024 foreign count exceeds actual foreign arrivals). Options: use it only for relative comparison (which provinces/years are higher or lower), not absolute headcounts; or fall back further toward the GVA proxy where the discrepancy matters most
2. Build the sub-row de-duplication rule so Boracay/Legazpi-style destination rows aren't double-counted when summed into their province
3. Decide how to treat years/regions with likely coverage-driven growth (more places reporting ≠ more real tourism) — at minimum, flag this caveat wherever multi-year DOT trends are shown
4. Quarantine and manually verify the suspicious province-year values flagged during testing (Quezon 2000, Cavite 2001/2010, Laguna 2002, Mindoro Oriental 2005–07, Mountain Province 2000, Zamboanga Sibugay 2023→2024) before using them in any calculation
5. Decide Region II's OFW-lumped-into-Foreign handling (exclude that split for Region II, or note it as non-comparable)
6. Add Region IV-A/IV-B (2008 split) to the same province→region normalization process as NIR/BARMM


**Carried over from before:**
7. Build the PSGC crosswalk using the Correspondence Code column
8. Decide BARMM handling for provinces missing from DOT files entirely (exclude vs. mark N/A)
9. Fill the population 2019–2023 year-gap: use the mid-year population dataset (province level, 2020–2025, already in inventory) for 2021–2023 after applying the PSGC crosswalk; for 2019 specifically, back it out from GDP ÷ per capita GDP or interpolate from census counts
10. Decide the exact "province" definition (province + HUCs within it, or otherwise) and how NCR is treated, then apply consistently across every source