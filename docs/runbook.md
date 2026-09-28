# Runbook

## Current status

There is no runnable data pipeline, Databricks job, API, or dashboard in the repository yet. The folders and `resources/jobs/tourism_pipeline.yml` are scaffolding/placeholders. No local setup or execution command is available at this stage.

Do not treat this file as proof that a pipeline has run. Update it when a runnable component is added, and include exact prerequisites and expected results.

## What the team can do now

1. Review candidate sources using the [source inventory sheet](https://docs.google.com/spreadsheets/d/18tTQHJLcJrIFVfNzgvT97ZMM6PfJNnAL/edit?gid=1004909730#gid=1004909730).
2. Follow the issue, branch, and pull request process in [CONTRIBUTING.md](../CONTRIBUTING.md).
3. Read [the provisional architecture](architecture.md) and keep unresolved choices explicit.
4. Check GitHub Actions after a workflow is implemented; the current `.github/workflows/ci.yml` is empty.

## Required contents when implementation starts

For each pipeline or application entry point, document:

- Prerequisites, supported runtime, and required packages
- How to configure access without committing secrets
- Exact command or Databricks steps to run it
- Expected input and output tables/files, with grain and schema references
- Expected row counts or quality-check outcomes for a small fixture
- Failure behavior, safe rerun instructions, and troubleshooting guidance
- Which steps require Databricks or external access and cannot run in GitHub Actions
