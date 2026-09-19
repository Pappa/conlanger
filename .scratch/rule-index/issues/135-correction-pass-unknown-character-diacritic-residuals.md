Type: task
Status: resolved
Blocked by: [49](49-correction-pass-ipa-letter-mappings.md)

# Correction pass: `unknown_character` diacritic and subscript residuals

Target cluster: `unknown_character` — **71** failing rules at current inventory; top `error_token` counts: **`ː`** (7), **`₂`** (7), **`͜`** (6), **`ŕ`** (6), **`̺`** (6), **`ₙ`** (5), combining marks **`̂`/`̻`/`̊`/`̚`/`̀`**, **`ʝ`** (2). Spawned from `/grill-with-docs` on [map.md](../map.md) (2026-09-19). Follow-on to [63 near-miss unknown_character](63-correction-pass-near-miss-unknown-character.md) (resolved 2026-08-19).

## Problem

Residual letter-like tokens are mostly **Unicode diacritics**, **subscript digits**, and **non-IPA modifiers** not covered by `ipa_mappings.yml` or existing compile passes (length marks, breve, superscript modifiers, ejectives).

Examples from inventory:

```
t > t͜s          (unknown_character '͜' — ligature tie)
…₂…             (subscript tone/digit ₂)
ŕ               (acute on r — Polish etc.)
```

Some `ː` rows may overlap [104 `(ː)`](104-correction-pass-parenthesized-optional-length-marker.md) / bare length hold-outs — classify before implementing.

## What to build

1. Re-pull `unknown_character_errors.csv`; group by token and section; note mono-class sections.

2. **Class-first fixes** per token family:
   - **IPA mappings** (`ipa_mappings.yml`) for letter+diaeresis/acute variants with high confidence.
   - **Compile normalisation** for combining marks with stable ASCA feature or segment targets (mirror ticket 50/110 patterns).
   - **Subscript digits `₂` etc.:** distinguish Index positional/tone notation ([40](40-correction-pass-positional-identity-subscripts.md)) vs spurious OCR — defer collective `ₓ` to series/section mappings when applicable.

3. Do not add low-confidence hacks; use parser config confidence levels.

4. Full inventory re-run; `unknown_character` cluster delta in **Answer**.

## Acceptance criteria

- [x] Target tokens listed and sized at claim time
- [x] Class-first transforms only ([ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md))
- [x] Full inventory re-run; ok + sections-all-OK before/after
- [x] Unit tests per token family touched

## Answer

**Claim-time cluster (2026-09-19):** **73** `unknown_character` rows; top tokens `ː` (10), `₂` (7), `͜` (6), `ŕ` (6), `̺` (6), `ₙ` (5), combining `̂`/`̻`/`̊`/`̚`/`̀`, `ʝ` (2).

**Shipped transforms**

| Family | Lever | Module / config |
|--------|--------|-----------------|
| `͜` tie bar | `͜` → `͡`; dangling-tie cleanup | `tie_bars.py` |
| Segment diacritics | Basque `s̺`/`s̻`, Polish `r̝`, Tuscarora voiceless ring, Obokuitai `̚`, Muskogean `V̂`, Elamite/Tupí `ŕ`/`r̀`/`*ŕ`, prose `C₂` in `//` tails | `segment_diacritics.py` |
| `ˑ` half-length | suffix → `:[+long]` | `length_marks.py` |
| Uto-Aztecan `Vₙ`/`Vₛ`/`Vᵤ`, `aₙ`, `ɨₙ` | section series mappings | `compiler_config.yml` §43 |
| Bantu `d₂` | section series mapping | `compiler_config.yml` §30 |
| IPA letters | `ŕ`, `r̀`, `ĩ`, `Ạ` confidence / targets | `ipa_mappings.yml` |

**Inventory (ASCA 0.10.3, full `validate_rules`)**

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK / rows | 8950 / 9839 (91.0%) | **8999 / 9839 (91.5%)** | **+49** |
| Sections all OK | 486 / 714 (68.1%) | **501 / 714 (70.2%)** | **+15** |
| `unknown_character` rows | 73 | **28** | **−45** |

**Residual `unknown_character` (28):** mostly `ː` stress/meta hold-outs (10), Romance `// C₂` prose slots (3), Khoisan / Pekingese dangling `͡` (3), Spanish bracket / `ʝ` (2), Tupí `*ŕ` (4), Marshallese `ᵚ`, Aquitanian `〈`, Basque prose tail `̺`, Totonacan `ḭ`, `#` list artefact (1 each). `*ŕ` left unmapped at compile (avoid `r > r` identity on Cavineña); follow parse/manual or skip. Follow-ons: length meta ([64](64-spike-syntax-other-near-miss-sections.md)), [136](136-correction-pass-khoisan-click-invalid-ipa.md), Spanish I/O brackets.

**Tests:** `test_tie_bars.py`, `test_segment_diacritics.py`, `test_length_marks.py` (half-length cases).

## References

- [unknown_character_errors.csv](../inventory/error_clusters/unknown_character_errors.csv)
- [42 spike IPA mappings](../issues/42-spike-unknown-character-ipa-mappings.md)
- [Correction pass template](13-correction-pass-template.md)
