Type: task
Blocked by: 12

# Correction pass: input optionals to env

Target cluster: `syntax_other` — **`Options can only be used in Environments or Structures`** — **86** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

ASCA permits optionals `(…)` only in environments or structures, not in bare I/O segments. Index writes input-side optionals such as `(G)V > ∅ / _#` that fail at compile validation.

## What to build

1. Identify recurring input-optional shapes in the cluster (e.g. `(C)V`, `(G)V`, prefixed optional consonants).
2. Implement parse/compile rewrite — move optionals into ASCA env/structure positions or expand to equivalent set notation `{…}` where faithful.
3. Full inventory re-run; record before/after for rows matching the exact error message.

**Expected impact:** ~**51** ok uplift at ~60% recoverability.

## Policy

- Preserve optional semantics; do not drop the optional branch silently.
- `raw` unchanged; class-first transform per edit ladder.

## Acceptance criteria

- [ ] Dominant optional-in-input patterns documented
- [ ] Handler(s) + tests on inventory samples (e.g. `(G)V > ∅ / _#`)
- [ ] Full inventory re-baseline; cluster size before/after in **Answer**
- [ ] Fixtures updated where outcomes change

## Answer

_(pending)_

## References

- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: parenthetical segment notation](48-correction-pass-parenthetical-segment-notation.md) — overlapping `(` handling
