Type: task
Status: resolved
Blocked by: 21

# Correction pass: when stressed / when unstressed env conditions

Target cluster: `expected_underscore` / `stuff_after_word_bound` from Index stress prose in env fields (~48–74 rules).

## Policy

Parse-time normalization (not compile, not ``raw``):

1. Remove comma before ``when stressed`` / ``when unstressed`` (``_N, when stressed`` → ``_N when stressed``).
2. Env-only condition → prefix focus ``_`` (``when unstressed`` → ``_ when unstressed``).
3. Prose-only env (no ``_``) → drop prose prefix (``in open syllables, when stressed`` → ``_ when stressed``).
4. After word boundary ``#`` → strip trailing stress phrase (``_# when unstressed`` → ``_#``; ASCA cannot parse text after ``#``).

ASCA accepts ``_C(C) when stressed`` and ``l_ when unstressed`` as-is once commas are removed.

## Acceptance criteria

- [x] Parse-time transform on env/exception
- [x] Unit + parse integration tests
- [x] Inventory re-baseline recorded

## Answer (before/after)

Baseline (after issue 21): **6204 / 9316** ok (66.6%).

Full inventory re-run:

- **6237 / 9316** ok (**+33** rules, **67.0%**)
- Sections all OK: updated in summary
