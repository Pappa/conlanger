Type: epic-duck:decision
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: Full-index inventory, artifacts, and operator commands.
Blocked by:

## Question

How do we **inventory** which index rules compile, which fail, and how corrections are tracked over time?

## Answer

Regenerate YAML, then run **`uv run create_index && uv run validate_rules`**. Persist per-rule CSV, summary, **success/error splits**, and an **ok-flip changelog** keyed by rule `source`.

Use inventory outputs to **prioritize correction passes** (sections-all-OK metric, near-miss bands). Details: [validate.md](../../docs/system/validate.md).

## Comments

- Migrated summary (2026-10-29): early inventory, full-index pass, CSV split/changelog decisions merged.
