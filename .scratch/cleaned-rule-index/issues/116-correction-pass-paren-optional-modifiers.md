Type: task
Blocked by:

# Correction pass: parenthetical optional segment modifiers

Target cluster: `expected_ipa` — parenthetical optional modifiers on segments — **21** failing rules (**8** mono-class sections would complete if cleared). Spawned from [114 IPA prioritisation spike](../issues/114-spike-ipa-correction-prioritization.md) (2026-09-05). Findings: [ipa-correction-prioritization.md](../research/ipa-correction-prioritization.md).

## Problem

Rules use Index parenthetical optional modifiers inside segments where ASCA expects bare IPA or matrices:

```
ɸ(ʼ,ʰ) > p
k > tʃ / _V:[+front]k(ʷ)
{tʷ:[+cg],tʷ,dʷ} > {tɕ(ʼ),tɕʷ(ʼ),tʃ(ʼ),tʃʷ(ʼ)}
ʔ > ∅ / _nk(ʷ)
```

Error: `Expected an IPA character, Primative or Matrix, but received '('` or `ʷ`.

Extends [48 parenthetical notation](../issues/48-correction-pass-parenthetical-segment-notation.md) and [111 cartesian I/O optionals](../issues/111-correction-pass-cartesian-io-optionals.md) Family B (modifier + segment).

## What to build

1. Classify `paren_optional_modifier` shapes ([ipa-correction-classes.csv](../research/ipa-correction-classes.csv)).
2. Compile pass: unwrap `(ʷ)`, `(ʲ)`, `(ʼ,ʰ)`, `(ˀ)` modifier optionals → cartesian segment variants or feature matrices.
3. Coordinate with 111 Family B (`k(ʰ){r,j}`) — reuse or extend existing compile step.
4. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [ ] Target cluster sized at claim time from current inventory
- [ ] Class-first compile transforms; `raw` unchanged
- [ ] Full inventory re-run; metrics in **Answer**
- [ ] Unit tests per modifier family (labialization, ejective/aspiration, glottal)

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `expected_ipa` / `paren_optional_modifier`
