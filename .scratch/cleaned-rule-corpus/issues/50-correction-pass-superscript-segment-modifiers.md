Type: task
Blocked by: 12, 23

# Correction pass: superscript segment modifiers

Target cluster: `syntax_other` — superscript modifiers **`ʷ`** / **`ʲ`** / **`ʰ`** / **`ʱ`** in I/O segments — **125** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

Ticket [23](23-correction-pass-labialized-class-letters.md) handled class-letter + `ʷ` (e.g. `Cʷ`). A larger cluster remains where superscripts attach to **segments** or appear in env-adjacent positions:

| received token | count |
|----------------|------:|
| `ʷ` | 60 |
| `ʲ` | 18 |
| `ʰ` | 18 |
| `ʱ` | 7 |

Examples: `{x,ɢ}(ʷ) > ∅`, `tɬ:[+long](ʼ)`, `mV[-long] > ∅ / #_{ʰC,s,ʃ}`.

## What to build

1. Extend compile-time superscript normalisation beyond ticket 23 — segment-level labialization/palatalization/aspiration (Unicode `ʷ` U+02B7, `ʲ` U+02B2, `ʰ` U+02B0, `ʱ` U+02B1).
2. Map to ASCA feature matrices or segment literals ASCA accepts (e.g. `ʷ` → `:[+labial]` on host segment, or decomposed IPA).
3. Full inventory re-run; record before/after for superscript-related `syntax_other` rows.

**Expected impact:** ~**56** ok uplift at ~45% recoverability.

## Policy

- Compile-layer fix preferred; `raw` unchanged (ADR-0010).
- Preserve ticket 23 regressions (`Kr`, `Kw`, `rK` class-letter boundaries).

## Acceptance criteria

- [ ] Superscript attachment patterns documented (segment vs env)
- [ ] Handler(s) + tests including ticket 23 regression fixtures
- [ ] Full inventory re-baseline; per-token residual counts in **Answer**
- [ ] Fixtures updated where outcomes change

## Answer

_(pending)_

## References

- [Correction pass: labialized class letters](23-correction-pass-labialized-class-letters.md)
- [Correction pass template](13-correction-pass-template.md)
