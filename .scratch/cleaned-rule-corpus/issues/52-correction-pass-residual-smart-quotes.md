Type: task
Status: resolved
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

- [x] Residual pattern audit documented (sample lines per sub-pattern)
- [x] Extended strip/normaliser + tests
- [x] Full inventory re-baseline; `"` / `"` / `'` token counts in **Answer**
- [x] Fixtures updated where outcomes change

## Answer

Baseline (after issue 57): **7134 / 9201** ok (77.5%).

### Residual audit (57 rows)

| Sub-pattern | count | sample | fix |
|-------------|------:|--------|-----|
| Stress-adjacent `”` (lookahead bug, `//`, `_`, `*`, sets, infix, output) | 39 | `// ”ə_V`, `a"a`, `C"iC_`, `#_"a` | `normalize_stress_marks()` expansion |
| Typographic apostrophe `'` (prefix, paren, Greek θ) | 12 | `'p 't`, `p(')`, `θ'` | `normalize_typographic_apostrophes()` |
| Prose glosses `"`/`"` | 3 | `hhy > "something like /ʒ/"`, `"The CIV rules…"` | field-wrapped/leading gloss + prose skip |
| Other stress orphans | 3 | `P"_(C,0)B`, `V(C)"(C)CaCV` | class-before-`_`, `)"(` patterns |

### Per-token `unknown_character` counts

| token | before | after |
|-------|-------:|------:|
| `"` (U+201C) | 3 | **0** |
| `"` (U+201D) | 42 | **0** |
| `'` (U+2019) | 12 | **0** |

Full inventory re-run: **7178 / 9201** ok (**+44**, **78.0%**). Two long quoted paragraphs marked `skipped: quoted prose paragraph`.

## References

- [Correction pass: smart quotes](24-correction-pass-smart-quotes.md)
- [Correction pass template](13-correction-pass-template.md)
