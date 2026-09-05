Type: task
Blocked by:

# Correction pass: prenasal ⁿ prefix normalisation

Target cluster: `invalid_ipa` — Unicode prenasal prefix `ⁿ` on segments — **11** failing rules (**6** mono-class sections would complete if cleared). Spawned from [114 IPA prioritisation spike](../issues/114-spike-ipa-correction-prioritization.md) (2026-09-05). Findings: [ipa-correction-prioritization.md](../research/ipa-correction-prioritization.md).

## Problem

Rules use Index prenasal prefix notation where ASCA cannot resolve the `ⁿ` grapheme:

```
P > ⁿP / #NV_
s ʃ > ⁿs ⁿʃ / _ %[-nas]
NVP > VⁿP / #_
N[-tense] N[+tense] > N[+tense] ⁿP / _ C=2 position
```

Error: `Could not get value of IPA 'ⁿ'.`

Concentrated in §7.13 (Algonquian), §10.3.5.x (Austronesian), §24.1.5/7 (Paman), §30.1.1 (Bantu).

Distinct from Khoisan click notation (§20.x — defer per [spike 64](../research/syntax-other-near-miss-sections.md)).

## What to build

1. Classify `prenasal_prefix` segment shapes ([ipa-correction-classes.csv](../research/ipa-correction-classes.csv)).
2. Compile `normalize_prenasal_prefix()` — expand `ⁿP` → prenasal segment or `N` + `P` matrix form ASCA accepts; handle output-side `VⁿP`.
3. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [ ] Target cluster sized at claim time from current inventory
- [ ] Class-first compile normalisation; no silent meaning change
- [ ] Full inventory re-run; metrics in **Answer**
- [ ] Unit tests for input-side, output-side, and env-adjacent shapes

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `invalid_ipa` / `prenasal_prefix`
