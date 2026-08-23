Type: task
Status: ready-for-agent
Blocked by:

# Correction pass: matrix-suffix length marker `ː`

Target cluster: `unknown_character` — residual error_token **`ː`** after tickets [15](15-correction-pass-length-marker.md) / [25](25-correction-pass-bare-length-marker.md) — **23** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from sizing after [63 near-miss unknown_character](63-correction-pass-near-miss-unknown-character.md) (2026-08-19).

## Context

`normalize_asca_length_marks()` in `src/conlanger/tools/compile/asca/length_marks.py` already handles segment+length (`pː` → `p:[+long]`), set suffixes, ref digits (`2ː`), and inter-matrix `]ː[`. **Residual** `ː` hits are mostly **matrix-suffix** forms ASCA never sees:

| Subcluster | rows (approx.) | Example |
|---|---:|---|
| Matrix + `ː` in env/output | 11 | `V:[+stress]ː`, `V:[+stress] > V:[+stress]ː` |
| Matrix suffix before token | 2 | `P[- voice]ː` |
| Template optional length | 3 | `V3(ː)ʔ` (Salish) |
| Iroquoian stress meta | 3 | `ː2`, complex stressed sets |
| Other / already OK in pipeline | 4 | NW Caucasian `p(ʲ)ː` in sets — verify inventory drift |

Prototype (2026-08-19): extend compile pass with `Matrix]ː` → `Matrix, +long]` (+ optional `V3(ː)` → `V3:[+long]`) fixes **~10** of 23 rules. **0** sections become all-OK (every `ː` section has other failure classes). Near-miss (≤3-fail) leverage: **1 / 23** rows.

## What to build

1. Extend `normalize_asca_length_marks()` for matrix-suffix `ː` (and `Vn(ː)` template optional length if cheap).
2. Unit tests in `tests/conlanger/tools/compile/asca/` mirroring ticket 25 style.
3. Full inventory re-run; record before/after for `ː` and sections-all-OK.
4. Do **not** tackle Iroquoian `ː2` / stress-meta shapes in this pass — defer to meta-notation / ticket 64 follow-ons.

## Policy

- Compile-layer fix only; index YAML `raw` unchanged (ADR-0010).
- Class-first mechanical transform — same edit ladder as tickets 15/25.

## Acceptance criteria

- [ ] Matrix-suffix `ː` patterns documented with ASCA smoke examples
- [ ] `normalize_asca_length_marks()` extended; Iroquoian meta hold-outs listed
- [ ] Full inventory re-run; before/after ok + `ː` residual count in **Answer**
- [ ] Fixtures updated where validation outcomes change

## References

- [Correction pass: length marker ː](15-correction-pass-length-marker.md)
- [Correction pass: remaining bare length marker ː](25-correction-pass-bare-length-marker.md)
- [Correction pass: near-miss unknown_character](63-correction-pass-near-miss-unknown-character.md)
- [ASCA compile transform order](../research/asca-compile-transform-order.md)
- [Correction pass template](13-correction-pass-template.md)
