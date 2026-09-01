Type: task
Blocked by:

# Correction pass: parallel output ∅ residuals

Target cluster: `syntax_other` — **`∅` in parallel output sets** (residual) — **10** near-miss rules (**8** mono-class sections would complete if cleared). Spawned from [106 near-miss prioritisation spike](../issues/106-spike-near-miss-correction-prioritization.md) (2026-09-01). Follow-on to resolved [81 parallel output ∅](81-correction-pass-parallel-output-null.md).

## Problem

Index parallel outputs with deletion branches still fail after ticket 81:

```
b d k > {∅,b} {∅,d} {∅,k}
k b r > {∅,k} {∅,b} {∅,r}
```

Error: `Expected an IPA character… received '∅'`.

Concentrated in sections **18.4.1** (Akwára), **21.2.3.x** (Deirate / Faia / Fayu / Kirikiri cluster). Residual shapes are mostly **multi-segment chain inputs** with `∅` in correspondence columns:

| Section | Example |
|---------|---------|
| 18.4.1 | `k b r > {∅,b,ɡ} {∅,r,ɡ}` (Akwára) |
| 21.2.3.x | `b d k > {∅,b,ɡ} {∅,d,ɡ} {∅,k,ɡ}` (Faia family) |

## What to build

1. Diff residual shapes against [81](../issues/81-correction-pass-parallel-output-null.md) policy — likely multi-column chained parallel sets.
2. Compile rewrite per ADR-0010 (split rules, `∅` output column, or env-qualified branches).
3. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [x] Residual shapes classified vs ticket 81 coverage
- [x] Compile transforms; `raw` unchanged
- [x] Full inventory re-run; metrics in **Answer**
- [x] Unit tests for each new shape

## Answer

Implemented 2026-09-01.

### Residual shapes vs ticket 81

| Shape | Index example | Ticket 81 | Ticket 109 |
|-------|---------------|-----------|------------|
| Uniform-width zip | `{m,ɲ} n > {ɲ,∅} {ŋ,∅}` | zip by index | unchanged |
| Uneven branch counts | `k b r > {ŋ,∅} {w,m} {n,r,t}` | out of scope | Cartesian product (12 branches) |
| Uneven 2/3/4 widths | `b d k > {b,β} {ɾ,l,∅} {k,x,ɡ,ɣ}` | out of scope | Cartesian product (24 branches) |
| Fixed + branching cols | `m n h j > b {n,r,∅} {h,∅} {j,∅}` | out of scope | Cartesian product (12 branches) |
| Env glued to output set | `ŋ > {∅,n} #_ else` | peel deferred | `peel_embedded_output_env` → optional-output branches |

### Code

- `expand_parallel_output_null_branches_from_tokens`: Cartesian fallback when column branch widths differ (ticket 109)
- `peel_embedded_output_env` in `field_tokens.py`; wired in `SoundChangeRule._build_alternatives`

### Inventory

Before: **8184 / 9677 ok (84.6%)**; **881** fail; **399 / 714** sections all-OK.

After: **8358 / 9840 ok (84.9%)**; **870** fail; **408 / 714** sections all-OK (**+9** section-complete).

`null_in_parallel_output_set` near-miss cluster: **10 / 10** rule_ids now validate on all alternative rows (was **0 / 10** after ticket 81 residuals). Extra inventory rows from `alt_idx` expansion (+163 rows total).

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `syntax_other` / `null_in_parallel_output_set`
