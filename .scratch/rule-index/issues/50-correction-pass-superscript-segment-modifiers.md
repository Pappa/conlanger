Type: task
Status: resolved
Blocked by: 12, 23

# Correction pass: superscript segment modifiers

Target cluster: `syntax_other` — superscript modifiers **`ʷ`** / **`ʲ`** / **`ʰ`** / **`ʱ`** in I/O segments — **125** rules at current inventory baseline ([summary](../inventory/rule-inventory-summary.md)).

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

## Answer

Baseline (pre-pass, HEAD inventory): **7178 / 9201** ok (78.0%); `syntax_other` **638**; rules whose error description contains `received 'ʷ'`, `'ʲ'`, `'ʰ'`, or `'ʱ'`: **56** (inventory grep on error CSV).

After `normalize_asca_superscript_modifiers` (pipeline step 4, before `apply_asca_group_mappings`):

- **7218 / 9201** ok (**78.4%**, **+40** vs pre-pass baseline)
- `syntax_other` **638 → 618** (−20)
- Residual `received 'ʷ'/'ʲ'/'ʰ'/'ʱ'` parse errors: **ʷ 11**, **ʲ 5**, **ʰ 1**, **ʱ 0** (17 total; mostly IPA-literal suffixes, env-adjacent `k(ʷ)` parentheticals, and prose-adjacent tokens out of scope)
- Taxonomy and compile examples: module docstring in `src/conlanger/tools/asca_compile/superscript_modifiers.py`

## Acceptance criteria

- [x] Superscript attachment patterns documented (segment vs env)
- [x] Handler(s) + tests including ticket 23 regression fixtures
- [x] Full inventory re-baseline; per-token residual counts in **Answer**
- [x] Fixtures updated where outcomes change (inventory CSVs + changelog)

## References

- [Correction pass: labialized class letters](23-correction-pass-labialized-class-letters.md)
- [Correction pass template](13-correction-pass-template.md)
