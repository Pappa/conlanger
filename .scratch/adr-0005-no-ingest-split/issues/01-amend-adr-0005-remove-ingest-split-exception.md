Type: grilling
Status: resolved
Blocked by:

# Amend ADR-0005 — remove ingest-split exception

## Question

What exactly replaces the current ADR-0005 **exception** (“splitting or another explicit decomposition is allowed” for edge cases)? Confirm the amended policy:

1. **Never** inflate corpus row count at ingest for multi-change lines (chains or otherwise).
2. **Compile-time** expansion is the only way to produce sequential applier rules from one corpus row.
3. When a line cannot be represented faithfully as one corpus rule **and** cannot compile — use `status: skipped` per ADR-0010, **not** ingest split.

Does the amended ADR also explicitly **supersede** [Correction pass: chained rules — parse-time split](../cleaned-rule-corpus/issues/18-correction-pass-chain-split.md) as contrary policy?

## Answer

**Confirmed (grill 2026-08-07):**

1. **Never** inflate corpus row count at ingest for multi-change lines.
2. **Compile-time** expansion is the only path from one corpus row to sequential applier rules.
3. Truly unrepresentable lines → `status: skipped` per ADR-0010, **not** ingest split.
4. **Supersedes** [ticket 18](../cleaned-rule-corpus/issues/18-correction-pass-chain-split.md) parse-time chain split as contrary policy.
5. **YAML shape:** keep opaque `input`/`output` strings (no `steps:` array); chains stay as multi-segment `output` (e.g. `tʃ > ʃ`).
6. **Delivery:** [Revert parse-time chain split](02-revert-parse-time-chain-split.md) and [Compile-time chain expansion](03-compile-time-chain-expansion.md) are **separate tickets** — revert may land before compile expansion (temporary inventory regression acceptable).

Amended ADR text to be written in [Update docs and parent cleaned-corpus map](05-update-docs-and-parent-map.md).
