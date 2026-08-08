Type: task
Blocked by: 12

# Correction pass: prose env medial

Target cluster: `expected_underscore` — prose environment **`medial`** / **`medially`** — **52** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

Rules use English position words in the env field where ASCA expects `_` focus, e.g.:

```
t > r / medially
t > j / medially
```

Error: `Expected '_', but received ''`.

Distinct from ticket [22](22-correction-pass-stress-conditions.md) (stress prose) and [53](53-correction-pass-prose-env-else.md) (`else` catch-alls).

## What to build

1. Classify medial-position claims — intervocalic (`V_V`), word-medial (`#_` / `_#` combinations), adjacent-consonant contexts.
2. Implement env rewrite templates mapping `medial`/`medially` to ASCA env patterns faithful to the section claim.
3. Full inventory re-run; record before/after for env prose containing `medial`.

**Expected impact:** ~**26** ok uplift at ~50% recoverability.

## Policy

- `raw` unchanged; no valid-but-inaccurate env guesses.
- Unmappable prose → `comment` + stub env or `status: skipped` with validation report reason.

## Acceptance criteria

- [ ] Medial pattern taxonomy with compile examples
- [ ] Handler(s) + tests on inventory samples
- [ ] Full inventory re-baseline; cluster size in **Answer**
- [ ] Fixtures updated where outcomes change

## Answer

_(pending)_

## References

- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: prose env else](53-correction-pass-prose-env-else.md)
- [Correction pass: stress conditions](22-correction-pass-stress-conditions.md)
