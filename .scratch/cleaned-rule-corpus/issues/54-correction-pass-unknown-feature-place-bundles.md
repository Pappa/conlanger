Type: task
Blocked by: 12, 32

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

- [ ] `bundle` kind supported in CSV loader and parser
- [ ] Place bundle rows seeded with spike-cited ASCA targets
- [ ] Unit tests per place label (`C:[+dental]`, etc.)
- [ ] Full inventory re-baseline; per-token counts in **Answer**
- [ ] Fixtures updated where outcomes change

## Answer

_(pending)_

## References

- [Correction pass: unknown_feature phase 1](32-correction-pass-unknown-feature.md)
- [Spike: Index feature matrices → ASCA targets](29-spike-index-feature-matrices-to-asca-targets.md)
- [Correction pass template](13-correction-pass-template.md)
