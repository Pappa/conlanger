Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Ingest/compile seams, operator split, compiled YAML monitoring, position.in.
Blocked by:

## Question

How are **ingest**, **compile**, and **operator scripts** bounded after applier-neutral SoT hygiene work (2026)?

## Answer

Enforce **import boundaries**: ingest must not import compile. Move ASCA-shaped rewrites out of applier-neutral SoT where required; **reorder env pipeline** parse → structured context → compile.

Split **`compile_rules`** from **`validate_rules`** on **compiled YAML**; emit **`asca_rules.yml`** as monitoring artifact. Implement **`position.in`** compile projection per relation inventory policy.

## Comments

- Migrated summary (2026-10-29): Oct 2026 parse/compile hygiene grill+task cluster merged.
