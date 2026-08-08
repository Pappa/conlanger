Type: task
Blocked by: 12

# Correction pass: parenthetical segment notation

Target cluster: `syntax_other` — parenthetical **`(`** in I/O segments — **144** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

Rules fail when Index wraps optional or alternation material in parentheses inside segments:

| Bucket | count | example |
|--------|------:|---------|
| `Expected end of line, received '('` | 87 | `z dz ɡ > ɡ {z,dz} ɡ(ʷ)` |
| `Expected … received '('` | 57 | `a > o / #Cw_{(d)l,f3}` |

ASCA rejects `(` in segment position outside env/structure optionals.

## What to build

1. Classify parenthetical uses: optional segment tail (`ɡ(ʷ)`), inline alternation `{(d)l,f3}`, output affix optionals, etc.
2. Implement parse and/or compile transforms — unwrap to ASCA sets `{…}`, move optionals into env/structures, or strip to `comment` when prose-only.
3. Full inventory re-run; record before/after for `syntax_other` rows whose description contains `received '('` or `received '(`.

**Expected impact:** ~**64** ok uplift at ~45% recoverability.

## Policy

- ADR-0010: no valid-but-inaccurate rewrites; `raw` preserved.
- Distinguish phonological optionals from editorial parentheticals (latter → `comment` per edit ladder).

## Acceptance criteria

- [ ] Parenthetical pattern taxonomy documented with compile examples
- [ ] Handler(s) + tests on representative lines from inventory
- [ ] Full inventory re-baseline; metrics in **Answer**
- [ ] Fixtures updated where outcomes change

## Answer

_(pending)_

## References

- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: input optionals to env](51-correction-pass-input-optionals-to-env.md) — related options placement
