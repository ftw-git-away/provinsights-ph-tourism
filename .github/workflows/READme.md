# GitHub Actions Workflows

This folder contains automated workflows for validating and deploying the Tuklas Pinas Data Platform.

## Workflows

| File | Purpose | Status |
| --- | --- | --- |
| `ci.yml` | Run automated checks on pull requests and pushes to `main` | Planned |
| `deploy.yml` | Deploy approved changes to the configured environment | Add only when deployment is ready |

## Continuous integration

The CI workflow should:

1. Run for pull requests and pushes to `main`.
2. Install the project’s declared dependencies.
3. Run automated tests using local fixtures.
4. Report failures in the GitHub Actions run.

CI checks should be repeatable and should not depend on live DOT or PSA services. Add Databricks bundle validation after the project has a bundle configuration.

## Deployment and secrets

Keep deployment separate from pull request checks. Store required credentials in protected GitHub environment secrets; never commit credentials or expose them to browser code. Grant workflows only the permissions they need.

