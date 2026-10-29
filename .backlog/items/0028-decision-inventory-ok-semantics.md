Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: FAILED/OK/SKIPPED inventory, validate-all-targets, per-field blame.
Blocked by:

## Question

What do **inventory ok values** mean, and how is compile validation run across compile targets?

## Answer

Inventory **`ok`** is a string enum: **`FAILED`**, **`OK`**, **`SKIPPED`** (not numeric 0/1/2). **`validate_rules`** exercises compile targets consistently; optional **per-field blame** attributes failures when implemented.

Use the **forked ASCA `validate`** integration for compile checks. Compiled YAML serde validation avoids false failures from series round-trip where fixed.

## Comments

- Migrated summary (2026-10-29): ok enum, validate-all-targets, native per-field validation spike outcomes merged.
