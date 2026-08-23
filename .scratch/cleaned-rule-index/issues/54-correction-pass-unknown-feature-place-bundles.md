Type: task
Status: resolved
Blocked by: 12, 32, 57

# Correction pass: unknown_feature place bundles (phase 2)

Target cluster: `unknown_feature` — Index **place bundle** matrix features — **51** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

Ticket [32](32-correction-pass-unknown-feature.md) shipped Phase 1 renames (`voiced`→`voice`, etc.). Phase 2 **bundle** expansion was deferred. Residual place-label tokens:

| error_token | count |
|-------------|------:|
| `dental` | 19 |
| `palatal` | 13 |
| `alveolar` | 5 |
| `velar` | 5 |
| `uvular` | 4 |
| `guttural` | 5 |

Per spike [29](29-spike-index-feature-matrices-to-asca-targets.md), these need `mapping_kind=bundle` rows expanding to multi-feature ASCA matrices — not 1:1 renames.

## What to build

1. Enable **`mapping_kind=bundle`** in `feature_mappings.csv` loader (rejected in Phase 1).
2. Seed bundle rows for place labels per [research/index-feature-matrices-to-asca-targets.md](../research/index-feature-matrices-to-asca-targets.md).
3. Wire bundle expansion in `IndexDiachronicaParser.apply_feature_mappings()` inside `[...]` only.
4. Full inventory re-run; record before/after for `unknown_feature` place tokens.

**Expected impact:** ~**35** ok uplift at ~70% recoverability.

### Out of scope

- Tone, lenis/fortis, `samePOA`, syllable `open`/`closed` — defer per spike 29
- `open` (16) — prosodic, not place; separate cluster if pursued

## Policy

- Parse-time only; `raw` preserved.
- Do not seed from Levenshtein suggestions without spike review.

## Acceptance criteria

- [x] `bundle` kind supported in CSV loader and parser
- [x] Place bundle rows seeded with spike-cited ASCA targets
- [x] Unit tests per place label (`C:[+dental]`, etc.)
- [x] Full inventory re-baseline; per-token counts in **Answer**
- [x] Fixtures updated where outcomes change

## Answer

Baseline (pre-pass): **7263 / 9201** ok (78.9%); `unknown_feature` place tokens: `dental` (22), `palatal` (13), `alveolar` (5), `velar` (5), `uvular` (4), `guttural` (5, deferred).

After place-bundle seed rows in `data/asca/feature_mappings.csv`:

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK | 7263 (78.9%) | 7299 (79.3%) | **+36** |
| `unknown_feature` class | 167 | 120 | **−47** |

**Per-token residual (`unknown_feature`):**

| token | before | after |
|-------|-------:|------:|
| `dental` | 22 | 0 |
| `palatal` | 13 | 0 |
| `alveolar` | 5 | 0 |
| `velar` | 5 | 0 |
| `uvular` | 4 | 0 |
| `guttural` | 5 | 5 (deferred per spike 29) |

**Code:** five `mapping_kind=bundle` rows (`dental`, `alveolar`, `palatal`, `velar`, `uvular`) with spike-cited ASCA targets; bundle expansion reuses #57 plumbing (literal signed features in `asca_target`). Tests in `test_IndexDiachronicaParser.py`.

## References

- [Correction pass: unknown_feature phase 1](32-correction-pass-unknown-feature.md)
- [Spike: Index feature matrices → ASCA targets](29-spike-index-feature-matrices-to-asca-targets.md)
- [Correction pass template](13-correction-pass-template.md)
