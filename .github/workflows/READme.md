# GitHub Actions Workflows

This folder contains the automated workflows that check and deploy the ProvInsights PH tourism data platform.

| File | Workflow name | Purpose | Status |
| --- | --- | --- | --- |
| `ci.yml` | CI | Checks the repository and the Databricks bundle on every push and pull request | Active |
| `deploy.yml` | CD - Deploy ProvInsights PH to Databricks | Deploys the Databricks bundle to the `dev` target after changes merge into `main` | Active |

```text
Pull request ──► CI (Validate repository + Validate Databricks bundle)
                    │  review + approval
                    ▼
Merge to main ──► CD (validate → deploy → summary) ──► Databricks job updated
                    │  optional: Run workflow with run_pipeline
                    ▼
                 Pipeline job runs in Databricks
```

## CI — `ci.yml`

### When it runs

- Pushes to `main`, `feature/**`, `chore/**`, `docs/**` and `fix/**`
- Pull requests into `main`
- Manually: **Actions → CI → Run workflow**

Each check appears twice on a pull request, once for the push and once for the pull request. This is expected.

### Job 1: Validate repository

Runs without Databricks credentials and never connects to live DOT, PSA or Databricks services.

| Check | Fails when |
| --- | --- |
| Required files and directories | `README.md`, `docs/`, `notebooks/`, `resources/`, `src/` or `tests/` is missing, or `README.md` is empty |
| Python syntax in `src/` | A `.py` file in `src/` does not compile |
| Notebooks directory contents | `notebooks/` contains anything other than `.ipynb` files and `README.md` files |
| Notebook structure and cell syntax | A notebook is not valid JSON, has an invalid cell type, has no markdown cell, has a `%python` cell with a syntax error, or has a `%sql` cell that is empty or not valid Databricks SQL |

Cells without a `%python`, `%sql` or `%md` magic are reported as `INFO` and not syntax-checked.

### Job 2: Validate Databricks bundle

Runs `databricks bundle validate -t dev` against the branch, using the GitHub `development` environment. It checks `databricks.yml` and every job in `resources/jobs/`, including that each `notebook_path` exists.

- A task that points to a notebook not yet on the branch fails this check. Merge the notebook first, then add its task.
- Skipped for pull requests from forks, which cannot read environment secrets.

## CD — `deploy.yml`

### When it runs

- Pushes to `main` that change any of: `databricks.yml`, `resources/**`, `notebooks/**`, `src/**`, `tests/**`, `dashboard/**`, `.github/workflows/deploy.yml`
- Manually: **Actions → CD - Deploy ProvInsights PH to Databricks → Run workflow**

Changes to `docs/` or README files alone do not trigger a deploy. Pull requests never deploy.

### Steps

1. **Check required GitHub configuration**: stops with a clear message if a value below is missing
2. **Install Databricks CLI**: pinned to version 1.19.0
3. **Validate bundle**: `databricks bundle validate -t dev`
4. **Deploy bundle**: `databricks bundle deploy -t dev`
5. **Show deployed Databricks resources**: lists the deployed job in the run's **Summary**
6. **Run end-to-end pipeline**: only on a manual run with **run_pipeline** ticked

Deploying updates the job definition. It does **not** run the job, so no tables change on merge. Only a manual run, or **run_pipeline**, writes data.

Only one deploy runs at a time (`concurrency: provinsights-databricks-dev`), and a running deploy is never cancelled.

## Required GitHub configuration

Both workflows read these values from **Settings → Environments → development**:

| Name | Type | Value |
| --- | --- | --- |
| `DATABRICKS_HOST` | Environment variable | Databricks workspace URL, e.g. `https://dbc-xxxx.cloud.databricks.com` |
| `DATABRICKS_TOKEN` | Environment secret | Databricks access token |
| `DATABRICKS_ALERT_EMAIL` | Environment variable | Email that receives pipeline failure notifications (one address) |

`DATABRICKS_ALERT_EMAIL` is passed to the bundle as `BUNDLE_VAR_alert_email`, which sets the `alert_email` variable in `databricks.yml`.

Never put tokens or workspace credentials in the repository. If a token leaks, revoke it in Databricks (**Settings → Developer → Access tokens**) and replace the secret.

## Troubleshooting

| What you see | Likely cause | Fix |
| --- | --- | --- |
| `Missing GitHub environment variable/secret: ...` | Value not set, or set at repository level instead of in the `development` environment | Add it under **Settings → Environments → development** |
| Authentication error or `401` in Validate / Deploy | Token expired or wrong, or wrong host URL | Create a new token and update `DATABRICKS_TOKEN`; check `DATABRICKS_HOST` |
| `notebook ... not found` | A job task points to a notebook that is not on the branch, or the path is wrong | Merge the notebook first; check the path starts with `../../` and matches the file name |
| `no value assigned to required variable alert_email` | `DATABRICKS_ALERT_EMAIL` not reaching the bundle | Check the variable name in the `development` environment |
| `notebooks/ may only contain .ipynb files and README.md` | A `.py`, `.csv` or other file was added under `notebooks/` | Export notebooks as `.ipynb`; keep data and seeds outside `notebooks/` |
| `notebook must contain at least one markdown cell` | Notebook has only code cells | Add a markdown cell describing the notebook |
| No deploy after a merge | The merge changed only files outside the `paths:` list | Expected; use **Run workflow** to deploy manually if needed |

## Testing locally before a pull request

```bash
databricks auth login --host <workspace URL> --profile <profile>
databricks bundle validate -t dev -p <profile> --var="alert_email=<your email>"
```

`Validation OK!` locally means the **Validate Databricks bundle** check should pass on GitHub.