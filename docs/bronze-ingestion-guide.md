# Bronze Ingestion Guide

> **Status: Implementation guide aligned with the analytical scope.**
>
> This document explains how approved source files will move from their original source into Bronze tables. File availability and extraction readiness must be confirmed during implementation.

## Purpose

To give the Bronze lead and other team members a clear, repeatable process for acquiring, reading, and loading the project's source data into Databricks.

The guide should allow someone who is not assigned to Bronze to understand which files are used, how they are loaded, and how to verify the result.

Finalized business and analytical questions live in [Business and Analytical Questions](business-and-analytical-questions.md). They define the analytical scope; this guide explains how to prepare its source data.

## What Bronze Does

> **Bronze preserves the source data in a readable form and records where it came from.**

The ingestion flow is:

**Source website or shared Drive → unchanged raw files → structured input, where needed → Bronze Delta tables**

| Stage | What it contains | Example |
| --- | --- | --- |
| **Raw files** | Original files retained unchanged | DOT PDF or PSGC workbook |
| **Prepared inputs** | Structured extracts from files that cannot be loaded directly as tables | A reviewed CSV extracted from a DOT PDF |
| **Bronze tables** | Source records loaded into Delta with ingestion metadata | DOT source rows with their file, year, and load details |

Prepared inputs must remain traceable to the original file. Extracting a table from a PDF makes it readable; it does not make its geography or reporting methods comparable across sources.

---

## Sources in Scope

Use the approved source inventory to confirm the exact files and releases. The IDs below follow the source inventory referenced in PR #30.

| Source | Role | First action |
| --- | --- | --- |
| **DOT overnight travelers — DS-05** | Tourism activity for 2019–2023 | Confirm the five yearly files and test extraction on 2019 |
| **PSGC — DS-34** | Geographic reference | Inspect the workbook, sheets, columns, and code formats |
| **Population — DS-24** | Potential population denominator | Acquire and inspect the selected table; record its actual years |
| **Provincial GDP, GDP per capita, and accommodation and food service GVA — DS-27–32** | Economic indicators | Acquire and inspect each selected file, including units and price basis |
| **Regional and PTSA sources** | Validation and national context | Record their role separately from the province-level core |

Being included in the analytical scope does not mean a file has been acquired or its extraction has been verified. Record those separately.

The final population-denominator method and geography-mapping rules are downstream decisions. They do not prevent preserving or loading the available source records.

---

## Notebooks to Create

> **Use one shared notebook to land the original files, separate notebooks for different preparation methods, and one shared notebook to load Bronze tables.**

The table below defines the initial notebook structure. These are notebooks to create, not existing implementations.

| Notebook | Responsibility | Inputs and output |
| --- | --- | --- |
| `notebooks/01_ingestion/01_land_source_files.ipynb` | Land all selected original files using the manifest | Reads accessible source files; writes unchanged copies to `raw/` and records file paths, hashes, and outcomes |
| `notebooks/01_ingestion/02_prepare_structured_sources.ipynb` | Profile and read structured sources such as PSGC and acquired PSA workbooks | Reads selected raw files using configured sheets, headers, and columns; produces profile results and prepared inputs where conversion is needed |
| `notebooks/01_ingestion/03_extract_dot_tables.ipynb` | Extract DOT PDF tables, starting with the 2019 pilot | Reads selected DOT PDFs; writes structured extracts under `prepared/dot/`, with source references and verification results |
| `notebooks/02_bronze/01_bronze_setup.ipynb` | Create the Bronze schema, required tables, and ingestion log | Uses the target catalog/schema and approved table definitions; creates missing objects without dropping existing data |
| `notebooks/02_bronze/02_load_bronze.ipynb` | Load all selected, verified inputs through the shared Bronze writer | Reads structured raw files or verified prepared inputs; writes each dataset to its own Bronze table and records load outcomes |
| `tests/bronze/01_bronze_validation.ipynb` | Verify the selected Bronze loads | Checks file-level row counts, required columns, source metadata, and load outcomes; produces validation results |

### One Landing Notebook for All Files

The landing notebook can process DOT PDFs, PSGC, and PSA files because its job is to **copy and verify files**, not interpret their tables. Use the manifest to select the files and their destinations.

Allow either all available approved files or a selected dataset/period to be processed. For example, the same notebook can land all five DOT PDFs or only the 2019 file.

Direct access to a website or Drive requires a working access method. If automated access is not available, upload the originals to an agreed staging location first and let the landing notebook copy them into `raw/`. Document that manual step in the runbook.

