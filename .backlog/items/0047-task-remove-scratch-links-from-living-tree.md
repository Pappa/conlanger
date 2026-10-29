Type: epic-duck:task
Status: resolved
Plan: [0001-plan-migrate-project-to-duck-skills.md](0001-plan-migrate-project-to-duck-skills.md)
Overview: Strip or retarget legacy wayfinder path references outside the deleted tree (docs, ADRs, backlog, src, tests).
Blocked by:

## Question

Deliver [0045](../items/0045-decision-duck-skills-cutover-agent-docs-and-scratch.md) **Answer** § Living links and § Research artefacts (drop refs, no moves).

## Answer

- Stripped markdown links to the legacy wayfinder tree across `docs/`, `.backlog/`, and `src/`; replaced bare path strings per 0045 Q11–Q12.
- `rg '\.scratch' --glob '!.git/**'` returns no matches on the living tree before directory deletion.
- **`Status: resolved`**; parent plan table synced.

## Comments

- **2026-10-29 (dev-duck):** Link strip pass + string scrub on living files; `SYSTEM.md`, `validate.md`, `index-diachronica-parser.md`, `sample_asca_guess_fixtures.py` cleaned; ruff excludes for deleted tree removed from `pyproject.toml`.
