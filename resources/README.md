# Resources

Databricks resources deployed by the bundle defined in [`databricks.yml`](../databricks.yml).

```text
resources/
├── jobs/
│   └── tourism_pipeline.yml   # End-to-end pipeline job
└── seeds/                     # Reviewed reference files used by notebooks (see seeds/README.md)
```

Every `*.yml` file in `resources/jobs/` is loaded by the bundle through:

```yaml
include:
  - resources/jobs/*.yml
```

## Pipeline job: `tourism_pipeline`

Job name in Databricks: **ProvInsights PH - End-to-End Pipeline**
(in the `dev` target it appears as `[dev <user>] ProvInsights PH - End-to-End Pipeline`).

### Run order

```text
ingestion_setup
 ├─ ingest_psa
 ├─ ingest_psgc
 ├─ ingest_dot
 └─ ingest_psa_ds18_pdf
        │  (all ingestion done)
        ▼
silver_setup ─ silver_geography ─┬─ silver_dot
                                 ├─ silver_psa_economy
                                 └─ silver_population
        │  (all Silver done)
        ▼
gold_setup ─┬─ gold_dim_province ─┐
            └─ gold_dim_year ─────┴─ gold_fact_province_year ─ gold_run_evidence
                                                                      │  (after gold_run_evidence)
                                                                      ▼
                                   analytics ─ analytics_validation ─ analytics_run_evidence
```

The job runs in layers. Each layer starts with its setup task, which waits for the whole
previous layer, so each task depends only on the step directly before it. Tasks in the same
step run in parallel.

If you remove a setup task, add direct dependencies on the tables each task reads, or the
layers can run out of order.

### Tasks

| Layer | Task | Notebook | Runs after |
| --- | --- | --- | --- |
| 01 Ingestion | `ingestion_setup` | `notebooks/01_ingestion/00_ingestion_setup.ipynb` | — |
| 01 Ingestion | `ingest_psa` | `notebooks/01_ingestion/01_ingest_psa.ipynb` | `ingestion_setup` |
| 01 Ingestion | `ingest_psgc` | `notebooks/01_ingestion/02_ingest_psgc.ipynb` | `ingestion_setup` |
| 01 Ingestion | `ingest_dot` | `notebooks/01_ingestion/03_ingest_dot.ipynb` | `ingestion_setup` |
| 01 Ingestion | `ingest_psa_ds18_pdf` | `notebooks/01_ingestion/04_ingest_psa_ds18_pdf.ipynb` | `ingestion_setup` |
| 03 Silver | `silver_setup` | `notebooks/03_silver/00_silver_setup.ipynb` | `ingest_psa`, `ingest_psgc`, `ingest_dot`, `ingest_psa_ds18_pdf` |
| 03 Silver | `silver_geography` | `notebooks/03_silver/01_silver_geography.ipynb` | `silver_setup` |
| 03 Silver | `silver_dot` | `notebooks/03_silver/02_silver_dot.ipynb` | `silver_geography` |
| 03 Silver | `silver_psa_economy` | `notebooks/03_silver/03_silver_psa_economy.ipynb` | `silver_geography` |
| 03 Silver | `silver_population` | `notebooks/03_silver/04_silver_population.ipynb` | `silver_geography` |
| 04 Gold | `gold_setup` | `notebooks/04_gold/00_gold_setup.ipynb` | `silver_dot`, `silver_psa_economy`, `silver_population` |
| 04 Gold | `gold_dim_province` | `notebooks/04_gold/01_gold_dim_province.ipynb` | `gold_setup` |
| 04 Gold | `gold_dim_year` | `notebooks/04_gold/02_gold_dim_year.ipynb` | `gold_setup` |
| 04 Gold | `gold_fact_province_year` | `notebooks/04_gold/03_gold_fact_province_year.ipynb` | `gold_dim_province`, `gold_dim_year` |
| 04 Gold | `gold_run_evidence` | `notebooks/04_gold/04_gold_run_evidence.ipynb` | `gold_fact_province_year` |
| 05 Analytics | `analytics` | `notebooks/05_analytics/01_build_analytics.ipynb` | `gold_run_evidence` |
| 05 Analytics | `analytics_validation` | `notebooks/05_analytics/02_analytics_validation.ipynb` | `analytics` |
| 05 Analytics | `analytics_run_evidence` | `notebooks/05_analytics/03_analytics_run_evidence.ipynb` | `analytics_validation` |

There is no `02_bronze` folder: the ingestion notebooks in `01_ingestion` write the Bronze
tables themselves, so the layer numbers go from `01` to `03`. The `02` prefix stays reserved
so the folder numbers keep matching the medallion layers (Bronze = 02, Silver = 03, Gold = 04).

Silver notebooks run their own
data-quality checks before writing; results go to `06_data_quality.dq_results`, and a failed
`BLOCK` check fails the task, which stops every task that depends on it.

### Job settings

| Setting | Value | Why |
| --- | --- | --- |
| `max_concurrent_runs` | `1` | Two runs never write the same tables at the same time |
| `timeout_seconds` (job) | `10800` (3 h) | Stops a stuck run; review after the first full run |
| `timeout_seconds` (task) | 900–2700 | Every task has its own limit; analytics limits are ~3× the longest observed run. Setup and run-evidence tasks get 1800 s to allow for serverless compute waits |
| Retries | 2 retries, 30 s apart | Ingestion tasks only, since they call external sources |
| Failure emails | `${var.alert_email}` | See below |
| Skipped / cancelled runs | No alert | Avoids noise from manual cancels |

### Failure emails

The job emails `alert_email` when a run fails. The value is a bundle variable defined in
`databricks.yml`:

| Where | How the value is set |
| --- | --- |
| GitHub deploy | Environment variable `DATABRICKS_ALERT_EMAIL` in **Settings → Environments → development** |
| Local validate / deploy | `--var="alert_email=<email>"` on the command line |

To notify more people, use a group address in `DATABRICKS_ALERT_EMAIL`, or add extra
addresses under `on_failure:` in `tourism_pipeline.yml` (one `- email` per line).

## Adding a task for a new notebook

1. Merge the notebook into `main` first. A task that points to a missing notebook fails
   validation and the deploy.
2. On a new branch, copy an existing task block in `resources/jobs/tourism_pipeline.yml`.
3. Set:
   - `task_key`: unique, lowercase, e.g. `silver_<table>`
   - `notebook_path`: relative to `resources/jobs/`, so it starts with `../../`
     (e.g. `../../notebooks/03_silver/05_silver_example.ipynb`)
   - `depends_on`: the step directly before it in its layer (the layer's setup task if it's
     the first one). Don't add dependencies on earlier layers; the setup tasks already cover them.
   - `timeout_seconds`: always; add retries only for tasks that call external sources
4. Validate:

   ```bash
   databricks bundle validate -t dev --var="alert_email=<your email>"
   ```

5. Open a small PR. After it merges, the deploy workflow updates the job automatically.

Layer folders use underscores: `01_ingestion`, `03_silver`, `04_gold`, `05_analytics`,
`06_data_quality`. There is no `02_bronze` folder, because Bronze is written during ingestion.

## Testing the job in your own dev folder

```bash
databricks bundle deploy -t dev --var="alert_email=<your email>"
databricks bundle run -t dev tourism_pipeline --var="alert_email=<your email>"
```

The `dev` target deploys to your own workspace folder and prefixes the job name with
`[dev <user>]`. Running the job writes to the shared `tuklas_dev` catalog, so tell the team
before a full run.