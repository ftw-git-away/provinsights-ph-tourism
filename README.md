# Tuklas Pinas Data Platform

GitAway's FTW Batch 12 capstone: a proposed public-facing platform for exploring Philippine tourism and local-economy information.

**Project status:** Source discovery and feasibility review. The repository currently contains planning documents and scaffold folders; data sources, schemas, pipelines, marts, and the public experience are not yet implemented.

## Why this project

Tourism, economic, geographic, and population information is published by different agencies, at different geographic levels and reporting periods. Tuklas Pinas aims to make selected, compatible information easier to understand through documented data products and a public exploration experience.

Questions the team is investigating include:

- Which destinations show tourism activity in the sources we can verify?
- Where are tourism opportunities concentrated?
- How do tourism indicators relate to available local economic, geographic, or population measures?
- What comparisons are supportable given the source coverage and definitions?

These are research questions, not claims the current repository can answer yet.

## Current source-discovery work

The team is inspecting candidate sources before choosing the MVP or finalizing schemas. The candidates include:

- [Department of Tourism data](https://www.tourism.gov.ph/dot/data/)
- Philippine Statistics Authority datasets, including population, Tourism Satellite Account, and regional GDP/GRDP data
- Philippine Standard Geographic Code (PSGC)

The candidate list is not a commitment to use every source. Access, fields, geography, time coverage, definitions, attribution, and joinability must be checked first.

Record findings in the team's [Source Inventory and Scope Feasibility sheet](https://docs.google.com/spreadsheets/d/18tTQHJLcJrIFVfNzgvT97ZMM6PfJNnAL/edit?gid=1004909730#gid=1004909730). See [source review guidance](docs/data-sources.md).

## Proposed architecture

The intended flow is still provisional and depends on source feasibility and the agreed MVP:

```text
Verified public sources
        ↓
Ingestion and raw preservation
        ↓
Cleaning and standardization
        ↓
Analytics-ready data marts
        ↓
Read-only access layer
        ↓
Public Tuklas Pinas experience
```

Databricks is the planned environment for data engineering and Gold marts. Hosting and access for the public query experience are not selected. GitHub is the source of truth for code, documentation, issues, and review history; it does not itself host Databricks data or a query service.

See [architecture and open decisions](docs/architecture.md).

## Repository status and structure

The repository is being scaffolded. Current tracked content is mainly documentation and placeholder files; there are no implemented pipelines or dashboard components yet.

```text
.github/
  workflows/       GitHub Actions workflow files (CI is not implemented yet)
dashboard/         planned public-facing experience; no application code yet
docs/
  architecture.md  proposed flow and decisions that still need confirmation
  data-sources.md  source discovery and feasibility review guidance
  runbook.md       current run status and future runbook requirements
notebooks/         planned Databricks notebooks; none committed yet
resources/jobs/    planned Databricks job configuration; not implemented
src/
  01-ingestion/    planned source acquisition
  02-bronze/       planned raw layer
  03-silver/       planned standardized layer
  04-gold/         planned analytics marts
  05-analytics/    planned metrics and analytical outputs
  06-data-quality/ planned quality reporting
tests/             validation guidance; automated tests not implemented yet
```

Folders describe intended organization, not completed deliverables. Review [the current run status](docs/runbook.md) before trying to execute anything.

## How GitAway works

Our first gate is source feasibility: inspect candidate data and record evidence before fixing the MVP, final schema, or join plan. Track tasks and blockers as GitHub Issues, progress and dates on the GitHub Project board, source evidence in the shared sheet, and approved project decisions in repository docs.

Read the [GitAway working agreement](team-workflow.md) for our source review, parallel work, issue ownership, branch/PR review, data handling, and capstone evidence rules. It is written for this project and can be revised by the team as we learn more. The [runbook](docs/runbook.md) explains what can currently be run.

## Team and target checkpoints

GitAway: Cole, Nella, Cha, Gab, and Haze.

- **September 30, 2026:** source feasibility and scope recommendation
- **October 3, 2026:** schema design informed by source findings
- **October 10, 2026:** Gold marts
- **October 17, 2026:** analytics/dashboard and certification exam
- **October 24, 2026:** capstone presentation and defense

These are planning targets. The team wants to finish earlier where feasible. The GitHub Project board carries the current dates and task status.

## Handoff status

**Not yet ready** for independent engineering handoff. The project has an overview and planning scaffold, but no selected/verified dataset set, complete setup instructions, runnable pipeline, implemented validation, or public application. Update this status only when a newcomer can set up, run, inspect checks, and modify the working project from the repository documentation.
