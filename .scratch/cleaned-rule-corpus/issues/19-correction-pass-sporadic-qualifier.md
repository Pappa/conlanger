Type: task
Status: resolved
Blocked by: 18

# Correction pass: uncertainty glosses — sporadic / sometimes

Target cluster: descriptive prose after rule syntax (`sporadic`, `sometimes`, …)

## Analysis

**258** chained rules; **127** carry env/exception (not split). Of rules with uncertainty language in fields, **~185** mention `sporadic` or `sometimes` (often as trailing gloss on output/env).

Policy (owner): keep the phonological rule, strip the English gloss, set `sporadic: true` so downstream pipelines may skip or sample application. Matches legacy `index_diachronica.yml` `sporadic: true` field.

## What was built

- `apply_sporadic_qualifier()` in `src/conlanger/tools/parsers.py` — parse-time transform (not stored in ``raw``):
  - Detect `\bsporadic(ally)?\b` or `\bsometimes\b` in any field.
  - Strip trailing parenthetical / quoted / bare glosses; strip env prefix `sporadic, usually …`.
  - Env/exception that is only `sometimes` → omitted (universal application, flagged sporadic).
  - Set `sporadic: true` on the corpus rule; propagated to chain-expanded steps.
- ``raw`` unchanged.

## Answer (before/after)

Full inventory: **5674 / 9334 ok (60.8%)**, up from 5592 / 9336 (+82 ok). **187** rules carry `sporadic: true`.

## Notes

- Long explanatory prose (e.g. `though sometimes > {s,ɟ}`) still in fields — separate cluster / skip decision later.
- `status: skipped` remains for unrepresentable rules; `sporadic` is not a skip.

## Acceptance criteria

- [x] Parse-time strip + `sporadic: true`; `raw` preserved
- [x] Unit + integration tests
- [x] Inventory re-baseline recorded
