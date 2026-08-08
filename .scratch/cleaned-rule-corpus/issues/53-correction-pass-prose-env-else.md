Type: task
Blocked by: 12

# Correction pass: prose env `else`

Target cluster: `expected_underscore` — prose environment keyword **`else`** — **85** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

Rules carry English `else` branches in the env field where ASCA expects `_` focus syntax, e.g.:

```
{xʷ,ɢʷ} > w / else
k:[+cg] > q / else
```

Error: `Expected '_', but received ''` (prose env fragment).

## What to build

1. Identify `else` env patterns — default-branch rules vs paired exception structures.
2. Implement env rewrite: map `else` catch-alls to ASCA env + `|` exception syntax, or strip to `comment` + synthesise `#_` stub where the claim is env-less.
3. Full inventory re-run; record before/after for env prose containing `else`.

**Expected impact:** ~**46** ok uplift at ~55% recoverability.

### Out of scope (separate tickets)

- `medial` / `medially` — [55](55-correction-pass-prose-env-medial.md)
- `stressed` / `unstressed` — partial overlap with [22](22-correction-pass-stress-conditions.md)

## Policy

- Preserve branch semantics where possible; `raw` unchanged.
- Prose-only env tails → `comment` per edit ladder when ASCA cannot express the claim.

## Acceptance criteria

- [ ] `else` pattern taxonomy with compile before/after examples
- [ ] Handler(s) + tests on inventory samples
- [ ] Full inventory re-baseline; `else` cluster size in **Answer**
- [ ] Fixtures updated where outcomes change

## Answer

_(pending)_

## References

- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: stress conditions](22-correction-pass-stress-conditions.md)
