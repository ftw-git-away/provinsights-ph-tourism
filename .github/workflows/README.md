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

- Pushes to `main`, `feature/**`, `chore/**`, `docs/**`, `fix/**`, `test/**` and `ci/**`
- Pull requests into `main`
- Manually: **Actions → CI → Run workflow**

Each check appears twice on a pull request, once for the push and once for the pull request. This is expected.

### Job 1: Validate repository

Runs without Databricks credentials and never connects to live DOT, PSA or Databricks services.

| Check | Fails when |
| --- | --- |
| Required files and directories | `README.md`, `docs/`, `notebooks/`, `resources/` or `tests/` is missing, or `README.md` is empty |
| Notebooks directory contents | `notebooks/` contains anything other than `.ipynb` files and `README.md` files |
| Run unit tests | Any test in `tests/unit/` fails: job definition, notebook Python and SQL syntax, seed data rules, or DQ docs alignment for Silver, Gold and Analytics (see [`tests/README.md`](../../tests/README.md)) |

Test dependencies are pinned in `tests/requirements.txt`.

### Job 2: Validate Databricks bundle

Runs `databricks bundle validate -t dev` against the branch, using the separate GitHub `ci-validate` environment and a low-privilege, validate-only token. Pull requests from branches in this repo can change workflow files, so CI never uses the deploy token in `development`. It checks `databricks.yml` and every job in `resources/jobs/`, including that each `notebook_path` exists.

- A task that points to a notebook not yet on the branch fails this check. Merge the notebook first, then add its task.
- Skipped for pull requests from forks, which cannot read environment secrets.

## CD — `deploy.yml`

### When it runs

- Pushes to `main` that change any of: `databricks.yml`, `resources/**`, `notebooks/**`, `tests/**`, `dashboard/**`, `.github/workflows/deploy.yml`
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

There are two environments, so the deploy token is never exposed to pull-request branches:

| Environment | Used by | Deployment branches | Token |
| --- | --- | --- | --- |
| `development` | `deploy.yml` | **`main` only** | Deploy token |
| `ci-validate` | `ci.yml` (Validate Databricks bundle) | All branches | Separate low-privilege token, used only for `bundle validate` |

Each environment needs these values (**Settings → Environments → \<name\>**):

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
| `Missing GitHub environment variable/secret: ...` | Value not set, or set at repository level instead of in the environment | Add it under **Settings → Environments → development** (deploy) or **ci-validate** (CI) |
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
