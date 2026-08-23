# Prefer one index rule per Index Diachronica rule line

Index Diachronica rules that express several related changes on one line should normally become **one entry** in the applier-neutral YAML rule index, using internal alternation/set (or equivalent) structure. Do not routinely explode them into separate index rules at ingest.

**Exception:** some edge cases cannot be represented faithfully as a single structured entry for every target applier. In those cases, splitting (or another explicit decomposition) is allowed, but it should be rare, visible, and justified — not the default.

## Considered Options

- **One index rule with internal structure (chosen, with edge-case escapes)** — preserves author grouping; compilers may expand for ASCA/Brassica.
- **Always split at ingest** — simpler rows; loses that the HTML presented one rule.
- **Always keep opaque strings** — maximum fidelity; weakens structured compile/validation.

## Consequences

- Default ingest path aims for 1 HTML rule line → 1 index rule.
- Edge-case splits should be detectable (flag, comment, or dedicated shape) so they do not silently look like independent changes.
- ASCA/Brassica compilers may further expand sets when the applier requires it; that is compile-time, not a license to always split at ingest.
- **Amendment (2026-08-09):** index rules store a **`stages`** list (ADR-0011), not `input`/`output` strings; compile expands adjacent pairs.
