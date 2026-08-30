Type: task
Status: needs-triage
Blocked by: 94

# Correction pass: parenthesized optional length marker `(ː)`

Target cluster: `unknown_character` — residual error_token **`ː`** in parenthesized optional-length shapes — **≥4** rules at current inventory baseline (plus broader policy surface across the index).

Spawned from rework of [79 matrix-suffix `ː`](79-correction-pass-matrix-suffix-length-marker.md) (2026-08-30): matrix-suffix `]ː` is scoped correctly; `(ː)` is **not** the same notation.

## Context

Index uses `(ː)` for **optional length** on a segment, matrix, or template token — distinct from bare suffix `ː` after a feature matrix (`V:[+stress]ː`, ticket 79).

| Subcluster | rows (approx.) | Example | Notes |
|---|---:|---|---|
| Matrix + `(ː)` in env | 1 | `_V:[+front](ː)` | Tocharian 17.13 |
| Template `(ː)` | 3 | `V3(ː)ʔ`, `V3(ː)` | Salish positional vowels |
| Segment `(ː)` collapse | many | `e(ː)`, `a(ː)` | ticket 15 maps to `segment:[+long]` only |
| Segment + modifier + `ː` | 3+ | `p(ʲ)ː`, `t(ʷ)ː` | NW Caucasian; not parenthesized |
| Iroquoian stress meta | 2+ | `ː2`, `Vː:[+stress]` | defer to meta-notation / ticket 64 |

**Policy tension (ticket 15 vs linguistics):**

- Ticket 15 collapsed `segment(ː)` → `segment:[+long]` because ASCA rejects `(:[+long])`.
- Parenthetical expansion alone on `e(ː)` yields `{e, eː}` → `{e, e:[+long]}` if length marks run **after** parenthetical — optional-length semantics.
- `e(ː,j)` already expands via `_OPT_LENGTH_COMMA_RE` to `{e:[+long], ej}` — inconsistent with bare `e(ː)`.

**Pipeline order today:** `normalize_asca_length_marks()` runs **before** `expand_index_parenthetical_notation()` in `compile_asca_field_post_subscript`, so `(ː)` is collapsed before parenthetical can emit alternates.

## What to build

**Blocked by [grill 94](94-grill-structured-soundchangerule-ir.md)** — implementation must follow IR / transform-order decisions from that session (optional-length may belong in parenthetical IR, a dedicated optional-length pass, or reordered string transforms).

When unblocked:

1. Lock policy for parenthesized optional length: collapse to `:[+long]` vs expand to `{segment, segment:[+long]}` (and matrix/template analogues).
2. Implement at the agreed compile layer (`parenthetical.py`, `length_marks.py` order, or IR walk) — not matrix-suffix regex in `length_marks`.
3. Unit tests in `tests/conlanger/tools/compile/asca/`; ASCA smoke on representative rows (Tocharian env, Salish `V3(ː)`).
4. Full inventory re-run; record before/after for `ː` residual and ok-flips.
5. Hold out Iroquoian `ː2` / stress-meta shapes (ticket 64 follow-ons).

## Acceptance criteria

- [ ] Policy for `(ː)` optional length recorded (link from grill 94 Answer)
- [ ] Parenthesized optional-length shapes compile without `unknown_character` `ː` where policy allows
- [ ] `e(ː)` and `e(ː,j)` handled consistently per locked policy
- [ ] Full inventory re-run; before/after metrics in **Answer**
- [ ] Fixtures updated where validation outcomes change

## References

- [Correction pass: matrix-suffix `ː`](79-correction-pass-matrix-suffix-length-marker.md) — scoped to `]ː` only
- [Correction pass: length marker `ː`](15-correction-pass-length-marker.md)
- [Correction pass: parenthetical segment notation](48-correction-pass-parenthetical-segment-notation.md)
- [Grill: parenthetical + parallel-set notation](71-grill-paren-and-parallel-set-notation.md)
- [Spike: Index I/O optionals vs ASCA](100-spike-io-optionals-asca-and-convention.md)
- [Grill: structured compile IR on SoundChangeRule](94-grill-structured-soundchangerule-ir.md)
- `src/conlanger/tools/compile/asca/length_marks.py`, `parenthetical.py`, `pipeline.py`
