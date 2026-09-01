Type: task
Blocked by:

# Correction pass: diacritic prerequisite lengthening

Target cluster: `diacritic_prereq` — voice prerequisite on lengthening diacritics — **10** near-miss rules (**5** mono-class sections would complete if cleared). Spawned from [106 near-miss prioritisation spike](../issues/106-spike-near-miss-correction-prioritization.md) (2026-09-01). Findings: [near-miss-correction-prioritization.md](../research/near-miss-correction-prioritization.md).

## Problem

Rules use ASCII lengthening (`ː` suffix) or aspiration (`ʰ`) on segments that ASCA rejects for lacking voice prerequisite:

```
pː pwː tː ʈː qː kː > …
jʰ > …
```

Error: `Segment does not have prerequisite properties to have this diacritic. Must be [+voice]`.

Concentrated in **10.3.5.x** (Caaàc / Jawé) and **10.2.4.2** (Madurese).

## What to build

1. Classify segment shapes in `voice_prerequisite_diacritic` bucket.
2. Compile normalisation — expand `pː` → `p:[+long]` or equivalent matrix notation ASCA accepts.
3. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [ ] Target cluster sized at claim time
- [ ] Compile transforms; `raw` unchanged
- [ ] Full inventory re-run; metrics in **Answer**
- [ ] Unit tests per segment class

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `diacritic_prereq` / `voice_prerequisite_diacritic`
