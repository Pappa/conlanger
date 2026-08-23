Type: task
Status: resolved
Blocked by: 59

# Correction pass: Index parallel-column `∅` in multi-segment I/O

Spawned from grill 2026-08-09 (Index vs ASCA multi-segment deletion). Template: [13](13-correction-pass-template.md).

## Problem

Index Diachronica writes **parallel-column** nulls inside multi-segment rules, e.g.:

```
c ɲ → ∅ n
k ʃ → ∅ ʃ / V_V
ʔ h → ∅ x
```

ASCA 0.10.2 treats any `∅`/`*` in the output as a **deletion rule**, then requires the output to contain **only** `∅`/`*` — so mixed forms fail:

`Syntax Error: The output of a deletion rule must only contain '*' or '∅'`

**~42** inventory rows today ([error CSV](../inventory/asca-rule-inventory-error.csv)).

## Confirmed ASCA mapping (grill probes)

Omit the deleted column from the output (uneven-length substitution), e.g.:

| Index | ASCA |
| --- | --- |
| `c ɲ > ∅ n` | `c ɲ > n` |
| `k ʃ > ∅ ʃ / V_V` | `k ʃ > ʃ / V_V` |
| `ʔ h > ∅ x` | `ʔ h > x` |

Probes (`asca 0.10.2`): Index forms fail; omitted-null forms parse and apply as whole-match replacements (`cɲa => na`, `akʃa => aʃa`, `ʔha => xa`). Pure single-segment deletion `x > ∅` stays unchanged.

Docs: ASCA [Insertion and Deletion](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#insertion-and-deletion-rules) — I or O must contain *only* `*`/`∅` for insert/delete rules; positional nulls are not that construct.

## What to build

**Compile-time** transform (Index-shaped SoT unchanged; `raw` keeps Index `∅`):

1. On each compiled step’s **input** and **output** (after stages → adjacent pairs): if the segment list mixes `∅`/`*` with other material, **drop** those null tokens; leave remaining segments in order.
2. If a side is only `∅`/`*` (pure deletion or pure insertion), do **not** strip — keep ASCA delete/insert form.
3. Wire into ASCA compile order (research/transform-order doc); re-run inventory; record before/after for the deletion-rule cluster (and matching insertion mixed-null residuals).

### Same pass: input-side null columns

Symmetric **input** case is **in scope for this ticket**: Index `∅ ʃ → k ʃ` fails with “input of an insertion rule must only contain `*` or `∅`”; omitting input null → `ʃ > k ʃ` works. Apply the same “drop mixed null tokens” on **input** and **output**.

### Out of scope

- `∅` **inside sets** (e.g. `{j,∅}`) — different error; not fixed by omitting a top-level null column. Confirmed out of scope (grill 2026-08-09).
- Proto reconstruction `*T` / `*D` misclassified as insertion (`*T > t`) — not Index null columns; separate cluster.
- ASCA panics on some set uneven forms (e.g. `c ɲ > {ɲ,j}`) — report residual; do not invent probe-synthesis workarounds.

## Policy

- Class-first, historically faithful: Index parallel columns → ASCA uneven substitution by dropping null columns only.
- No inventing env when absent; no changing non-null segments.

## Acceptance criteria

- [x] Compile transform drops mixed top-level `∅`/`*` from **input and output** before ASCA join
- [x] Pure deletion/insertion (`x > ∅`, `∅ > x`) unchanged
- [x] Inventory: `deletion rule must only contain` cluster reduced; mixed-input insertion residuals noted; before/after in **Answer**
- [x] Fixtures/tests cover `c ɲ → ∅ n` → `c ɲ > n` and `∅ ʃ → k ʃ` → `ʃ > k ʃ` (plus at least one env case)

## Answer

Compile-time **`drop_mixed_parallel_null_columns`** in `asca_compile/parallel_null_columns.py`, applied in `SoundChangeRule._compile_rule_text` on input/output before join (Index SoT unchanged).

**Inventory:** before **7187 / 9201 ok (78.1%)** → after **7255 / 9201 ok (78.9%)** (**+68**). `deletion rule must only contain` cluster **~42 → 0**; mixed-input `∅ ʃ > k ʃ` fixed (e.g. HTML:1092). Residual insertion errors are proto-reconstruction `*T`/`*D`/`*R` tokens (out of scope). Deletion residuals: `l > ∅?)`, `r > *L` (malformed / non-column null).

## References

- ASCA 0.10.2 docs § Insertion and Deletion
- [asca-rule-validity.md](../research/asca-rule-validity.md) §2 Output (delete = `∅` alone)
- Example sources: `index_diachronica_original.html` (e.g. Proto-Utupua to Nebao `c ɲ → ∅ n`)
