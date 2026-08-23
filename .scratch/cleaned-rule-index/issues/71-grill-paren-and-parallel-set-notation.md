Type: grilling
Status: needs-triage
Blocked by: None

# Grill: parenthetical + parallel-set notation (`(h)ə{p,b}`, `e(C){V[…]}`)

Spawned from [spike 67](67-spike-nested-sets.md). Findings: [nested-sets-inventory.md](../research/nested-sets-inventory.md) §4.5.

## Question

Index uses **optional segment prefix + brace parallel column** and **segment-template + set** shapes that ASCA reports as `nested_brackets` but are not always true nested `{}`:

- `(h)ə{p,b} → t / _l` (`index_diachronica_original.html:2398`)
- `e(C){V[- low]} → …` (`index_diachronica_original.html:3124`)
- `(j){u,ʌ}` with env (`index_diachronica_original.html:5900`)

How should these compile?

1. **Rule fan-out** (Cartesian product of optional prefix × set members)?
2. **Flatten** to a single `{…}` after expanding optionals?
3. **`manual_mappings`** / skip for ambiguous rows?

## Facts

- Ticket [66](66-implement-optional-outputs-alt-idx.md) optional outputs apply only to **unpaired whole-field output sets** — not these input-side shapes.
- Ticket [48](48-correction-pass-parenthetical-segment-notation.md) handled many I/O parens; residual parallel-column shapes remain.
- ASCA 0.10.2: no nested `{}`; optionals `(…)` not allowed in I/O segments.

## Acceptance criteria

- [ ] Owner decision on semantics per shape family
- [ ] Unblocks [70](70-correction-pass-flatten-nested-io-sets.md) for mixed rows
- [ ] Answer recorded; implementation ticket filed or defer written
