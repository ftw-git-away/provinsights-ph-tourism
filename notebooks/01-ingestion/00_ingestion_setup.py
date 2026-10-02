# Databricks notebook source
# DBTITLE 1,Ingestion Control Setup
# MAGIC %md
# MAGIC # Ingestion Control Setup
# MAGIC
# MAGIC This notebook creates the persistent Delta control tables used to monitor and audit source ingestion for the Tuklas Pinas data pipeline.
# MAGIC
# MAGIC The `01_ingestion` schema stores pipeline-run metadata, source-file and source-table processing results, and ingestion errors.
# MAGIC
# MAGIC Actual source data is written separately to the Bronze layer under `tuklas_dev`.`02_bronze`.
# MAGIC
# MAGIC The control tables created here are designed to support:
# MAGIC
# MAGIC * `01_ingest_psa`
# MAGIC * `02_ingest_psgc`
# MAGIC * `03_ingest_dot`

# COMMAND ----------

# DBTITLE 1,Step 1 — Configuration
# MAGIC %md
# MAGIC ### Step 1 — Configuration
# MAGIC
# MAGIC Define the Unity Catalog identifiers and a helper for fully qualified ingestion-table names.
# MAGIC
# MAGIC The `01_ingestion` schema already exists and must **not** be dropped or recreated.

# COMMAND ----------

# DBTITLE 1,Configuration
CATALOG = "tuklas_dev"
INGESTION_SCHEMA = "01_ingestion"
BRONZE_SCHEMA = "02_bronze"

def ingestion_table(table_name):
    """Return the fully qualified, backtick-quoted identifier for an ingestion control table."""
    return f"`{CATALOG}`.`{INGESTION_SCHEMA}`.`{table_name}`"

# Verify that the ingestion schema already exists (do NOT create or drop it)
schema_exists = spark.sql(
    f"SELECT 1 FROM `{CATALOG}`.information_schema.schemata "
    f"WHERE catalog_name = '{CATALOG}' AND schema_name = '{INGESTION_SCHEMA}'"
).count()

assert schema_exists == 1, (
    f"Schema `{CATALOG}`.`{INGESTION_SCHEMA}` does not exist. "
    "Create it manually before running this notebook."
)
print(f"✓ Schema `{CATALOG}`.`{INGESTION_SCHEMA}` verified.")
print(f"  Bronze schema: `{CATALOG}`.`{BRONZE_SCHEMA}` (for reference only — not modified here)")

# COMMAND ----------

# DBTITLE 1,Table 1 — ingestion_run_log
# MAGIC %md
# MAGIC ### Table 1 — `ingestion_run_log`
# MAGIC
# MAGIC **Purpose:** One row represents one execution of an ingestion notebook.
# MAGIC
# MAGIC This table summarizes the **entire** notebook run — not individual datasets. A single PSA execution may process DS\_01 (10 Bronze tables), DS\_02 (3 tables), PSY/DS\_08–17, DS\_18 Excel, DS\_18 PDF, and multiple CSV files; all of that is captured in one row here.
# MAGIC
# MAGIC | Column | Type | Description |
# MAGIC | --- | --- | --- |
# MAGIC | `run_id` | STRING | Unique run identifier |
# MAGIC | `notebook_name` | STRING | e.g. `01_ingest_psa` |
# MAGIC | `source_system` | STRING | e.g. `PSA` |
# MAGIC | `source_folder` | STRING | Google Drive folder URL |
# MAGIC | `started_at` | TIMESTAMP | Run start time |
# MAGIC | `completed_at` | TIMESTAMP | Run end time |
# MAGIC | `files_discovered` | BIGINT | Files found in source |
# MAGIC | `files_ingested` | BIGINT | Files successfully ingested |
# MAGIC | `files_skipped` | BIGINT | Files intentionally skipped |
# MAGIC | `files_failed` | BIGINT | Files that failed |
# MAGIC | `tables_created` | BIGINT | Bronze tables created/refreshed |
# MAGIC | `status` | STRING | `STARTED`, `SUCCESS`, `PARTIAL_SUCCESS`, `FAILED` |
# MAGIC | `notes` | STRING | Free-text notes |
# MAGIC
# MAGIC No restrictive `CHECK` constraints are added to avoid compatibility issues in Databricks Free Edition.

# COMMAND ----------

