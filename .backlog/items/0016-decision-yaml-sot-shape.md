Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Applier-neutral YAML schema and stages spine for the cleaned index.
Blocked by:

## Question

What **YAML shape** is the long-term applier-neutral source of truth for the cleaned rule index, and how are multi-stage rules represented?

## Answer

The SoT file has top-level **`abbreviations`** and **`sections`**. Each rule carries a uniform **`stages`** list (adjacent pairs expanded at compile), plus **`raw`**, **`source`**, and optional fields (`env`, `exception`, `status`, `sporadic`, `comment`, etc.) per [ADR-0011](../../docs/adr/0011-index-rule-stages.md).

**Index Diachronica HTML** is the historical ingest source; **cleaned YAML** is the working SoT consumed by parse → compile → validate.

## Comments

- Migrated summary (2026-10-29): schema + stages cutover decisions merged.
