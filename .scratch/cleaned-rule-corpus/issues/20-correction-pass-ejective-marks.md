Type: task
Status: resolved
Blocked by: 15

# Correction pass: ejective marker ʼ (U+02BC)

Target cluster: `prose_or_expected_arrow` / `syntax_other` — error_token `ʼ` (~83+ rules)

## Problem

Index Diachronica places ejective `ʼ` **after** feature matrices and sets (`ts:[+long]ʼ`, `{t,ts}ʼ`). ASCA parses `ʼ` only as a **segment diacritic** (before `:`) or as the feature **`[+cg]`**. See `.scratch/cleaned-rule-corpus/research/asca-ejective-notation.md`.

## What was built

- `normalize_asca_ejective_marks()` in `src/conlanger/tools/rules.py` — ASCA compile transform:
  1. `segment:[features]ʼ` → `segment:[features,+cg]`
  2. `{members}ʼ` → `{member:[+cg],…}` per set member
  3. bare `segmentʼ` → `segment:[+cg]` (voiced ejectives + normalize voiceless)
- Wired in `RuleChange._compile_rule_text()` after length marks, ASCA only.
- Corpus dict fields and `raw` unchanged.

## Acceptance criteria

- [x] Research doc explaining ASCA ejective representation
- [x] Class-first ASCA compile transform
- [x] Unit + ASCA integration tests on representative fixtures
- [x] Smoke before/after metrics recorded

## Answer (before/after)

Baseline (after issue 19): **5674 / 9334** ok (60.8%).

Full inventory re-run with ejective compile transform:

- **5713 / 9334** ok (**+39** rules)
- `received 'ʼ'` syntax errors reduced substantially; remainder are `(ʼ)` optional notation, prose, etc.
