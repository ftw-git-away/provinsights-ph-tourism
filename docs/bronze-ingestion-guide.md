# Bronze Ingestion Guide

This guide explains how the source files move from Google Drive into Bronze Delta tables, how each ingestion run is tracked, and how to check the results. Which sources are used and why is in [consolidated-data-sources.md](consolidated-data-sources.md). Every column of the control and Bronze tables is in the [data dictionary](data-dictionary.md#2-01_ingestion_bronze--01_ingestion-and-02_bronze).

## Contents

- [What Bronze does](#what-bronze-does)
- [Source access](#source-access)
- [Notebooks](#notebooks)
- [Ingestion control tables](#ingestion-control-tables)
- [Run lifecycle](#run-lifecycle)
- [Bronze tables](#bronze-tables)
- [Bronze metadata](#bronze-metadata)
- [Reruns and changed files](#reruns-and-changed-files)
- [Checking a run](#checking-a-run)
- [Adding a new source](#adding-a-new-source)
- [Removed Bronze tables](#removed-bronze-tables)

## What Bronze does

The notebooks in `notebooks/01_ingestion_bronze` write to two schemas in `tuklas_dev`:

| Schema | Holds |
| --- | --- |
| `01_ingestion` | What happened during each run: `ingestion_run_log`, `file_manifest`, `ingestion_errors` |
| `02_bronze` | What was loaded: every source table exactly as printed, plus the original files as binary |

**Bronze keeps every value exactly as printed, as text.** It doesn't standardize names, map places to PSGC, remove hierarchy markers, interpret `-`, convert types, aggregate or calculate anything. All of that happens in Silver, where each rule is documented in the decision log.

Only the technical steps needed to load a file are allowed: making column names valid for Delta, reading the correct header row, keeping mixed-type Excel columns as text, and dropping completely empty worksheet rows.

| Bronze | Silver |
| --- | --- |
| Keeps source rows, labels, notes and `-` markers as printed | Applies the missing-data rules (DL-009, DL-019) |
| Records where each row came from | Maps every place to a PSGC reporting unit (DL-010) |
| Shows source problems | Resolves them through reviewed rules and seeds |
| Loads safely and logs the outcome | Produces one row per unit and year |

## Source access

The source files sit in shared Google Drive folders. The notebooks read them through the Unity Catalog connection **`capstone_gdrive`**, listing a folder with:

```sql
SELECT * FROM list_files('<folder URL>', connection => 'capstone_gdrive');
```

The connection holds the Google Drive credentials, so no service-account keys, tokens or passwords are stored in the notebooks or the repository. Access is controlled by who can use the connection in Unity Catalog.

Each notebook sets its folder and files at the top:

| Notebook | Folder setting | Files |
| --- | --- | --- |
| `01_ingest_psa`, `04_ingest_psa_ds18_pdf` | `PSA_FOLDER`: [PSA folder](https://drive.google.com/drive/folders/1hBSj2dHu1ylbEjRjLzzxwMQ9CBXItiQs) | `SOURCE_FILES`, one Drive file link per dataset |
| `02_ingest_psgc` | `PSGC_FOLDER`: [PSGC folder](https://drive.google.com/drive/folders/12pSL9t9MsD4wy7Jj0L_Qadb5UsfxZJ3m) | `SOURCE_FILES`, DS_33 and DS_34 |
| `03_ingest_dot` | `DOT_FOLDER`: [DOT Regional Travelers folder](https://drive.google.com/drive/folders/1dlmJFnL7FZgd3KXnioxcbrbmI5bS_ovy) | `SOURCE_FILES`, one PDF per year, 2019-2024 |

Files are matched by their Drive file ID, so renaming a file in Drive doesn't break ingestion. The folder listing is used to read each file's exact name.

### File naming

Dataset IDs use underscores (`DS_05`, `DS_34`, never `DS-05`). PSA files follow `DS_XX_PSA_<description>_<years>.<ext>`, for example `DS_31_PSA_Table_3_94_Accommodation_Food_Service_GVA_Current_Prices_2019_2023.csv`. The Philippine Statistical Yearbook workbook `DS_08_to_DS_17_PSA_PSY_Tables_8_1_to_8_10.xlsx` is one file holding ten datasets.

## Notebooks

The job runs `00_ingestion_setup` first, then the four ingestion notebooks in parallel (see the [runbook](runbook.md)).

| Notebook | Run ID prefix | Reads | Writes |
| --- | --- | --- | --- |
| `00_ingestion_setup` | none | nothing | The three control tables, with `CREATE TABLE IF NOT EXISTS`. It never drops, truncates or overwrites them, and inserts no rows. |
| `01_ingest_psa` | `psa_` | 12 PSA files (CSV, Excel, PDF) | 32 Bronze tables, including `psa_ds_18_pdf` (the DS_18 PDF stored as binary) |
| `02_ingest_psgc` | `psgc_` | DS_33 and DS_34 (Excel) | One table per sheet, `psgc_report_text`, `psgc_source_files` |
| `03_ingest_dot` | `dot_` | DS_05 PDFs, 2019-2024 | One table per year, `dot_ds_05_report_text`, `dot_ds_05_pdf` |
| `04_ingest_psa_ds18_pdf` | `psa_ds18pdf_` | The DS_18 PDF | `psa_ds_18_pdf_rows`, `psa_ds_18_pdf_report_text` |

`04_ingest_psa_ds18_pdf` exists because the DS_18 Excel gives province totals that include their HUCs, while ProvInsights keeps 16 HUCs separate (DL-010). Only the PDF lists every city and municipality, so it is the source of HUC population (DL-021).

## Ingestion control tables

### `ingestion_run_log`

One row per notebook run. The row is inserted as `STARTED` and updated at the end, never appended twice.

| Column | Meaning |
| --- | --- |
| `files_discovered` | Physical source files in the run |
| `files_ingested` | Physical files processed successfully |
| `files_skipped` | Physical files skipped or left for review |
| `files_failed` | Physical files with at least one failed output |
| `tables_created` | Distinct Bronze tables written successfully |
| `status` | `STARTED`, `SUCCESS`, `PARTIAL_SUCCESS` or `FAILED` |

A physical file is `FAILED` if any of its outputs failed, otherwise `INGESTED` if any output was ingested, otherwise `SKIPPED`.

### `file_manifest`

One row per **logical output**, so one file can have several rows (for example, the DS_01 workbook gives 10 tables and the DS_18 Excel and PDF are separate rows). Statuses are `DISCOVERED`, `INGESTED`, `SKIPPED`, `NEEDS_REVIEW` and `FAILED`. A sheet with no table, such as the image-only "Coding Structure" sheet in DS_34, is `SKIPPED`.

The manifest is written with `MERGE INTO` on `run_id`, `source_dataset_id`, `source_file`, `COALESCE(source_sheet, '')` and `destination_table`, so re-executing a cell in the same run updates the row instead of duplicating it. A new run gets a new `run_id`, so earlier runs stay visible.

### `ingestion_errors`

One row per real technical failure: a Drive read, CSV, Excel or PDF parsing failure, or a Delta write failure. Nothing is written when nothing fails.

## Run lifecycle

1. **Start.** Generate a `run_id` (prefix, date, time and a short random ID, such as `dot_<yyyymmdd>_<hhmmss>_<8 characters>`), insert a `STARTED` row in `ingestion_run_log`, and list the source folder.
2. **Load each source.** Read it, keep the values as printed, add the Bronze metadata, write the Delta table, check it, and record the output in `file_manifest`. If one source fails, record it as `FAILED`, write the error to `ingestion_errors`, and continue with the next independent source.
3. **Finish.** Count the outputs from `file_manifest`, roll them up to physical files, set the final status, and update the same `ingestion_run_log` row.

A run left at `STARTED` (for example after a cluster stops) is only marked `SUCCESS` when its manifest shows a complete successful load. Old `STARTED` rows are never converted automatically.

## Bronze tables

| Pattern | One row is | Example |
| --- | --- | --- |
| `dot_ds_05_<year>` | One printed row of that year's DOT table (region, province or HUC, or sub-row) | `dot_ds_05_2023` |
| `psa_ds_<nn>` | One printed row of a PSA table | `psa_ds_27` (GDP), `psa_ds_31` (A&F GVA), `psa_ds_18` (population) |
| `psa_ds_01_table_<nn>`, `psa_ds_02_<sheet>` | One printed row of a PTSA or classification sheet | `psa_ds_01_table_01`, `psa_ds_02_tourism_industries` |
| `psa_ds_18_pdf_rows` | One printed row of the DS_18 PDF, with its six yearly values | |
| `psgc_ds_33_<sheet>`, `psgc_ds_34_<sheet>` | One printed row of a PSGC sheet | `psgc_ds_34_psgc` |
| `*_report_text` | One non-table line: a title, an "as of" date or a footnote (such as DOT's Boracay jetty note) | `dot_ds_05_report_text`, `psgc_report_text` |
| `*_pdf`, `*_source_files` | One original file stored as binary | `dot_ds_05_pdf`, `psa_ds_18_pdf`, `psgc_source_files` |

Every tabular Bronze row keeps its position in the source: `source_row_number`, or `page_number` and `pdf_line_number` for PDFs (DL-023). Delta tables have no row order, so this is what lets Silver read layouts that span several rows.

## Bronze metadata

Every Bronze row carries:

| Column | Meaning |
| --- | --- |
| `_source_dataset_id` | Dataset ID, for example `DS_05` |
| `_source_file` | Exact file name |
| `_source_sheet` | Worksheet name; NULL for CSV and PDF |
| `_source_path` | Google Drive link |
| `_source_system` | `DOT`, `PSA` or `PSGC` |
| `_source_sha256` | SHA-256 fingerprint of the source file |
| `_run_id` | The ingestion run that wrote the row |
| `_ingested_at` | When the row was written |

Together with the stored original file and the row position, these let any value be traced back to the exact file and row it came from.

## Reruns and changed files

Bronze tables have fixed names and are written with Delta `overwrite`, so a rerun replaces a table instead of appending a second copy. For example, `psa_ds_32` has 133 rows after every run, not 266. Delta keeps the earlier version in its history.

| Notebook | What a rerun replaces |
| --- | --- |
| `01_ingest_psa` | Every PSA table |
| `02_ingest_psgc` | The datasets in `FILES_TO_RUN` (`"all"` or a list such as `["DS_34"]`); others are untouched |
| `03_ingest_dot` | The years in `YEARS_TO_RUN` (`"all"` or a list such as `["2024"]`); other years are untouched |
| `04_ingest_psa_ds18_pdf` | Both of its tables |

**Changed files.** Every notebook stores the file's SHA-256 fingerprint. The DOT and DS_18 PDF notebooks compare it with the fingerprint from the previous load and write a warning to the `file_manifest` notes when the file changed. `01_ingest_psa` also stops if a file changes while it is being read. To load a new year of data, follow "Load a new year of source data" in the [runbook](runbook.md).

## Checking a run

Control-table timestamps are stored in UTC. Convert them to `Asia/Manila` for display.

```sql
-- latest runs
SELECT run_id, notebook_name, status,
       from_utc_timestamp(started_at, 'Asia/Manila')   AS started_at_ph,
       from_utc_timestamp(completed_at, 'Asia/Manila') AS completed_at_ph,
       files_discovered, files_ingested, files_skipped, files_failed, tables_created
FROM tuklas_dev.`01_ingestion`.ingestion_run_log
ORDER BY started_at DESC;

-- outputs of one run
SELECT source_dataset_id, source_file, source_sheet, destination_table, row_count, status, notes
FROM tuklas_dev.`01_ingestion`.file_manifest
WHERE run_id = '<run_id>'
ORDER BY source_dataset_id, source_sheet, destination_table;

-- errors of one run
SELECT *
FROM tuklas_dev.`01_ingestion`.ingestion_errors
WHERE run_id = '<run_id>';
```

A complete `01_ingest_psa` run shows 12 physical files and 32 `INGESTED` outputs:

```sql
SELECT COUNT(DISTINCT source_file) AS physical_files,
       COUNT(DISTINCT CASE WHEN status = 'INGESTED' THEN destination_table END) AS outputs
FROM tuklas_dev.`01_ingestion`.file_manifest
WHERE run_id = '<psa run_id>';
```

## Adding a new source

A new source is ready for Silver when:

- [ ] it has a `DS_XX` ID and a file name that follows the naming pattern;
- [ ] it is in a Drive folder the `capstone_gdrive` connection can read, and its file link is in the notebook's `SOURCE_FILES`;
- [ ] it reuses the control tables and run lifecycle above, with no second control framework;
- [ ] every row keeps its source position and the Bronze metadata columns;
- [ ] the original file is stored as binary;
- [ ] a rerun replaces the table instead of appending to it;
- [ ] each output is in `file_manifest` and any failure in `ingestion_errors`;
- [ ] the source is added to [consolidated-data-sources.md](consolidated-data-sources.md) and the [data dictionary](data-dictionary.md), and any new task to the job (see [`resources/README.md`](../resources/README.md)).

## Removed Bronze tables

On 2026-10-21 eight early PSGC tables with a `psa_psgc_` prefix were dropped from `tuklas_dev.02_bronze` with `notebooks/99_maintenance/drop_stale_bronze_tables`, to free Unity Catalog metastore quota (DL-038). They predate `02_ingest_psgc`, no notebook writes or reads them, and lineage showed no downstream consumers. Each has a `psgc_` replacement:

| Dropped | Replaced by |
| --- | --- |
| `psa_psgc_report_text` | `psgc_report_text` |
| `psa_psgc_source_files` | `psgc_source_files` |
| `psa_psgc_ds_33_provincial_summary` | `psgc_ds_33_provincial_summary` |
| `psa_psgc_ds_34_metadata` | `psgc_ds_34_metadata` |
| `psa_psgc_ds_34_psgc` | `psgc_ds_34_psgc` |
| `psa_psgc_ds_34_notes` | `psgc_ds_34_notes` |
| `psa_psgc_ds_34_national_summary` | `psgc_ds_34_national_summary` |
| `psa_psgc_ds_34_prov_sum` | `psgc_ds_34_prov_sum` |
