Type: task
Status: resolved
Blocked by:

# Correction pass: double-slash env shorthand

Target cluster: `expected_underscore` — `//` prose env shorthand — **22** near-miss rules (**9** mono-class sections would complete if cleared). Spawned from [106 near-miss prioritisation spike](../issues/106-spike-near-miss-correction-prioritization.md) (2026-09-01). Findings: [near-miss-correction-prioritization.md](../research/near-miss-correction-prioritization.md).

## Problem

Rules use Index `//` as an environment delimiter with prose conditions but no `_` focus:

```
b > w // adjacent to another consonant
t > ð // adjacent to P
r > ur:[+long] / #_e // Logudorese
```

Error: `Expected '_', but received ''`.

Extends the prose-env family from [55 medial](55-correction-pass-prose-env-medial.md); `//` marks a secondary env clause or dialect qualifier.

## What to build

1. Classify `double_slash_no_underscore` shapes ([near-miss-all-classes.csv](../research/near-miss-all-classes.csv)).
2. Parse-time rewrite: structural env + `exception` or `comment` peel for dialect tails (`// Logudorese`).
3. `adjacent to {X}` → neighbour env set (overlap with [107](107-correction-pass-prose-env-positions.md) — coordinate or land together).
4. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [x] Target cluster sized at claim time
- [x] Parse-time transforms; `raw` unchanged
- [x] Full inventory re-run; metrics in **Answer**
- [x] Unit tests per supported `//` shape

## Answer

Baseline (after ticket 107): **8143 / 9677** ok (84.1%); **161** `expected_underscore` failures; target cluster **22** near-miss rows in `double_slash_no_underscore` bucket (**9** mono-class sections cited at spawn).

Full inventory re-run (2026-09-01):

- **8184 / 9677** ok (**+41** rules, **84.6%**)
- Sections all OK: **385 → 399** (**+14**)
- `expected_underscore` failure class: **161 → 116** (−45)
- Implementation: `apply_double_slash_env_conditions` in `double_slash_env.py`, wired after `apply_prose_position_env_conditions` in `parse_rule_element`

**Shapes normalized:** prose exception tails — `adjacent to another consonant` → `C_,_C`; `adjacent to {S}` / `next to {X}` → `_,S` / `_,{X}`; `onset of U[+stress]` → `#_U[+stress]`; `before an identical vowel` → `V_V`; `penult` → `%_`; dialect names (`Logudorese`) → `comment`. Env heads — bare `%[+feature]` / `U[+feature]` → `_ %[+feature]`; `odd syllables` → `_` + comment; `maybe` → `_` + `sporadic`; `∅` env dropped; `, typically` peeled to comment; `medially,` with existing exception → `_` (no boundary exception merge). Sporadic `?` stripped from exceptions when env is uncertain.

**Deferred / residual:** complex Middle English `#% with the following % containing /iː/…` exception prose (slashes inside exception); `O[+voice] earlier in the word`; Mongolic `{r,rʲ,l,lʲ}_ or _ɡ` exception (`or` prose); Shuswap parenthetical set notation; rules where `//` appears only in compiled ASCA output from unrelated failure shapes.

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `expected_underscore` / `double_slash_no_underscore`
