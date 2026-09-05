Type: task
Blocked by:

# Correction pass: editorial slash and prose residue in compile fields

Target cluster: `expected_ipa` — editorial `/gloss/` slashes and unclosed-prose residue in compile fields — **30** failing rules (**8** mono-class sections would complete if cleared). Spawned from [114 IPA prioritisation spike](../issues/114-spike-ipa-correction-prioritization.md) (2026-09-05). Findings: [ipa-correction-prioritization.md](../research/ipa-correction-prioritization.md).

## Problem

Rules carry Index editorial slashes or prose tails inside I/O or env fields where ASCA expects IPA:

```
Original z (/ts/?) > dj
ɡ > j / V_ (if /j/ resulted, it dropped after /i/
{a/e} {e/a} > e a
V > ∅ / V:[+stress]$_(C)(C)V(C)# (
```

Error: `Expected an IPA character, Primative or Matrix, but received '/'` (or `''` from unclosed `(`).

Distinct from [108 double-slash env](../issues/108-correction-pass-double-slash-env.md) (`expected_underscore` bare `//`) and [21 trailing glosses](../issues/21-correction-pass-trailing-glosses.md) (parse-time strip at ingest).

## What to build

1. Classify shapes in `editorial_slash_gloss` bucket ([ipa-correction-classes.csv](../research/ipa-correction-classes.csv)).
2. Compile normalisation:
   - Strip editorial `/phoneme/` glosses to `comment` (preserve `raw`).
   - Peel unclosed `(` prose tails from env/I/O into `comment`.
   - Expand structural `{a/e}` vowel alternation → `{a,e}` (Tupi §18.3.x).
3. Defer `ipa_mappings` hold-outs (`*`, `@`) and malformed chains (§17.7.3.1.1).
4. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [ ] Target cluster sized at claim time from current inventory
- [ ] Class-first compile transforms; no silent meaning change
- [ ] Full inventory re-run; metrics in **Answer**
- [ ] Unit tests per supported shape family

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `expected_ipa` / `editorial_slash_gloss`
