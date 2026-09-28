# Source discovery and feasibility

Source investigation is the project’s current work. Candidate sources are not selected inputs until the team checks access, coverage, definitions, terms, quality, and whether they can support an agreed question.

## Shared inventory

Record one row per specific dataset in the [GitAway Source Inventory and Scope Feasibility sheet](https://docs.google.com/spreadsheets/d/18tTQHJLcJrIFVfNzgvT97ZMM6PfJNnAL/edit?gid=1004909730#gid=1004909730).

Use the same sheet fields for each candidate: publisher and dataset name; official URL; what it measures; geographic level and coverage; time coverage and granularity; format and access method; metadata/methodology; observed data quality; attribution/terms; limitations; potential use; feasibility; and evidence.

## Evidence to collect

For each source:

1. Open the official source page and locate the actual dataset, download, API, or data portal entry.
2. Retrieve a small sample or inspect a representative published file. Record when and how it was accessed.
3. Note field names, types, units, identifiers, missing values, duplicates, date range, and geographic granularity where observable.
4. Check the source documentation for definitions, revisions, methodology, licensing, attribution, and update cadence.
5. Test whether the intended Databricks environment can access the source if an automated ingestion path is being considered.
6. Record evidence links and distinguish observed facts from assumptions.

Do not upload full datasets or credentials to GitHub. Check source terms before storing or redistributing any sample.

## Feasibility status

Use consistent values in the sheet:

- **Unverified** — not enough evidence yet.
- **Feasible** — relevant data is accessible and appears to cover the needed geography/time range with usable definitions and terms.
- **Feasible with limitations** — usable only with documented caveats or manual steps.
- **Not feasible** — a material constraint prevents responsible use for this scope.

Do not select a source based on a working landing-page link alone. A selection should include sample evidence and a short explanation of the source’s fit and limitations.

## Candidate publishers

The slide and project brief identify DOT tourism statistics / Tourism Satellite Account, PSA population and regional GDP/GRDP, and PSGC as candidates. These are leads to investigate, not a confirmed source list. Add the specific dataset and official location after verification.

## Selection gate

After the inventory is filled, compare candidates against one chosen project question. The team should agree on the MVP sources, geographic unit, time window, and limitations before final schema design. Record unresolved or rejected sources and the evidence behind the decision.
