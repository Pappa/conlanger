Type: task
Status: resolved
Blocked by: [121](121-correction-pass-io-matrix-bracket-to-colon.md)

# Correction pass: merge adjacent ASCA feature matrices

Target cluster: `incomplete_matrix` — **1** rule today ([Sebirwa-S](../inventory/error_clusters/incomplete_matrix_errors.csv)); pattern may recur wherever group expansion leaves `][` between matrices on the same host.

Spawned from wayfinder session on [Cleaned rule index SoT](../map.md) (2026-09-08). Related: ticket [62 tone merge](62-correction-pass-tone-features.md) (tone-only); ticket [121 host+bracket→colon](121-correction-pass-io-matrix-bracket-to-colon.md) (bracket form, not `][` split). **Out of scope:** [Cypriot-Arabic-∅](../inventory/error_clusters/incomplete_matrix_errors.csv) — env+matrix insertion interaction; see [125](125-grill-asca-grouping-insertion.md) / [126](126-correction-pass-asca-grouping-insertion.md).

## Problem

ASCA 0.10.2 rejects **adjacent** feature matrices at apply time (`Runtime Error: An incomplete matrix cannot be inserted`) even when syntax validation passes. Merged colon form on one host is legal:

| Form | `asca run` |
| --- | --- |
| `P > C:[+labial][+spread]` | **fail** |
| `P > C:[+labial,+spread]` | **ok** |

**Inventory example:** `Sebirwa-S` (`S → Sʰ → Aʰ`, first chain step). Index `S > Sʰ` compiles to `P > C:[+labial][+spread]`:

1. Superscript pass: `Sʰ` → `S[+spread]`
2. Group mappings: `S` → `P`, then `P` → `C:[+labial]`, leaving trailing `[+spread]` as a **separate** matrix token

Same failure mode as [62](62-correction-pass-tone-features.md) probes (`V:[+long][tone: 51]`), but for **general** binary/bundle features—not only `[tone: N]`.

## What to build

1. **Compile pass** on compiled input/output strings (after [121](121-correction-pass-io-matrix-bracket-to-colon.md) `normalize_asca_host_bracket_matrices`; env/exception out of scope unless probes require them).
2. Rewrite adjacent matrices `…[featuresA][featuresB]…` → single matrix with comma-merged interiors (reuse or generalize logic in `tone_matrices.py`).
3. **Do not** merge across segment hosts (e.g. leave `V:[+long] C:[+spread]` unchanged).
4. Apply probes from ticket 62 plus Sebirwa chain step and any near-miss rows in [near-miss-all-classes.csv](../research/near-miss-all-classes.csv) tagged `incomplete_matrix` with `][` shape.
5. Re-run full inventory; record ok/fail and `incomplete_matrix` cluster delta in **Answer**.

## Policy

- Index/applier-neutral YAML unchanged; fix is **compiled-string** shape only.
- Prefer one shared helper (extend `normalize_asca_tone_matrices` or sibling module) over a one-off regex in group mappings.

## Acceptance criteria

- [x] Pass merges `C:[+labial][+spread]` → `C:[+labial,+spread]` on I/O compile fields
- [x] Tone merge behaviour from [62](62-correction-pass-tone-features.md) preserved (regression tests)
- [x] `Sebirwa-S` validates (`ok=1`) or documented hold-out with reason
- [x] Full inventory re-run; before/after metrics in **Answer**

## Answer

**Shipped 2026-09-09.** Shared `merge_adjacent_feature_matrices` in `tone_matrices.py`; `normalize_asca_adjacent_feature_matrices` runs on compiled I/O after `normalize_asca_host_bracket_matrices`. Tone pass reuses the same merge helper.

- **Inventory:** OK **8865 → 8866 (+1)**; fail **694 → 693 (−1)**; sections all-OK **439 → 440 / 714**. `incomplete_matrix` **2 → 1 (−1)** — `Sebirwa-S` recovered (`P > C:[+labial, +spread]`); residual `Cypriot-Arabic-∅` out of scope ([125](125-grill-asca-grouping-insertion.md)).
- **Apply probes:** `C:[+labial][+spread]` → merged colon form validates; tone merge regression tests unchanged.

## References

- [incomplete_matrix_errors.csv](../inventory/error_clusters/incomplete_matrix_errors.csv)
- `src/conlanger/tools/compile/asca/tone_matrices.py`
- `src/conlanger/tools/compile/asca/pipeline.py`
- ASCA 0.10.2 grouping / matrix docs ([Groupings](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#groupings))