# DBTITLE 1,Create + validate ingestion_run_log
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {ingestion_table('ingestion_run_log')} (
    run_id            STRING,
    notebook_name     STRING,
    source_system     STRING,
    source_folder     STRING,
    started_at        TIMESTAMP,
    completed_at      TIMESTAMP,
    files_discovered  BIGINT,
    files_ingested    BIGINT,
    files_skipped     BIGINT,
    files_failed      BIGINT,
    tables_created    BIGINT,
    status            STRING,
    notes             STRING
) USING DELTA
""")

# ── Validate ──
run_log_df = spark.table(ingestion_table("ingestion_run_log"))
print(f"✓ Table {ingestion_table('ingestion_run_log')} created / verified.")
print(f"Rows: {run_log_df.count()}")
run_log_df.printSchema()
display(run_log_df.limit(10))

# COMMAND ----------

# DBTITLE 1,Table 2 — file_manifest
# MAGIC %md
# MAGIC ### Table 2 — `file_manifest`
# MAGIC
# MAGIC This is the most important control table. It stores the result of processing **each logical source/output table** during an ingestion run.
# MAGIC
# MAGIC One manifest row = one logical ingestion output. One physical file may produce **multiple** Bronze tables, so `file_manifest` can have many rows for the same `source_file`, differentiated by `source_sheet` and `destination_table`.
# MAGIC
# MAGIC **Examples:**
# MAGIC
# MAGIC * `DS_01_PSA_PTSA_Statistical_Tables_2000_2025.xlsx` → 10 rows (one per sheet, `psa_ds_01_table_01` through `psa_ds_01_table_10`)
# MAGIC * `DS_02_PSA_Tourism_Statistical_Classification_2025.xlsx` → 3 rows (`psa_ds_02_metadata`, `psa_ds_02_tourism_industries`, `psa_ds_02_tourism_products`)
# MAGIC * `DS_08_to_DS_17_PSA_PSY_Tables_8_1_to_8_10.xlsx` → 10 rows (T8\_1→DS\_08→`psa_ds_08` through T8\_10→DS\_17→`psa_ds_17`)
# MAGIC * DS\_18 Excel and PDF share `source_dataset_id = DS_18` but produce different Bronze tables (`psa_ds_18` vs `psa_ds_18_pdf`)
# MAGIC
# MAGIC The combination of `run_id` + `source_dataset_id` + `source_file` + `source_sheet` + `destination_table` distinguishes processing records. No primary-key constraint is enforced.
# MAGIC
# MAGIC **Status values:** `DISCOVERED`, `INGESTED`, `SKIPPED`, `NEEDS_REVIEW`, `FAILED` — compatible with the existing PSA notebook.
# MAGIC
# MAGIC | Column | Type | Description |
# MAGIC | --- | --- | --- |
# MAGIC | `run_id` | STRING | Foreign reference to `ingestion_run_log.run_id` |
# MAGIC | `notebook_name` | STRING | Notebook that produced this record |
# MAGIC | `source_dataset_id` | STRING | e.g. `DS_01`, `DS_08` |
# MAGIC | `source_system` | STRING | e.g. `PSA` |
# MAGIC | `source_file` | STRING | Physical file name from Google Drive |
# MAGIC | `source_sheet` | STRING | Worksheet name (NULL for CSV/PDF) |
# MAGIC | `source_path` | STRING | Full source URL/path |
# MAGIC | `destination_table` | STRING | Bronze table name |
# MAGIC | `row_count` | BIGINT | Rows written to Bronze |
# MAGIC | `column_count` | BIGINT | Columns in Bronze table |
# MAGIC | `status` | STRING | Processing status |
# MAGIC | `discovered_at` | TIMESTAMP | When the file was discovered |
# MAGIC | `ingested_at` | TIMESTAMP | When the file was ingested |
# MAGIC | `notes` | STRING | Free-text notes |
# MAGIC
# MAGIC **Compatibility with current PSA notebook:**
# MAGIC
# MAGIC | PSA summary / Bronze metadata field | `file_manifest` column |
# MAGIC | --- | --- |
# MAGIC | `source_dataset_id` / `_source_dataset_id` | `source_dataset_id` |
# MAGIC | `source_file` / `_source_file` | `source_file` |
# MAGIC | `source_sheet` / `_source_sheet` | `source_sheet` |
# MAGIC | `bronze_table` | `destination_table` |
# MAGIC | `row_count` | `row_count` |
# MAGIC | `column_count` | `column_count` |
# MAGIC | `status` | `status` |
# MAGIC | `notes` | `notes` |
# MAGIC | `_source_path` | `source_path` |
# MAGIC | `_source_system` | `source_system` |
# MAGIC | `_ingested_at` | `ingested_at` |

# COMMAND ----------

# DBTITLE 1,Create + validate file_manifest
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {ingestion_table('file_manifest')} (
    run_id             STRING,
    notebook_name      STRING,
    source_dataset_id  STRING,
    source_system      STRING,
    source_file        STRING,
    source_sheet       STRING,
    source_path        STRING,
    destination_table  STRING,
    row_count          BIGINT,
    column_count       BIGINT,
    status             STRING,
    discovered_at      TIMESTAMP,
    ingested_at        TIMESTAMP,
    notes              STRING
) USING DELTA
""")

# ── Validate ──
manifest_df = spark.table(ingestion_table("file_manifest"))
print(f"✓ Table {ingestion_table('file_manifest')} created / verified.")
print(f"Rows: {manifest_df.count()}")
manifest_df.printSchema()
display(manifest_df.limit(10))

