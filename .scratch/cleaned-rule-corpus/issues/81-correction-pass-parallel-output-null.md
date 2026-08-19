Type: task
Status: ready-for-agent
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

- [ ] Subcluster shapes documented with ASCA smoke examples
- [ ] Compile transform implemented
- [ ] Full inventory re-run; before/after ok + section-complete delta in **Answer**
- [ ] Fixtures updated where validation outcomes change

## References

- [Spike: syntax_other near-miss sections](64-spike-syntax-other-near-miss-sections.md)
- [Correction pass template](13-correction-pass-template.md)
- [ASCA compile transform order](../research/asca-compile-transform-order.md)
