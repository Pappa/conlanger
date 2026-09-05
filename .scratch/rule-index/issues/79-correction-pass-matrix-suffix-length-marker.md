Type: task
Status: resolved
Blocked by:

# Correction pass: matrix-suffix length marker `ː`

Target cluster: `unknown_character` — residual error_token **`ː`** after tickets [15](15-correction-pass-length-marker.md) / [25](25-correction-pass-bare-length-marker.md) — **23** rules at current inventory baseline ([summary](../inventory/rule-inventory-summary.md)).

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

## What was built

Extended `normalize_asca_length_marks()` in `length_marks.py`:

- `Matrix]ː` → `Matrix, +long]` (matrix-suffix length; stress/tone env+I/O)
- `(?!:)` guard on grouping/segment length so `Vː:[+stress]` Iroquoian hold-outs stay literal

**Deferred (2026-08-30 rework):** parenthesized optional length `(ː)` on matrices/templates
(`V:[+front](ː)`, `V3(ː)`) — wrong to collapse here; follow-on [104](104-correction-pass-parenthesized-optional-length-marker.md) (**blocked by [94](94-grill-structured-soundchangerule-ir.md)**).

Unit + ASCA smoke tests in `tests/conlanger/tools/compile/asca/test_length_marks.py` (matrix-suffix cases moved from `test_tools_compile_asca.py`).

## Answer (before/after)

Baseline: **8089 / 9676** ok; **10** rules with `unknown_character` / error_token `ː`; **373 / 714** sections all-OK.

Re-run (`uv run validate_rules`) after scoped matrix-suffix pass:

- **8089 / 9676** ok (unchanged — matrix-suffix `]ː` rows were already handled; no false ok-flips from `(ː)` collapse)
- `ː` unknown_character **10** (unchanged; Salish `V3(ː)`, Tocharian `V:[+front](ː)` remain deferred)
- Sections all-OK **373 / 714** (unchanged)

**Rework note:** initial commit incorrectly collapsed `](ː)` and `Vn(ː)` like matrix-suffix; reverted those rules after review showed `(ː)` is optional-length notation, not `]ː`.

## Acceptance criteria

- [x] Matrix-suffix `ː` patterns documented with ASCA smoke examples
- [x] `normalize_asca_length_marks()` extended; Iroquoian meta hold-outs listed
- [x] Full inventory re-run; before/after ok + `ː` residual count in **Answer**
- [x] Fixtures updated where validation outcomes change (no `sound_change_rules.csv` rows for affected rules; inventory CSVs regenerated)

## Policy

- Compile-layer fix only; index YAML `raw` unchanged (ADR-0010).
- Class-first mechanical transform — same edit ladder as tickets 15/25.

## References

- [Correction pass: length marker ː](15-correction-pass-length-marker.md)
- [Correction pass: remaining bare length marker ː](25-correction-pass-bare-length-marker.md)
- [Correction pass: near-miss unknown_character](63-correction-pass-near-miss-unknown-character.md)
- [ASCA compile transform order](../research/asca-compile-transform-order.md)
- [Correction pass template](13-correction-pass-template.md)
