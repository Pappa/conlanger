Type: task
Status: resolved
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

- [x] `normalize_asca_breve_marks()` implemented; index `raw` unchanged (ADR-0010)
- [x] ASCA smoke tests for Tai, Scots, Tanacross representative rules
- [x] Slavic §46.14 rule held out
- [x] Full inventory re-run; before/after `̆` residual + sections-all-OK in **Answer**
- [x] Fixtures updated where validation outcomes change

## Answer

**Shipped 2026-08-19.**

### Inventory

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK / total | 8168 / 9683 (84.4%) | **8180 / 9683 (84.5%)** | **+12** |
| Sections all OK | 308 / 712 (43.3%) | **309 / 712 (43.4%)** | **+1** (Scots 17.7.2.1.10) |
| `unknown_character` | 207 | **194** | **−13** |
| `̆` error-token residual | 13 | **0** | **−13** |

**Recovered:** 12 breve rules via `normalize_asca_breve_marks()` (Tai ×10, Scots ×1, Tanacross ×1). Tanacross nested set `{æ̆,ă}` validates after breve transform (no separate nested-set pass needed for this rule).

**Held out:** `Pre-Slavic-Vowel-Changes-i` (§46.14) via `parser_config.yml` `skip_rules` → `status: skipped` at parse.

**Code:** `src/conlanger/tools/compile/asca/breve_marks.py`; pipeline step after ejective marks; `data/parser_config.yml` `skip_rules`; tests in `test_breve_marks.py`.

## References

- [Research: breve vowel notation](../research/breve-vowel-notation.md)
- [ASCA ejective notation research](../research/asca-ejective-notation.md) — compile-transform precedent
- [Correction pass template](13-correction-pass-template.md)
- [length_marks.py](../../../src/conlanger/tools/compile/asca/length_marks.py)
