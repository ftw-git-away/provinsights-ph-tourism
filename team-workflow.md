# GitAway working agreement

**Version:** 1, proposed for team review  
**Project:** Tuklas Pinas Data Platform

These rules are written for GitAway's capstone, source-first project stage, five-person team, and course handoff rubric. They can change when the team records a decision in an issue and updates this page.

## 1. Source evidence comes before final schema decisions

- Treat DOT, PSA, and PSGC as candidate publishers until a specific dataset has been inspected.
- For each candidate, one owner records the official URL, measure/definition, geography, time coverage, granularity, access method, metadata, terms, observed quality, limitations, and evidence in the shared source inventory.
- Mark assumptions as assumptions. A landing page alone is not evidence that a dataset is usable.
- Before calling a source feasible, inspect a representative sample or file and explain how it could support a project question.
- Do not lock the MVP, final schema, or join strategy until the team has reviewed the source evidence and agreed on the supported question, geographic unit, time window, and limitations.
- Keep independent work moving: draft questions, inspect metadata, outline candidate fields, or prepare a mock input while a source access issue is unresolved. Label mock-based work as provisional.

## 2. Keep project records in the right place

- **GitHub Issues** hold task scope, one accountable owner, acceptance criteria, blockers, and evidence links.
- **The GitHub Project board** shows current status and target dates.
- **The source inventory sheet** holds one row per candidate dataset and its evidence.
- **Repository documentation** holds the current project scope, approved decisions, data model, architecture, run instructions, and quality results.
- When these records disagree, flag the mismatch in the related issue and update the source of truth for that information.

## 3. Share work by outcome, not by pipeline phase

- Give every issue one accountable owner. A reviewer or collaborator can help without splitting accountability.
- Write issues around reviewable outcomes. State what is included, what is out of scope, how completion will be shown, and what blocks the work.
- Assign a different reviewer when another teammate is available.
- A dependency blocks only the work that needs it. Teammates may start independent source research, documentation, mock-input work, or design drafts in parallel.
- Revisit assignments when a blocker threatens a checkpoint; rebalance work rather than leaving a teammate waiting.

## 4. Protect the shared branch and make changes reviewable

- Do not push commits directly to `main`. Use a short-lived branch named `task/<issue-number>-<short-name>`.
- Keep a pull request focused on its issue. Link the issue; say what changed and why; list evidence checked and anything not checked.
- Update the README or the relevant source, architecture, model, or run documentation in the same pull request when the change makes it stale.
- A teammate reviews the change against the issue's acceptance criteria before merge. The author addresses requested changes; the project lead coordinates the merge.
- Do not claim CI, tests, notebooks, or pipelines passed unless they were run and the result is available. Until CI is implemented, review the evidence that exists and state the limits.

## 5. Keep data traceable and interpretations supportable

- Use sources the team has reviewed for the capstone. Record source URL, retrieval date, attribution/terms, coverage, definitions, and limitations.
- Never commit credentials, tokens, private data, or raw source files whose terms do not allow redistribution. Use only a small, permitted sample when a sample is needed.
- Preserve source lineage through transformations. Do not silently discard rows; document exclusions and their reasons.
- Before joining or comparing datasets, check their definitions, time periods, geographic levels, identifiers, and units. Keep unsupported comparisons out of the public-facing claims.
- For each table or published dataset, document its grain, keys, important fields, and known gaps before asking another engineer to rely on it.

## 6. Make capstone work explainable

- Use AI tools for assistance if useful, but check generated code, SQL, facts, and interpretations against the source and project requirements.
- Mention material AI assistance in the pull request. The contributor must understand the result and be able to explain and defend it.
- Keep decisions, validation evidence, assumptions, limitations, and failed checks in reviewable project records. The team should be able to demonstrate what was done and what remains uncertain.

## 7. Work toward the team's checkpoints

These are the current planning targets from the team's capstone plan; the GitHub Project board carries task status and dates.

- **September 30, 2026:** source feasibility and scope recommendation
- **October 3, 2026:** schema design informed by inspected sources
- **October 10, 2026:** Gold marts
- **October 17, 2026:** analytics/dashboard and certification exam
- **October 24, 2026:** presentation and defense

The team wants to finish earlier where feasible. Replan openly on the board when source evidence or implementation changes a date. Keep each checkpoint tied to reviewable evidence, not only a date or a folder existing.

## Project references

- [Current scope and project status](README.md)
- [Source discovery guidance](docs/data-sources.md)
- [Proposed architecture and open choices](docs/architecture.md)
- [Current run status and future runbook](docs/runbook.md)
- [Shared source inventory and scope feasibility sheet](https://docs.google.com/spreadsheets/d/18tTQHJLcJrIFVfNzgvT97ZMM6PfJNnAL/edit?gid=1004909730#gid=1004909730)
