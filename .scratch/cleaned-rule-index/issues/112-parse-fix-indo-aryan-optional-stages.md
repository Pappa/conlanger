Type: task
Status: needs-triage
Blocked by: None

# Parse fix: Indo-Aryan optional stages dropped from chain

Spawned from [grill 71](71-grill-paren-and-parallel-set-notation.md) Q7. Compile cartesian work is [111](111-correction-pass-cartesian-io-optionals.md); this ticket is **parse-only**.

## Problem

Rule `Central-Middle-Indo-Aryan-ai,ja-au,wa` (`index_diachronica_original.html` — Indo-Aryan section):

```text
a{i,j}(a) a{u,w}(a) → e o
```

**`raw`** preserves both optionals. **YAML `stages`** drop the second `(a)` on the second spine segment — a parse bug, not a glossary `comment` peel.

After [111](111-correction-pass-cartesian-io-optionals.md), the first segment should compile toward `a{i,j,ia,ja}` (owner preference) or equivalent flat cartesian; the second segment needs correct stages before compile.

## What to build

1. Reproduce from HTML → YAML ingest; assert `stages` retains both `(a)` optionals on the two-segment chain.
2. Fix parser stage splitting / optional capture so chain spines do not lose parenthetical tails.
3. Regression test keyed by rule id `Central-Middle-Indo-Aryan-ai,ja-au,wa` (or current HTML id).
4. **`raw` unchanged**; fix applies to parsed `stages` only.

## Acceptance criteria

- [ ] Parsed `stages` match Index `raw` for both `(a)` optionals on this rule
- [ ] Unit test in `tests/conlanger/tools/ingest/`
- [ ] No change to unrelated chain-split behaviour ([18](18-correction-pass-chain-split.md))

## References

- [Grill 71](71-grill-paren-and-parallel-set-notation.md) Q7
- [Correction pass: cartesian I/O optionals](111-correction-pass-cartesian-io-optionals.md)

## Comments

> 2026-09-02: Filed from closed grill 71. Owner confirmed separate parse ticket (not bundled with 111).
