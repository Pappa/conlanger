Type: task
Blocked by:

# Correction pass: dot-affricate and cluster notation

Target cluster: `expected_range_dots` — European dot-separated affricates and consonant clusters — **35** failing rules (**3** mono-class sections would complete if cleared; **+1** with `dot_inside_set` fold-in). Spawned from [114 IPA prioritisation spike](../issues/114-spike-ipa-correction-prioritization.md) (2026-09-05). Findings: [ipa-correction-prioritization.md](../research/ipa-correction-prioritization.md).

## Problem

Rules use Index dot notation for affricates or cluster splits where ASCA expects `..` range syntax or bare segments:

```
ttʃ ddʒʱ > t.ʃ d.ʒʱ
s:[+long] ʂ:[+long] > t.s t.ʂ
p çp b > p. ç.w p
t st tr d > t. s.d tr.
```

Error: `Expected '..'` (ASA range-dot parser) on `.` inside segments.

Concentrated in §17.10 (Indo-Iranian affricates) and §36.3.2.x (Tibeto-Burman cluster notation). Yup'ik §24.x geminate `V.V` shapes are **not** in this cluster on current inventory.

## What to build

1. Classify `european_dot_affricate` and `dot_inside_set` shapes ([ipa-correction-classes.csv](../research/ipa-correction-classes.csv)).
2. Compile pass: expand `C1.C2` dot clusters to ASCA-parseable segment sequences or matrices (policy: affricate `t.ʃ` → `tʃ` or `t ʃ` per ASCA segment model).
3. Defer Yup'ik `..` range shapes (0 active rows) and mixed-failure §36.3 sections until mono-class leverage warrants.
4. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [ ] Target cluster sized at claim time from current inventory
- [ ] Class-first compile transforms; `raw` unchanged
- [ ] Full inventory re-run; metrics in **Answer**
- [ ] Unit tests for Indo-Iranian affricate and Tibeto-Burman cluster families

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan buckets: `expected_range_dots` / `european_dot_affricate`, `dot_inside_set`
