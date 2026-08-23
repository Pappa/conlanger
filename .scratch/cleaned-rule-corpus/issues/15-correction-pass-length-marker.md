Type: task
Status: resolved
Blocked by: 14

# Correction pass: unknown_character — length marker ː

Target cluster: `unknown_character` — error_token `ː` (1251 rules at baseline)

## What was built

- `normalize_asca_length_marks()` in `src/conlanger/tools/rules.py` — ASCA compile transform (not ingest):
  1. `segment(ː)` → `segment:[+long]`
  2. `Groupingː` → `Grouping:[+long]`
  3. `segmentː` → `segment:[+long]`
- Wired in `SoundChangeRule._compile_rule_text()` at **instantiation** (stored in ``value`` before ``__str__``), after group mappings, ASCA only.
- Corpus dict fields (`input`, `output`, …) and `raw` unchanged.

## Answer (before/after)

Baseline: **1251** rules with `unknown_character` / error_token `ː`.

Smoke re-check on same rows with full compile path (group mappings + length marks, ASCA 0.10.2):

- **644 / 1251** now pass `validate_asca` (~52%).
- **233** still report `Unknown character 'ː'` (bare `(ː)` in sets, meta notation).
- Remainder fail other classes (prose env, nested brackets, etc.).

Re-run full inventory:

```bash
uv run create_index
```

## Notes

- ASCA rejects `(:[+long])`; optional Index `(ː)` maps to `segment:[+long]` (same surface as suffix length).
- Unmatched `ː` left in place for clustering — no silent strip.

## Acceptance criteria

- [x] Class-first ASCA compile transform; index stays applier-neutral
- [x] Unit + ASCA integration tests on representative fixtures
- [x] Smoke before/after metrics recorded