Verify the copy against the original file hash. If the same file is already landed and verified, skip it. If its contents changed, retain a separate version for review. Record pending files as pending; a missing file explicitly selected for the run must be reported as a failure.

### Separate Preparation by Reading Method

DOT PDFs need extraction and reconciliation, so they have their own preparation notebook. Structured sources share another notebook, with source-specific reading settings and functions.

The structured preparation notebook must not assume every workbook has the same sheet names, headers, or layout. If an acquired source requires a substantially different process, add a preparation notebook for that method and document its inputs and output.

Use the same DOT notebook for 2019–2023, with year-specific extraction logic where needed. Do not create a separate notebook for every yearly file. During the pilot, run it for 2019 only; later runs may select the remaining years. Unverified extracts must not enter the Bronze load.

### One Bronze Loader, Separate Tables

The Bronze loading notebook selects the correct reader and target table for each dataset. Sharing a loader does **not** mean combining DOT, PSGC, population, and economic records into one table.

Load available, verified datasets independently. An unresolved DOT extraction must not prevent a verified PSGC file from loading. Report success, failure, and skip outcomes per selected input, and fail the run if a required selected load fails.

### Where the Reusable Code Goes

| Location | Code to keep there |
| --- | --- |
| `src/01_ingestion/` | File-copy and hash functions, source readers, PDF extraction, and profiling logic |
| `src/02_bronze/` | Metadata handling, safe Delta writes, table setup, and ingestion-log logic |
| `notebooks/` | Parameters, calls to the reusable code, and readable run results |
| `tests/bronze/` | Executable Bronze validation checks |

Notebooks are the Databricks entry points. Keep reusable logic in `src/` and have notebooks call it rather than maintaining two copies. Use parameters such as dataset ID, period/release, manifest location, storage root, and target catalog/schema as applicable.

### Run Order

1. Run **landing** for the selected originals.
2. Run the relevant **structured preparation or DOT extraction** notebook.
3. Complete extraction review where required and record readiness.
4. Run **Bronze setup**, then **Bronze loading** for verified inputs.
5. Run **Bronze validation**.
6. Rerun the same unchanged selection and validate again to demonstrate safe rerun behavior.

The preparation branches can run independently after their files land. Bronze setup can also run independently before loading. The first DOT extraction review is a readiness step; scheduling the notebooks alone does not verify the extracted values.

---

## Task 1: Record the Exact Files

### What to Do

Create `resources/source-manifest.yml` as the ingestion source register. A **manifest** is a list of the exact files the pipeline will use and the information needed to identify them.

Record the following for each file:

- dataset ID and source agency;
- official source URL and original filename;
- release or reference period and years covered;
- file format and archive/raw location;
- retrieval date and available attribution or usage terms;
- acquisition status and extraction status;
- file hash, once acquired.

A **file hash** is a fingerprint of the file's contents. It helps detect whether a file changed even when its filename stayed the same.

Keep acquisition and extraction status separate. For example, a PDF may be **acquired** while its table extraction is still **not verified**. If usage terms are unclear, record that uncertainty.

### Expected Output

One source register showing which files are available, which are missing, and which are ready to load.

## Task 2: Preserve the Original Files

### What to Do

Retain the unchanged originals in the shared Drive archive and copy the files needed for ingestion into the agreed Databricks Volume under `raw/`.

PDFs remain PDFs. Workbooks remain workbooks. Save extracted or converted files separately under `prepared/`.

Use dataset and period folders so files can be found consistently. Record the actual paths in the manifest.

If a new file has the same name but different contents, retain it as a separate version and review the change before reloading it.

### Expected Output

Original files are available to the ingestion process and can be matched to the source register.

## Task 3: Confirm How Each File Can Be Read

### Structured Files: PSGC, Population, and Economic Tables

Inspect each acquired file and record:

- the sheet or table to read;
- the header row, columns, and row count;
- geographic code and label formats;
- reference years, units, and current/constant-price labels, where relevant;
- blank fields, repeated records, footnotes, and total rows.

Preserve codes as text when needed to retain leading zeros. Keep source labels and reporting notes available for later interpretation.

These checks describe the file. Do not remove repeated records or missing values simply because they look unusual; first establish what each source row represents.

### DOT PDFs

Start with the **2019 file** as the extraction pilot:

1. Identify the relevant pages and tables.
2. Check whether the table text is readable or requires OCR.
3. Extract the table into a structured file.
4. Compare extracted labels and values with the PDF.
5. Reconcile reported totals where the source provides them, and record any differences.
6. Retain the original filename and page/row references for the extracted records.

