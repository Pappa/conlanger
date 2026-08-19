Type: task
Status: ready-for-agent
Blocked by:

# Correction pass: breve vowel notation (`̆`)

Target cluster: `unknown_character` — error_token **`̆`** — **13** rules across **8** sections at current inventory baseline.

Spawned from [Spike: breve vowel notation](80-spike-breve-vowel-notation.md) (2026-08-19). Findings: [breve-vowel-notation.md](../research/breve-vowel-notation.md).

## Context

ASCA 0.10.2 rejects combining breve U+0306 and precomposed breve vowels (`ă`, `ŏ`, `ŭ`) in sound-change rules. Accepted encoding for extra-short vowels is **`segment:[-long]`**; bare segment stripping also validates for Tai glide outputs.

| Subcluster | rows | Transform |
|---|---:|---|
| Tai `ı̆`/`j̆`, `ɨ̆` | 10 | Strip U+0306; `j̆`→`j`, `ɨ̆`→`ɨ` (or `ɨ:[-long]`) |
| Scots `ə̆` | 1 | `ə̆` → `ə:[-long]` |
| Tanacross breve outputs | 1 | `æ̆`→`æ:[-long]`, `ă`→`a:[-long]`, `ŏ`→`o:[-long]` |
| Slavic chain | 1 | **`status: skipped`** — hold-out, not breve-only |

**Impact:** +1 section all-OK (17.7.2.1.10 Scots); 12 rules recoverable via compile transform. Low near-miss leverage — run in parallel with #81–#83.

## What to build

1. Add `normalize_asca_breve_marks()` in `src/conlanger/tools/compile/asca/` (new module or extend pipeline); register in `ASCA_COMPILE_STEP_NAMES` **after** IPA letter normalisation, **before** `validate_asca`.
2. Decompose NFC precomposed breve vowels (`ă`, `ŏ`, `ŭ`) before stripping/appending `[-long]`.
3. Policy: glide outputs (`j̆`) → bare `j`; vowel breve → strip or `:[-long]` per research (prefer strip for Tai, `[-long]` for Scots/Tanacross).
4. Hold out `Pre-Slavic-Vowel-Changes-i` (§46.14) as `status: skipped`.
5. Unit tests in `tests/conlanger/tools/compile/asca/`; full inventory re-run.

## Out of scope

- Tanacross nested output set `{æ̆,ă}` — may need separate nested-set pass if still failing after breve transform
- Bundling with [#79](79-correction-pass-matrix-suffix-length-marker.md) matrix-suffix `ː`
- Brassica compile path

## Acceptance criteria

- [ ] `normalize_asca_breve_marks()` implemented; corpus `raw` unchanged (ADR-0010)
- [ ] ASCA smoke tests for Tai, Scots, Tanacross representative rules
- [ ] Slavic §46.14 rule held out
- [ ] Full inventory re-run; before/after `̆` residual + sections-all-OK in **Answer**
- [ ] Fixtures updated where validation outcomes change

## References

- [Research: breve vowel notation](../research/breve-vowel-notation.md)
- [ASCA ejective notation research](../research/asca-ejective-notation.md) — compile-transform precedent
- [Correction pass template](13-correction-pass-template.md)
- [length_marks.py](../../../src/conlanger/tools/compile/asca/length_marks.py)
