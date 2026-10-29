Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Feature matrices at ingest; class letters and DiachronicSeries at compile.
Blocked by:

## Question

How do **Index abbreviations**, **feature matrices**, and **class letters** map into applier-neutral YAML and ASCA at compile time—and what must *not* replace compile mappings?

## Answer

Normalize **feature matrix** synonyms at **ingest** (`feature_mappings` / config). Expand **DiachronicSeries** and **class letters** at **compile** via **`group_mappings`** (bracket-safe expansion, labialized letters, positional slots).

**ASCA `.alias` (`-l`)** is for word (de)romanisation only—it does **not** substitute for compile-time class-letter expansion in rules.

## Comments

- Migrated summary (2026-10-29): abbreviation resolution, feature spikes, alias-vs-group-mappings grill merged.
