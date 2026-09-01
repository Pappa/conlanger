Type: task
Status: resolved
Blocked by:

# Correction pass: prose env positions

Target cluster: `expected_underscore` — prose environment position phrases — **41** near-miss rules (**13** mono-class sections would complete if cleared). Spawned from [106 near-miss prioritisation spike](../issues/106-spike-near-miss-correction-prioritization.md) (2026-09-01). Findings: [near-miss-correction-prioritization.md](../research/near-miss-correction-prioritization.md).

## Problem

Rules use English position words in the `env` field where ASCA expects `_` focus:

```
a V > e / final syllables
C[+voice] > C[-voice] / next to {P,s,l̥}
t > l / #_, in nouns
```

Error: `Expected '_', but received ''`.

Distinct from [55 medial](55-correction-pass-prose-env-medial.md) (word-internal), [22 stress](22-correction-pass-stress-conditions.md), and [53 else](53-correction-pass-prose-env-else.md).

## What to build

1. Classify prose env shapes in `missing_underscore_other` + `prose_position_env` buckets ([near-miss-all-classes.csv](../research/near-miss-all-classes.csv)).
2. Parse-time normalisation per shape (e.g. `final syllables` → `exception: :{<.._>#}:`, `next to {X}` → neighbour env set) — `raw` unchanged.
3. Defer env+existing-exception merges (Mongolic pattern from ticket 55).
4. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [x] Target cluster sized at claim time from current inventory
- [x] Class-first parse transforms; no silent meaning change
- [x] Full inventory re-run; metrics in **Answer**
- [x] Unit tests for each supported prose shape

## Answer

Baseline (before): **8123 / 9677** ok (84.0%); **179** `expected_underscore` failures; target cluster **50** near-miss rows in `missing_underscore_other` + `prose_position_env` buckets (41 rules cited at spawn included overlap with non-position residuals).

Full inventory re-run (2026-09-01):

- **8143 / 9677** ok (**+20** rules, **84.1%**)
- Sections all OK: **379 → 385** (**+6**)
- `expected_underscore` failure class: **179 → 161** (−18)
- Implementation: `apply_prose_position_env_conditions` in `prose_position_env.py`, wired after `apply_medial_env_conditions` in `parse_rule_element`

**Shapes normalized:** bare `final syllables` / `syllable-final(ly)` → `U#`; `next to {X}` / `adjacent to {X}` → `_,{X}`; `adjacent to a nasal vowel` → `_V[+nasal], V[+nasal]_`; `unstressed syllables` → `_ %[-stress]`; `accented or stressed monosyllables` → `#_[+stress]`; bare `monosyllables` → `#_#`; `typically near *u` → `_,u`; `between two vowels…` → `V_V`; `not universal?` → `_` + `sporadic`; trailing `, in monosyllables|polysyllables|nouns` stripped from structural envs into `comment`.

**Deferred / out of scope (ticket 108+):** `//` exception prose (`adjacent to another consonant`, …); complex multi-clause env (`when pretonic and immediately adjacent to…`); bare `polysyllables`; `%:[+stress]`-only env failures miscounted in near-miss bucket; `before modal suffixes`.

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `expected_underscore` / `missing_underscore_other`