# COMMAND ----------

# DBTITLE 1,Table 3 — ingestion_errors
# MAGIC %md
# MAGIC ### Table 3 — `ingestion_errors`
# MAGIC
# MAGIC **Purpose:** Store actual ingestion exceptions and technical failures separately from the normal file manifest.
# MAGIC
# MAGIC This table supports errors such as Google Drive read failures, CSV/Excel parsing failures, worksheet parsing failures, Delta write failures, unexpected schema issues, and binary PDF ingestion failures.
# MAGIC
# MAGIC No errors are intentionally generated to populate this table.
# MAGIC
# MAGIC | Column | Type | Description |
# MAGIC | --- | --- | --- |
# MAGIC | `run_id` | STRING | Foreign reference to `ingestion_run_log.run_id` |
# MAGIC | `notebook_name` | STRING | Notebook that produced this error |
# MAGIC | `source_dataset_id` | STRING | Dataset being processed |
# MAGIC | `source_system` | STRING | e.g. `PSA` |
# MAGIC | `source_file` | STRING | Physical file name |
# MAGIC | `source_sheet` | STRING | Worksheet name (NULL if N/A) |
# MAGIC | `source_path` | STRING | Full source URL/path |
# MAGIC | `destination_table` | STRING | Intended Bronze table |
# MAGIC | `error_type` | STRING | Category of error |
# MAGIC | `error_message` | STRING | Exception or error message text |
# MAGIC | `error_timestamp` | TIMESTAMP | When the error occurred |
# MAGIC | `notes` | STRING | Free-text notes |

# COMMAND ----------

# DBTITLE 1,Create + validate ingestion_errors
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {ingestion_table('ingestion_errors')} (
    run_id             STRING,
    notebook_name      STRING,
    source_dataset_id  STRING,
    source_system      STRING,
    source_file        STRING,
    source_sheet       STRING,
    source_path        STRING,
    destination_table  STRING,
    error_type         STRING,
    error_message      STRING,
    error_timestamp    TIMESTAMP,
    notes              STRING
) USING DELTA
""")

# ── Validate ──
errors_df = spark.table(ingestion_table("ingestion_errors"))
print(f"✓ Table {ingestion_table('ingestion_errors')} created / verified.")
print(f"Rows: {errors_df.count()}")
errors_df.printSchema()
display(errors_df.limit(10))

# COMMAND ----------

# DBTITLE 1,Relationship & Idempotency
# MAGIC %md
# MAGIC ### Relationship Between the Three Tables
# MAGIC
# MAGIC ```
# MAGIC ingestion_run_log
# MAGIC     one row per notebook execution
# MAGIC            |
# MAGIC            | run_id
# MAGIC            v
# MAGIC file_manifest
# MAGIC     multiple rows per run
# MAGIC     one row per logical source/output
# MAGIC            |
# MAGIC            | failures
# MAGIC            v
# MAGIC ingestion_errors
# MAGIC     zero or more error records per run
# MAGIC ```
# MAGIC
# MAGIC ```
# MAGIC 01_ingest_psa
# MAGIC         |
# MAGIC         +--> ingestion_run_log
# MAGIC         |
# MAGIC         +--> file_manifest
# MAGIC         |
# MAGIC         +--> ingestion_errors
# MAGIC         |
# MAGIC         +--> actual data --> `02_bronze`.`psa_*`
# MAGIC ```
# MAGIC
# MAGIC Actual PSA/PSGC/DOT rows are **not** stored in the control tables — only metadata about ingestion runs, file processing results, and errors.
# MAGIC
# MAGIC **Idempotency:** This notebook uses `CREATE TABLE IF NOT EXISTS` exclusively. It does not drop, truncate, delete, or overwrite any existing data. Safe to rerun.

# COMMAND ----------

# DBTITLE 1,Final control summary
from pyspark.sql.functions import lit

control_tables = [
    ("ingestion_run_log", "one row per ingestion notebook execution"),
    ("file_manifest",     "one row per logical source/output processed"),
    ("ingestion_errors",   "technical ingestion failures and exceptions"),
]

summary_rows = []
for tbl_name, purpose in control_tables:
    full_name = ingestion_table(tbl_name)
    exists = spark.catalog.tableExists(full_name)
    row_count = spark.table(full_name).count() if exists else -1
    summary_rows.append((tbl_name, purpose, exists, row_count))
    marker = "✓" if exists else "✗"
    print(f"{marker} {tbl_name:<22} | purpose: {purpose} | rows: {row_count}")

summary_df = spark.createDataFrame(
    summary_rows,
    schema="table_name STRING, purpose STRING, exists BOOLEAN, row_count BIGINT"
)
display(summary_df)

print("\nIngestion control setup complete.")
print(f"Schema: `{CATALOG}`.`{INGESTION_SCHEMA}`")
print("Tables: ingestion_run_log, file_manifest, ingestion_errors")