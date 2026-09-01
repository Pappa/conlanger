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

- [ ] Residual shapes classified vs ticket 81 coverage
- [ ] Compile transforms; `raw` unchanged
- [ ] Full inventory re-run; metrics in **Answer**
- [ ] Unit tests for each new shape

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `syntax_other` / `null_in_parallel_output_set`
