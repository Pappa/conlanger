Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Minimal HTML→YAML ingest and parse-time surface normalization bounds.
Blocked by:

## Question

What does **minimal extract-only ingest** produce, and which Index surface cleanups belong in parse vs compile?

## Answer

**`IndexDiachronicaParser`** emits applier-neutral YAML (`create_index` / `data/diachronica/index_diachronica.yml`). Parse-time work includes arrows, em dashes, chain split, gloss/stress/sporadic stripping, and related **typographic** normalization.

Do **not** store ASCA-only literals in SoT unless they are defensible as **applier-agnostic** canonical surface. Class-letter expansion and ASCA env shapes belong at **compile** (or structured **IndexContext**, not raw ASCA in YAML).

## Comments

- Migrated summary (2026-10-29): minimal ingest + early parse-normalization decisions merged.
