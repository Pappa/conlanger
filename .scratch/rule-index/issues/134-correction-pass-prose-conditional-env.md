Type: task
Blocked by: [131](131-correction-pass-env-exception-feature-matrices.md)
Status: resolved

# Correction pass: prose conditional env (`expected_underscore`)

Target cluster: `expected_underscore` — Index **prose env tails** without `_` — **~28** rules at current inventory after deferring co-occurrence conditionals to [137](137-correction-pass-manual-mapping-co-occurrence-env.md) (**10** stress-word prose, **8** `else` residuals, plus scattered `//` / position phrases; **~13** other conditional prose TBD at claim). **75** total `expected_underscore` failures.

Spawned from `/grill-with-docs` on [map.md](../map.md) (2026-09-19). Related: [53 prose env else](53-correction-pass-prose-env-else.md), [55 medial](55-correction-pass-prose-env-medial.md), [107 prose positions](107-correction-pass-prose-env-positions.md), [131 env matrices](131-correction-pass-env-exception-feature-matrices.md), [122 position grill](122-grill-proximity-conditions-yaml.md).

## Problem

Rules keep natural-language **conditions** in `env` after prior passes:

```
dʒ > d / if s or z occur somewhere else in the word
dʒ > ʒ // if s or z occur somewhere else in the word
```

ASCA expects structural env with `_`; bare prose after `/` → `expected_underscore` (empty `error_token` in inventory).

**Co-occurrence / “elsewhere in word” conditionals (deferred):** e.g. Moroccan Arabic `if s or z occur somewhere else in the word` — no ASCA env; **interim** `manual_mappings.yml` + `sporadic ;` per [137](137-correction-pass-manual-mapping-co-occurrence-env.md) until [122](122-grill-proximity-conditions-yaml.md) defines structured conditioning.

**`else` residuals (8):** complementary-env pairs not yet rewritten by ticket 53 (new shapes or parse ordering).

**Stress prose (10):** env tails still containing words like `stressed` / `unstressed` without matrix form after ticket 22/131.

## What to build

1. **Inventory scan** — bucket `expected_underscore_errors.csv` by prose pattern (`if …`, `else`, stress words, `//` leftovers); size mono-class section payoff.

2. **Parse-time transforms** (preferred for editorial prose per edit ladder) where meaning is mechanical:
   - **`else` pairs:** extend [53](53-correction-pass-prose-env-else.md) detector for remaining shapes.
   - **Stress prose:** extend [22](22-correction-pass-stress-conditions.md) or map to `[-stress]`/`[+stress]` matrices per [119](119-grill-distinctive-features-env-exception.md).

3. **Out of scope:** imprecise co-occurrence / non-local conditionals → [137](137-correction-pass-manual-mapping-co-occurrence-env.md). Imprecise **position** neighbour claims → grill [122](122-grill-proximity-conditions-yaml.md) (Phase 0+); until then extend `manual_mappings.yml` only via explicit tickets like 137.

4. Hold-outs: `status: skipped` when neither mechanical parse nor manual mapping is agreed.

5. Full inventory re-run; `expected_underscore` cluster delta and sections-all-OK in **Answer**.

## Acceptance criteria

- [x] Target buckets named and sized from current inventory at claim time
- [x] Class-first transforms; `raw` unchanged; prose captured in `comment` when stripped
- [x] Full inventory re-run; metrics in **Answer**
- [x] Unit tests for Indo-European conditional env family (representative `dʒ` rules)

## Answer

**Target buckets (claim-time inventory, 70 `expected_underscore` rows):**

| Bucket | ~size | Handling |
|--------|------:|----------|
| Co-occurrence `if … occur` / stem | 5 | Deferred [137](137-correction-pass-manual-mapping-co-occurrence-env.md) |
| `else` residuals | 5 | Structural prev-env gate + prose env normalize before section else pass |
| Stress / matrix prose tails | 10 | Extended stress + prose conditional (penult, `[-stress], but…`, Rhaeto `[+stress], usually when`) |
| `//` / position / compile matrix residuals | ~50 | Out of scope here (108, 131, 122) |

**Baseline (before):** **8940 / 9839** ok (90.9%); **70** `expected_underscore`; sections all OK **484 / 714**.

**After (2026-09-19):** **8950 / 9839** ok (**+10**, **91.0%**); **51** `expected_underscore` (−19); sections all OK **486 / 714** (**+2**).

**Implementation:** `apply_prose_conditional_env_conditions` in `prose_conditional_env.py` (after stress, before medial); catch-all else resolution requires `_` in immediate previous `env`; stress strip for `, when neither vowel is stressed`.

**Moroccan `dʒ` family:** else no longer inherits prose co-occurrence as `exception` (awaits [137](137-correction-pass-manual-mapping-co-occurrence-env.md)); unit tests cover complementary deferral + Old Mandarin V5 cascade.

## References

- [expected_underscore_errors.csv](../inventory/error_clusters/expected_underscore_errors.csv)
- [Correction pass template](13-correction-pass-template.md)
