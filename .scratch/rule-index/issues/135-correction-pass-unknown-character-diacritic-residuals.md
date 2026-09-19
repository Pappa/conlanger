Type: task
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

- [ ] Target tokens listed and sized at claim time
- [ ] Class-first transforms only ([ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md))
- [ ] Full inventory re-run; ok + sections-all-OK before/after
- [ ] Unit tests per token family touched

## References

- [unknown_character_errors.csv](../inventory/error_clusters/unknown_character_errors.csv)
- [42 spike IPA mappings](../issues/42-spike-unknown-character-ipa-mappings.md)
- [Correction pass template](13-correction-pass-template.md)
