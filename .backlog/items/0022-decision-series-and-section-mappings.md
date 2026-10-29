Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Correspondence series, section mappings, and skip policy.
Blocked by:

## Question

How are **correspondence-series indices** and **section-local class letters** expanded or configured at parse time?

## Answer

Expand series indices at **parse** when a section map exists; retain **`raw`** with subscripts; unmapped indices remain literal and may fail validation until mapped.

Retire CSV **`series_mappings`**; use **`parser_config`** **`section_mappings`** and **`skip_sections`** for seeded heavy families (document reason). Manual mappings and ingest corrections remain config-driven.

## Comments

- Migrated summary (2026-10-29): series/grill, implement passes, section_mappings merged.
