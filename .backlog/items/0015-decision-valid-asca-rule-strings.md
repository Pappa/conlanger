Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Valid ASCA rule string shape and validation entry point for Index-derived rules.
Blocked by:

## Question

What form must a **compiled ASCA rule string** take for Index Diachronica–derived rules, and what is the preferred validation entry point when checking whether a rule is syntactically acceptable?

## Answer

A valid rule string follows **`input > output [/env] [|exception]`** with non-empty input and output (including `*`, `∅`, and metathesis forms). Environment uses a **single `_` focus**; **`#`** is env-peripheral only.

Prefer ASCA **`ParsedRules::try_from`** (or the project’s wrapped equivalent) for syntactic validation rather than ad hoc string checks. Operator and compile docs live under [sound-change-applier.md](../../docs/system/sound-change-applier.md).

## Comments

- Migrated summary (2026-10-29): legacy foundation + validator decisions merged into this ticket.
