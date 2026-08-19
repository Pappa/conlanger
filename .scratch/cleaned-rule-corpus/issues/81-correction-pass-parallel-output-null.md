Type: task
Status: resolved
Blocked by:

# Correction pass: parallel output ∅ sets

Target cluster: `syntax_other` — **`∅` in parallel output sets** — **24** rules in ≤3-fail sections (**17** mono-class sections would complete if cleared). Full-corpus count TBD at claim time ([inventory summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [64 syntax_other near-miss spike](../issues/64-spike-syntax-other-near-miss-sections.md) (2026-08-19).

## Context

Index writes parallel outputs with deletion branches inline:

| Example | ASCA error |
|---------|------------|
| `{r,h} > {∅,h}` | `Expected an IPA character… received '∅'` |
| `{m,ɲ} n > {ɲ,∅} {ŋ,∅}` | same |
| `{b,k} r > {r,∅}` | same |

ASCA accepts `∅` as a segment (deletion) but not as a member of a parallel correspondence set. **24** near-miss rules; **17** sections are mono-class `syntax_other` and would go all-OK if this cluster clears.

## What to build

1. Classify shapes: single-branch deletion in set, multi-column parallel outputs, chained sets.
2. Compile rewrite — expand to ASCA-legal deletion syntax (split rules, `∅` output column, or env-qualified branches) without silent meaning change.
3. Full inventory re-run; record before/after for `syntax_other` rows whose description contains `received '∅'` in the IPA-character bucket.
4. Unit tests in `tests/conlanger/tools/compile/asca/`.

## Policy

- Compile-layer fix; corpus YAML `raw` unchanged (ADR-0010).
- Preserve parallel semantics — do not drop a deletion branch.

## Acceptance criteria

- [x] Subcluster shapes documented with ASCA smoke examples
- [x] Compile transform implemented
- [x] Full inventory re-run; before/after ok + section-complete delta in **Answer**
- [x] Fixtures updated where validation outcomes change

## Answer

Implemented 2026-08-19.

### Shapes → ASCA mapping

| Shape | Index example | ASCA branches (smoke) |
|-------|---------------|----------------------|
| Paired whole-field sets | `{r,h} > {∅,h}` | `r > ∅`, `h > h` |
| Paired column sets | `{pʰ,ŋ} > {∅,j}` | `pʰ > ∅`, `ŋ > j` |
| Multi-column zip | `{m,ɲ} n > {ɲ,∅} {ŋ,∅}` | `m n > ɲ ŋ`, `ɲ n > ∅` |
| Single + set column | `m l > {m,n} {l,∅}` | `m l > m l`, `m l > n` |
| Fixed + branching column | `p k > ɸ {∅,k}` | `p k > ɸ`, `p k > ɸ k` |
| Input set + trailing segment | `{b,k} r > {r,∅}` | `b r > r`, `k r > ∅` |
| Out of scope | `k b r > {ŋ,∅} {w,m} {n,r,t}` | uneven branch counts across columns |
| Out of scope | `b d k > {b,β} {ɾ,l,∅} {k,x,ɡ,ɣ}` | 2 / 3 / 4 branch counts |

### Code

- `expand_parallel_output_null_branches` in `src/conlanger/tools/compile/asca/parallel_output_null.py`
- `SoundChangeRule._build_parallel_null_set_alternatives` (ticket 81) after optional-output detection (ticket 66)
- `_peel_trailing_env_from_output` for stages that embed env after set output (`ŋ > {∅,n} #_ else`)
- Exported `split_outside_groupers` from `parallel_null_columns.py`

### Inventory

Before (committed inventory): **8125 / 9639 ok (84.3%)**.

After: **8195 / 9683 ok (84.7%)** (**+70** ok rows; extra rows from `alt_idx` expansion).

`null_in_parallel_output_set` near-miss cluster (**24** rules): **15 / 24** rule_ids now validate on all alternative rows; **9** residuals are uneven multi-column branch counts (`Akwára-k-b-r`, West Tariku `b d k` family, `Tunebo-m-n-h-j`).

Full-corpus `received '∅'` in set syntax: **~40 → ~15** error rows (remaining include uneven-branch residuals and rules outside the near-miss set).

Mono-class near-miss sections from spike: **9 / 19** now section-complete for this subcluster (remainder blocked on uneven-branch rules in mixed sections).


## References

- [Spike: syntax_other near-miss sections](64-spike-syntax-other-near-miss-sections.md)
- [Correction pass template](13-correction-pass-template.md)
- [ASCA compile transform order](../research/asca-compile-transform-order.md)
