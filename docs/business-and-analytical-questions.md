# Business and Analytical Questions

> **Status: Draft for Team Review**
>
> This document is a working proposal and is **not yet final**. The business and analytical questions below are open for team review, revision, addition, or removal.
>
> The final set will be determined after the team reviews the proposed questions and verifies the coverage, definitions, granularity, and quality of the available data sources.

## Purpose

To gather team feedback and reach agreement on **3-4 core business questions** before finalizing the project's analytics scope, data requirements, metrics, and analytical models.

Team members are encouraged to:

- Comment on questions that should be revised, combined, removed, or added
- Review whether each analytical question directly supports its business question
- Flag questions that may not be supported by the available data
- Suggest clearer wording or additional analytical questions
- Identify data limitations that may affect answerability

These questions should be treated as **provisional** until the team completes source verification and agrees on the final scope.

## Important Measure Definition

For the initial analysis, **tourism activity** means the number of reported overnight travelers in accommodation establishments, as recorded in Department of Tourism (DOT) regional reports.

This measure is a practical indicator of reported accommodation activity. It does not represent every tourist, day visitor, trip, or tourism-related transaction in a destination.

## Business Problem 1: Tourism activity differs across destinations

**Business question:**  
Which destinations have the highest and lowest reported tourism activity?

**Analytical questions:**

- What is the reported number of overnight travelers for each destination and period?
- How do destinations rank by reported overnight travelers?
- How has reported tourism activity changed over time for each destination?

**Data needed:**

- DOT reported overnight travelers
- Destination name and geographic level
- Reporting period
- Traveler category, where available (domestic, foreign, and overseas Filipino)

**Answerability:**  
Likely answerable for the geographic levels and periods covered by DOT’s regional reports. Confirm that destination names, geographic boundaries, and reporting periods are comparable before ranking them.

## Business Problem 2: Tourism activity changes over time

**Business question:**  
Which destinations are growing or declining in reported tourism activity?

**Analytical questions:**

- What is the year-over-year change in reported overnight travelers by destination?
- Which destinations show sustained growth or decline across comparable periods?
- Which destinations show unusually large changes compared with their previous periods?

**Data needed:**

- Comparable DOT traveler counts across multiple years
- Destination and reporting-period fields
- Notes on missing, revised, or provisional data

**Answerability:**  
Answerable where DOT reports provide comparable time series. Changes and unusual patterns can be identified, but I don't think the data alone cannot explain their causes (except for obvious cases like during the pandemic).

## Business Problem 3: Tourism activity and local economic conditions may move together

**Business question:**  
How does reported tourism activity relate to local economic conditions?

**Analytical questions:**

- How does reported tourism activity compare with Gross Regional Domestic Product (GRDP) across regions?
- Do tourism and economic indicators move in similar or different directions over time?
- Which regions show different patterns between tourism activity and GRDP?

**Data needed:**

- DOT traveler counts at the regional level
- Philippine Statistics Authority (PSA) GRDP by region
- Periods and geographic definitions that align across both sources

**Answerability:**  
Partly answerable at the regional level, provided the time periods and geographic levels align. Treat the results as comparisons or associations; they do not show that tourism caused economic growth (_correlation doesn't mean causation_), or vice versa. National tourism accounts should not be used to claim local economic impacts.

## Business Problem 4: Some destinations may warrant further investigation

**Business question:**  
Which destinations show tourism patterns that may warrant further planning or investigation?

**Analytical questions:**

- Which destinations have low reported tourism activity compared with comparable destinations?
- Which destinations show rapid growth that may warrant further study?
- Which destinations have tourism trends that differ from their population or economic trends?

**Data needed:**

- DOT traveler counts
- Comparable destination groupings
- PSA population data and, where geographic levels align, economic indicators
- Additional evidence for any planning or capacity conclusions

**Answerability:**  
Partly answerable as a screening exercise. The data can flag patterns for follow-up, but cannot establish that a destination is underserved or needs investment, infrastructure, or capacity because those conclusions require additional evidence, such as accommodation capacity, infrastructure, environmental conditions, and local plans.

## Our Source Assessment

- [GitAway - Scope and Source Feasibility](https://docs.google.com/spreadsheets/d/18tTQHJLcJrIFVfNzgvT97ZMM6PfJNnAL/edit?usp=sharing&ouid=109728975218616355743&rtpof=true&sd=true)

## Initial Scope

The following scope is also **subject to team review and source verification**.

- Start with Business Problems 1 and 2 using DOT reported overnight travelers at a geographic level and time range confirmed through source assessment.
- Consider Business Problem 3 only where DOT and PSA geographic and reporting periods can be aligned.
- Treat Business Problem 4 as exploratory screening rather than a basis for recommending specific interventions.

The team may expand, narrow, combine, or remove these questions based on **feedback** and **source availability**.
