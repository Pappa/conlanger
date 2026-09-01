Type: task
Blocked by:

# Correction pass: prose env positions

Target cluster: `expected_underscore` — prose environment position phrases — **41** near-miss rules (**13** mono-class sections would complete if cleared). Spawned from [106 near-miss prioritisation spike](../issues/106-spike-near-miss-correction-prioritization.md) (2026-09-01). Findings: [near-miss-correction-prioritization.md](../research/near-miss-correction-prioritization.md).

## Problem

Rules use English position words in the `env` field where ASCA expects `_` focus:

```
a V > e / final syllables
C[+voice] > C[-voice] / next to {P,s,l̥}
t > l / #_, in nouns
```

Error: `Expected '_', but received ''`.

Distinct from [55 medial](55-correction-pass-prose-env-medial.md) (word-internal), [22 stress](22-correction-pass-stress-conditions.md), and [53 else](53-correction-pass-prose-env-else.md).

## What to build

1. Classify prose env shapes in `missing_underscore_other` + `prose_position_env` buckets ([near-miss-all-classes.csv](../research/near-miss-all-classes.csv)).
2. Parse-time normalisation per shape (e.g. `final syllables` → `exception: :{<.._>#}:`, `next to {X}` → neighbour env set) — `raw` unchanged.
3. Defer env+existing-exception merges (Mongolic pattern from ticket 55).
4. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [ ] Target cluster sized at claim time from current inventory
- [ ] Class-first parse transforms; no silent meaning change
- [ ] Full inventory re-run; metrics in **Answer**
- [ ] Unit tests for each supported prose shape

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `expected_underscore` / `missing_underscore_other`
