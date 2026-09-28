# GiitAway Team Workflow

These working agreements help GitAway build one reviewable capstone together. The repository is the source of truth for code and project documentation; the GitHub Project is the source of truth for task status and target dates.

## Before starting work

1. Pick an issue or create one using the appropriate form in GitHub.
2. Check its owner, reviewer, acceptance criteria, and dependencies.
3. If the work depends on a source or design decision, link that blocker. Do not treat an unverified source assumption as settled.
4. Keep one person accountable for each issue. Teammates can contribute, pair, or review without obscuring ownership.

## Branches and commits

- Do not commit directly to `main`.
- Branch from the latest `main` using:
  - `feature/issue-<number>-<short-name>` for implementation
  - `docs/issue-<number>-<short-name>` for documentation
  - `fix/issue-<number>-<short-name>` for corrections
- Keep each change focused and commit in understandable increments.
- Use commit messages that say what changed, such as `Document tourism source feasibility`.

## Pull requests and review

- Open a pull request into `main` and link the issue with `Closes #<number>` when it fully completes that issue.
- Summarize the change, why it is needed, and how it was checked.
- Include validation evidence: commands or notebooks run, sample size or row counts where relevant, quality-check results, and anything not checked.
- Update the relevant documentation in the same PR. Start with [the docs index](docs/README.md) when one is available; current project references are [source guidance](docs/data-sources.md), [architecture](docs/architecture.md), and [run status](docs/runbook.md).
- Ask the named reviewer to check the change against the issue’s acceptance criteria. Address review comments before merge.
- Merge only after review and any applicable CI checks pass. The project lead coordinates merges.

## Data and source handling

- Use public sources approved for the project and record attribution, license or terms, retrieval date, coverage, and limitations in the [source inventory](https://docs.google.com/spreadsheets/d/18tTQHJLcJrIFVfNzgvT97ZMM6PfJNnAL/edit?gid=1004909730#gid=1004909730).
- Do not commit credentials, tokens, private data, or raw datasets. Store project data in the approved Databricks workspace or other agreed storage.
- Do not silently drop records. Document exclusions and retain a reason that can be reviewed.
- Do not claim comparability across sources until definitions, time periods, geographic levels, and join keys have been checked.
- Keep sample data synthetic or small and redistributable; verify source terms before including it.

## AI-assisted work

AI tools may help explain concepts, draft boilerplate, review code, and improve documentation. The contributor remains responsible for every change.

- Never send credentials, private data, or information the source terms do not allow you to share.
- Verify generated facts, SQL, transformations, and quality rules against the source and the project requirements.
- Make sure you can explain and defend the result before requesting review.
- State material AI assistance in the PR when it helped produce code or analysis. A human must verify the output and evidence.

## Project references

- [README: current scope and project status](README.md)
- [Source discovery guidance](docs/data-sources.md)
- [Proposed architecture and open choices](docs/architecture.md)
- [Current run status and future runbook](docs/runbook.md)
