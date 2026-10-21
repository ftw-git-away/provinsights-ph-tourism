# Notebooks

Pipeline notebooks, one folder per layer. The job in [`resources/jobs/tourism_pipeline.yml`](../resources/jobs/tourism_pipeline.yml) runs them in this order; see [`resources/README.md`](../resources/README.md) for the task list.

| Folder | Layer | Notebooks | Writes to schema(s) in `tuklas_dev` |
| --- | --- | --- | --- |
| `01_ingestion_bronze/` | Ingestion and Bronze | `00_ingestion_setup`, `01_ingest_psa`, `02_ingest_psgc`, `03_ingest_dot`, `04_ingest_psa_ds18_pdf` | `01_ingestion` (run metadata), `02_bronze` (raw source data) |
| `02_silver/` | Silver | `00_silver_setup`, `01_silver_geography`, `02_silver_dot`, `03_silver_psa_economy`, `04_silver_population` | `03_silver` |
| `03_gold/` | Gold (star schema) | `00_gold_setup`, `01_gold_dim_province`, `02_gold_dim_year`, `03_gold_fact_province_year`, `04_gold_run_evidence` | `04_gold` |
| `04_analytics/` | Analytics | `01_build_analytics`, `02_analytics_validation`, `03_analytics_run_evidence` | `05_analytics` |
| `99_maintenance/` | Maintenance | One-off notebooks, run by hand | Not part of the job |

Data-quality results from every layer go to `06_data_quality.dq_results`.

## Conventions

- Each notebook starts with a markdown cell explaining what it does.
- `CATALOG` is always `tuklas_dev`.
- Data-quality checks run inside the notebook that builds the table, before it is written. A failed `BLOCK` check fails the task and stops every task after it ([rules](../docs/data-quality-rules.md)).
- No credentials in notebooks. CI checks this (see [`tests/README.md`](../tests/README.md)).
