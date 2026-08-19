Type: task
Status: needs-triage
Blocked by: 71

# Correction pass: flatten nested sets in stages I/O

Target cluster: `nested_brackets` — true nested `{…}` in **stages** (~9 inventory rows at 2026-08-12 baseline).

Spawned from [spike 67](67-spike-nested-sets.md). Findings: [nested-sets-inventory.md](../research/nested-sets-inventory.md) §4.1.

**Blocked by [71](71-grill-paren-and-parallel-set-notation.md)** where shapes mix optional-prefix parallel columns with nested braces (`(h)ə{p,b}`, `{e{V…},…}`).

**Policy hold:** [Spike 85](85-spike-nested-set-flatten-prototype.md) will recommend parse-time vs compile-time placement for all nested-set flatten work; rewrite implementation brief before agent pickup if spike concludes parse-time.

Examples:

| source | shape |
|--------|-------|
| `index_diachronica_original.html:998` | `{ʔ,{h1,h2}} → ∅` |
| `index_diachronica_original.html:5048` | `{{∅,∅}s,s{∅,∅}} → sː` |
| `index_diachronica_original.html:1398` | `{{s,z}(ˤ),ʒ}ʃ → ʃː` |

ASCA: `NestedBrackets` in I/O.

## What to build

1. Classify: union-flatten vs rule-split vs `manual_mappings`.
2. Simple input nests: `{ʔ,{h1,h2}}` → `{ʔ,h1,h2}` when attested semantics = union of alternatives.
3. Paired nested output sets (`{e{V…},eC{V…}}`) → sequential rules or flattened peers per grill 71.
4. Chain malformation (`4654`, unbalanced `2173`) → parse/chain fix or skip, not nested flatten alone.

## Acceptance criteria

- [ ] Taxonomy + handler(s) + tests
- [ ] Inventory re-baseline; metrics in **Answer**
- [ ] Complex residuals routed to `manual_mappings` or skip
