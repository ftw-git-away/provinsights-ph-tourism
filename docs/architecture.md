# Architecture and open choices

**Status:** Provisional. Source discovery is underway; this describes an intended direction, not a deployed system.

## Intended data flow

```text
Verified public sources
        ↓
Ingestion with retrieval metadata
        ↓
Raw landing / Bronze
        ↓
Standardized and quality-checked data / Silver
        ↓
Analytics-ready Gold marts
        ↓
Read-only query/access layer
        ↓
Public Tuklas Pinas website
```

Databricks is the planned environment for ingestion and data transformations. The intended medallion layers are a starting design; their final scope should match the selected sources and capstone deliverables.

GitHub stores code, notebook exports or source files, documentation, CI configuration, issues, and review history. It is not the database or public query service. Hosting for an anonymous public site and API/query layer has not been selected.

## Decisions still open

Do not finalize these until source feasibility and the project MVP are agreed:

- Which exact DOT, PSA, and/or PSGC datasets to use
- Geographic unit, coverage, and time window
- How geographic identifiers and names will be standardized
- Which layers and tables are needed for the chosen question
- Data-quality rules and what should block publication
- Whether the public experience reads static published files, a read-only API, or another approved service
- Public hosting, refresh cadence, and operating responsibilities

## Current boundaries

The repository does not yet contain implemented ingestion, transformations, marts, dashboard code, or a deployment. See the [README](../README.md) for the current status and [source feasibility guidance](data-sources.md) for the evidence required before design decisions.
