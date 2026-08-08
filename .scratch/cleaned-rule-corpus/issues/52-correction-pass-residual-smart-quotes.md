Type: task
Blocked by: 12, 24

# Correction pass: residual smart quotes

Target cluster: `unknown_character` — residual typographic quotes **`"`** **`"`** **`'`** (U+201C/U+201D/U+2019) — **57** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

Ticket [24](24-correction-pass-smart-quotes.md) added `strip_embedded_quoted_gloss_from_field()` and `normalize_typographic_apostrophes()`, fixing **+168** ok. Residual smart-quote `unknown_character` failures remain (**57** rows): embedded glosses the first pass missed, field-boundary orphans, or quote-adjacent stress marks misclassified as quotes.

## What to build

1. Audit residual rows in [asca-rule-inventory-error.csv](../inventory/asca-rule-inventory-error.csv) where `error_token` ∈ `"` `"` `'`.
2. Extend parse-time strip/normalise (or move prose to `comment`) for patterns ticket 24 did not cover.
3. Full inventory re-run; record per-token before/after.

**Expected impact:** ~**48** ok uplift at ~85% recoverability.

## Policy

- Editorial quotes → `comment` or ASCII strip; phonological apostrophe → U+02BC (continue ticket 24 policy).
- `raw` unchanged.

## Acceptance criteria

- [ ] Residual pattern audit documented (sample lines per sub-pattern)
- [ ] Extended strip/normaliser + tests
- [ ] Full inventory re-baseline; `"` / `"` / `'` token counts in **Answer**
- [ ] Fixtures updated where outcomes change

## Answer

_(pending)_

## References

- [Correction pass: smart quotes](24-correction-pass-smart-quotes.md)
- [Correction pass template](13-correction-pass-template.md)
