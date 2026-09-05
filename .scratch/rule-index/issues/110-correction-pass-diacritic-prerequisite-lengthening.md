Type: task
Status: resolved
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

- [x] Target cluster sized at claim time
- [x] Compile transforms; `raw` unchanged
- [x] Full inventory re-run; metrics in **Answer**
- [x] Unit tests per segment class

## Answer

Implemented 2026-09-01.

### Segment shapes

| Shape | Example | Compile rewrite |
|-------|---------|-----------------|
| Voiced / sonorant + `ʰ` | `jʰ`, `bʰ`, `lʰ`, `rʰ` | `segment:[+spread,+voice]` |
| Modulated voiced aspirate | `ɡʲʰ`, `gʷʰ`, `ɢʷʰ` | `segment:[+spread,+voice]` |
| Voiceless stop + `w` + `ʰ` | `pwʰ`, `twʰ` | `stopʷʰ` |
| Input lengthening (ticket 25) | `pː` | `p:[+long]` — already in `length_marks` |

Residual `diacritic_prereq` (**9** rules): Polish `r̝` fricative — `Must be [-sonorant]` (out of scope).

### Code

- `normalize_asca_voice_prerequisite_diacritics()` in `voice_prerequisite_diacritics.py`; wired in `compile_asca_field_post_subscript` after `length_marks` / `breve_marks`.

### Inventory

Before: **8358 / 9840 ok (84.9%)**; **870** fail; **408 / 714** sections all-OK; **`diacritic_prereq` 32**.

After: **8380 / 9840 ok (85.2%)**; **848** fail; **414 / 714** sections all-OK (**+6** section-complete).

`voice_prerequisite_diacritic` near-miss cluster: **10 / 10** target rules now OK; **+22** total `diacritic_prereq` recoveries including Proto-Italic / Abazgi / Latino-Falsican voiced aspirates.

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `diacritic_prereq` / `voice_prerequisite_diacritic`