Once the pilot is verified, repeat the process for 2020–2023. Check every year's output because layouts and reporting categories may differ.

If OCR or manual transcription is needed, document the method and review the output against the original. An unreadable or unverified value must not be guessed.

### Expected Output

A documented reading method for each structured source and reviewed extracts for the DOT PDFs. Any unresolved extraction issue is recorded before the affected data is treated as ready.

## Task 4: Load the Bronze Tables

### What to Do

Build a reusable loading process that reads each verified input, adds ingestion metadata, and writes the records into Bronze Delta tables.

Use a shared loading pattern with source-specific readers where needed. A PDF extract and an Excel workbook may need different reading logic.

Each loaded record must be traceable through metadata such as:

| Metadata | Purpose |
| --- | --- |
| Dataset ID | Identifies the source inventory entry |
| Original source file and hash | Identifies the exact original file |
| Input file | Identifies the file actually read, including a prepared extract |
| Source period or release | Identifies the reporting period or version |
| Ingestion timestamp and run ID | Identifies when and in which run the record was loaded |
| Source page/row reference, where applicable | Supports checking extracted values against the original |

Preserve source values and notes, including distinctions between zero, blank, unavailable, and suppressed values. Record any structural changes needed to read the file, such as flattening a multirow header.

Define safe rerun behavior before the first load:

- Reprocessing the same input must not add duplicate records.
- A replacement must affect only the intended dataset and period or release.
- Changed content must be detected and reviewed before replacing previously loaded data.
- Failed or empty loads must be visible in the run result.

Do not use an unrestricted table overwrite when loading one year's file into a table containing several years. Record which file/version was loaded and whether the load succeeded, failed, or was skipped.

### Expected Output

Bronze Delta tables with source metadata and a documented loading process that can be rerun safely.

## Task 5: Verify and Document the First Run

### What to Do

For each loaded file, record:

- original and prepared-file hashes, where applicable;
- input row count and Bronze row count for that file;
- required columns and source periods found;
- extraction or schema issues;
- load outcome;
- result of rerunning the same unchanged input.

Verify that rerunning does not increase the loaded row count or introduce additional copies of the same source records. Preserve legitimate repeated rows from the original source unless an approved rule says otherwise.

Document the run instructions and evidence in `docs/runbook.md`. Include how to select a source, run its load, inspect the result, and recover from a failed attempt.

### Expected Output

A verified first load, rerun evidence, and instructions another team member can follow.

---

## What Can Start in Parallel

| Workstream | Can start when |
| --- | --- |
| PSGC profiling and loading | The selected workbook is available |
| DOT 2019 extraction pilot | The original 2019 PDF is available |
| Remaining DOT years | The pilot provides a working extraction approach; each year still needs verification |
| Population and economic sources | Their individual files are acquired |
| Silver geography and quality design | Source profiles provide enough information to propose rules |
| Executable Silver transformations | The required Bronze inputs are available and verified |

The team does not need every dataset finished before loading an available, verified source. Silver design can also proceed while Bronze implementation continues.

## Bronze and Silver Responsibilities

| Bronze | Silver |
| --- | --- |
| Preserve source files and source records | Standardize fields and data types |
| Extract readable tables and verify extraction accuracy | Apply approved quality and transformation rules |
| Record source labels, periods, units, and reporting notes | Map source geography to the approved PSGC reference |
| Retain missing-value markers and reporting differences | Apply approved missing-data and comparability rules |
| Load safely and record lineage | Produce consistent records for Gold analysis |

Bronze should expose issues for the next layer to handle. Geography mapping, population-denominator selection, recovery thresholds, and analytical comparisons follow the decisions documented for Silver and Gold.

## Definition of Done

> **A source is Bronze-ready when its original file is preserved, its reading or extraction method is verified, its records can be loaded reproducibly, and the load can be traced and rerun safely.**

- [ ] The exact file and its status are recorded in the manifest.
- [ ] The original file is retained unchanged in the agreed raw location.
- [ ] The reading method is documented, with extraction checks where needed.
- [ ] Bronze records retain the source values and required metadata.
- [ ] Input and loaded row counts reconcile, or differences are explained.
- [ ] Rerunning the same input does not introduce additional copies.
- [ ] Known limitations and recovery instructions are documented.

Track completion per source. Missing files and unresolved extraction issues remain visible; they do not prevent verified sources from moving forward.
