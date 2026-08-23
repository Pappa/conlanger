Type: task
Status: resolved
Blocked by: 12, 32

# Feature bundle expansion + vowel-height compounds

Implement multi-feature **`mapping_kind=bundle`** expansion in `feature_mappings.csv` / `IndexDiachronicaParser`, with inaugural **vowel-height** seed rows for Index hyphen compounds `close-mid` and `open-mid`.

Grilled 2026-08-08; unblocks [Correction pass: unknown_feature place bundles](54-correction-pass-unknown-feature-place-bundles.md).

## Problem

Two Kenyah rules (§10.2.6.2.1) fail because ASCA does not accept Index compounds `[+close-mid]` / `[+open-mid]` — it tokenises `close` / `open` as unknown features ([inventory error CSV](../inventory/asca-rule-inventory-error.csv), `index_diachronica_original.html:3054–3055`).

Phase 1 feature renames ([ticket 32](32-correction-pass-unknown-feature.md)) only support 1:1 swaps. Spike [29](29-spike-index-feature-matrices-to-asca-targets.md) scoped **`bundle`** for place labels (#54) but the same plumbing is needed here.

## What to build

### 1. Bundle plumbing

1. Enable **`mapping_kind=bundle`** in `load_feature_mappings()` (currently rejected).
2. In `normalize_feature_matrices_in_field()`, replace one Index token inside `[...]` with a comma-separated multi-feature ASCA matrix body from `asca_target`.
3. **Polarity semantics (Q12 deferred):** document behaviour in code/tests when landed; vowel-height seed rows use **literal** signed features in `asca_target` (see below).
4. Match compound keys as whole tokens: `close-mid`, `open-mid` — never `close` / `open` alone (spike 29).

### 2. Vowel-height seed rows

Per [ASCA 0.10.2 vowel-space table](https://github.com/Girv98/asca-rust/blob/36c3c623fb9f501a358ae087764e77b92d0037bf/doc/doc.md#segment-features) (mid height = `-hi -lo`; close-mid vs open-mid split on **tense**):

| `index_feature` | `mapping_kind` | `asca_target` | `confidence` | Notes |
|-----------------|----------------|---------------|--------------|-------|
| `close-mid` | `bundle` | `-hi,-lo,+tense` | high | Upper mid (e, o row); ASCA `+tns` |
| `open-mid` | `bundle` | `-hi,-lo,-tense` | high | Lower mid (ɛ, ɔ row); ASCA `−tns` |

Parse-time only; `raw` unchanged.

### 3. Verification

- ASCA smoke on §10.2.6.2.1 env fragments after expansion.
- Unit tests: compound-key match, no partial `open`/`close` match, both polarity bundles.
- Full inventory re-run; record before/after in **Answer**.

**Expected impact:** **+2 ok** (Kenyah rules); primary deliverable is reusable bundle infrastructure for #54.

### Out of scope

- Place bundles (`dental`, `palatal`, …) — [ticket 54](54-correction-pass-unknown-feature-place-bundles.md)
- Final `mapping_kind` naming for literal vs propagated polarity (grill Q12 deferred)
- Syllable-prosody `open` / `%[+open]` — distinct cluster

## Policy

- Parse-time mapping inside `[...]` only; `raw` preserved (ADR-0010).
- Cite ASCA vowel-space source in CSV `notes` column.

## Acceptance criteria

- [x] `bundle` kind supported in CSV loader and `apply_feature_mappings()`
- [x] `close-mid` / `open-mid` rows seeded as above
- [x] Kenyah §10.2.6.2.1 rules compile (`validate_asca`)
- [x] Tests cover bundle expansion and compound-key matching
- [x] Full inventory re-baseline; per-token counts in **Answer**

## Answer

Baseline (pre-pass): **7132 / 9201** ok (77.5%); `unknown_feature` tokens `close` (1), `open` (1) at Kenyah §10.2.6.2.1.

After `mapping_kind=bundle` plumbing + vowel-height seed rows:

- **7134 / 9201** ok (**77.5%**, **+2**)
- Kenyah rules `index_diachronica_original.html:3054–3055` now **ok**
- `close` / `open` residual from `[+close-mid]` / `[+open-mid]`: **1 → 0** each

**Code:** `bundle` added to `_SUPPORTED_FEATURE_MAPPING_KINDS`; `normalize_feature_matrices_in_field()` inserts literal `asca_target` feature lists (index polarity ignored — Q12 deferred). Seed rows in `data/asca/feature_mappings.csv`. Tests in `test_IndexDiachronicaParser.py`.

Unblocks [ticket 54](54-correction-pass-unknown-feature-place-bundles.md) place-bundle rows.

## References

- [Correction pass: unknown_feature phase 1](32-correction-pass-unknown-feature.md)
- [Correction pass: unknown_feature place bundles](54-correction-pass-unknown-feature-place-bundles.md) — blocked by this ticket
- [Spike: Index feature matrices → ASCA targets](29-spike-index-feature-matrices-to-asca-targets.md)
- [Research: index-feature-matrices-to-asca-targets.md](../research/index-feature-matrices-to-asca-targets.md)
