# Tests and Validation

Tests and validation are responsible for **checking that the resulting data is correct and meets the project's rules**.

## Validation by Pipeline Layer

Validation is organized by the layer or component being checked.

| Scope      | Validation                                                  |
| ---------- | ----------------------------------------------------------- |
| Ingestion  | Source availability, file/API response, required metadata   |
| Bronze     | Schema, record ingestion, duplicates, source tracking       |
| Silver     | Data types, required fields, transformations, relationships |
| Gold       | Table grain, keys, joins, measures, business rules          |
| Analytics  | Metrics, calculations, expected outputs                     |
| End-to-end | Complete pipeline and final data-quality checks             |


## Validation Principles

### 1. Validate each layer

A problem should be detected as close as possible to where it is introduced.

```text
Source
  ↓
Ingestion ──→ Validate
  ↓
Bronze ─────→ Validate
  ↓
Silver ─────→ Validate
  ↓
Gold ───────→ Validate
  ↓
Analytics ──→ Validate
  ↓
End-to-End → Validate
```

### 2. Separate creation from validation

Do not hide important quality checks inside transformation logic to make it easier to understand **what the pipeline does** and **how we know it worked**.


For example:

```text
03_silver/
└── tourism.py              # Creates Silver table

tests/
└── test_tourism.py         # Checks Silver table
```


### 3. Test important behavior

Tests should cover areas such as:

* Schema and data types
* Required fields
* Primary/business keys
* Duplicate records
* Null or invalid values
* Source-to-target mappings
* Geographic relationships
* Time periods
* Business rules
* Rerun/idempotency behavior
* Final analytical outputs


Tests requiring Databricks data or external services can be executed in the appropriate development or integration environment.

## End-to-End Quality Gate

The final pipeline should have a consolidated quality check that verifies the important requirements for the completed data product. A failed critical validation should cause the pipeline to fail.

The specific framework used for the end-to-end quality gate will be documented once selected.

## Goal

Tests and validation should provide evidence that:

> **The pipeline ran, the data has the expected structure and quality, and the resulting outputs can be trusted for the project's intended use.**
