# Modular Source Code

This folder contains the pipeline logic as small, reviewable code files.

Each SQL file should have **one clear responsibility**, usually one table or view, to make changes easier to review, test, and maintain.

```text
src/
├── 01_ingestion/    # Acquire and prepare data from external sources
├── 02_bronze/       # Raw source tables and controlled loads
├── 03_silver/       # Cleaned and standardized tables
├── 04_gold/         # Analytics-ready dimensions and facts
├── 05_analytics/    # Business metrics and insight views
└── 06_data_quality/ # Data-quality and monitoring views
```

## How the folders work

* **`src/`** - Main source code. This is where pipeline logic is developed and reviewed.
* **`notebooks/`** - Databricks notebooks that run the pipeline using the approved logic from `src/`.
* **`tests/`** - Tests that verify schema, transformations, data quality, and pipeline behavior.
* **`docs/`** - Architecture, source, data-model, and other project documentation.

The overall flow is:

```text
Source
  ↓
Ingestion
  ↓
Bronze
  ↓
Silver
  ↓
Gold
  ↓
Analytics
  ↓
Dashboard/Public Experience
```

## Change Workflow

When changing pipeline logic:

1. **Update the corresponding Databricks notebook** with the approved logic. 
2. **Update the SQL in `src/`.**
3. **Update or add tests** when the change affects schema, transformations, data quality, or rerun behavior.
4. **Update relevant documentation** if the architecture, data model, or behavior changes.
5. **Run CI and the relevant tests** before opening or merging the pull request.
6. **Run the pipeline and verify the results** in Databricks.

### Keep implementations aligned

If the same logic exists in both `src/` and a Databricks notebook, they must represent the **same approved implementation**.

```text
src/ SQL
   ↕
Databricks notebook
   ↓
Tests
   ↓
CI
   ↓
Deploy
   ↓
Run & Verify
```

CI should catch cases where the source SQL and its corresponding notebook become inconsistent.

## Naming and Organization

Numeric prefixes indicate the expected dependency order:

```text
01_ingestion
02_bronze
03_silver
04_gold
05_analytics
06_data_quality
```

Within a layer, keep files focused and avoid putting unrelated transformations into one large code/sql file.

**Goal:** A new data engineer should be able to open this folder, identify where a change belongs, understand what owns the logic, and safely trace that change from source code through testing and execution.
