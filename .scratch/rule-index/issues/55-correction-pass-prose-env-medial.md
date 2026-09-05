Type: task
Status: resolved
Blocked by: 12

# Correction pass: prose env medial

Target cluster: `expected_underscore` — prose environment **`medial`** / **`medially`** — **~55** rules at current inventory baseline ([summary](../inventory/rule-inventory-summary.md); ticket spawn note said 52).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08). **Grill 2026-08-10** locked semantics and parse-time rewrite policy (below).

## Problem

Rules use English position words in the env field where ASCA expects `_` focus, e.g.:

```
t > r / medially
t > j / medially
```

Error: `Expected '_', but received ''`.

Distinct from ticket [22](22-correction-pass-stress-conditions.md) (stress prose) and [53](53-correction-pass-prose-env-else.md) (`else` catch-alls).

## Decision (grill 2026-08-10)

**Parse-time** normalization on `env` / `exception` (same placement as passes 22 and 53; `raw` unchanged).

### Meaning

Bare Index **`medial`** / **`medially`** means **word-internal** — the focus segment is neither word-initial nor word-final. This is the complement of explicit boundary envs in sibling rules (e.g. Proto-Agaw `{x,ɢ}(ʷ) → ∅ / at word boundaries` → `#_, _#` vs `t → r / medially`).

**Not** intervocalic (`V_V`) by default. Tentative author comments (e.g. Proto-Italic `s → z / medial (I'm assuming between vowels…)`) stay in **`comment`** and do **not** drive a narrower rewrite.

**Do not** map medial to `#_, _#` — in ASCA that shorthand means **at word boundaries** (initial or final), the opposite of medial.

### ASCA encoding

Word-internal position requires an **environment set** on the exception — plain `// #_, _#` does **not** block both edges (verified ASCA 0.10.2):

| Rewrite | ASCA emit |
| --- | --- |
| bare `medial` / `medially` | `env: _` + `exception: :{#_, _#}:` → `_ // :{#_, _#}:` |
| structural env + `, when medial` / `when medial`, **no** existing `exception` | strip qualifier; keep env; set `exception: :{#_, _#}:` |
| env + **existing** `exception` (e.g. Mongolic `b → h / medially, ! …`) | **defer** — leave unchanged (cf. ticket 53 env+exception deferrals; no exception-merge until designed) |

Out of scope: **`comment`**-only medial qualifiers where `env` is already structural (e.g. `kʷ → ʍ / ku_ (medial)`).

### Implementation sketch

1. Post-pass (or extend env normalizer) in `IndexDiachronicaParser` / `parsers.py`: `apply_medial_env_conditions` on `env` and `exception` fields after stress pass, before or alongside other env prose handlers.
2. Strip trailing commas after `medially` (`medially,` → medial handler input when exception is separate field).
3. Tests: bare medial; `when medial` on `_k` and `C[-voice]_n`; Proto-Italic comment-only case unchanged in env; one deferred env+exception pair left failing; ASCA trace spot-check (`ta`/`at` unchanged, `ata`/`stak` change).
4. Full inventory re-run; record before/after.

**Expected impact:** ~**54** ok uplift (55 cluster − 1 deferred Mongolic); prior ~50% estimate was pessimistic given unified word-internal policy.

## Policy

- `raw` unchanged; no valid-but-inaccurate env guesses.
- Comment prose does not narrow env rewrites.
- Unmappable / deferred shapes → leave literal or `status: skipped` with validation report reason (no stub env).

## Acceptance criteria

- [x] Parse-time transform per Decision table
- [x] Deferred env+exception pair still fails compile validation
- [x] Tests on inventory samples + ASCA boundary spot-check
- [x] Full inventory re-baseline; cluster size in **Answer**
- [x] Fixtures updated where outcomes change
- [x] `CONTEXT.md` Environment / Exception wording aligned

## Answer

Baseline (before): **7394 / 9201** ok (80.4%); **55** rules with `env` matching bare `medial` / `medially` / `when medial` (including trailing-comma Mongolic).

Full inventory re-run:

- **7447 / 9201** ok (**+53** rules, **80.9%**)
- Medial env cluster: **55 → 1** (54 rewritten; 1 deferred Mongolic `b → h / medially, ! …` still has `env: medially,`)
- `expected_underscore` failure class: **338 → 285** (−53)
- Implementation: `apply_medial_env_conditions` in `parse_rule_element` after `apply_stress_conditions`

## References

- Grill 2026-08-10 (word-internal medial; env-set exception; parse-time; defer env+exception merge)
- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: prose env else](53-correction-pass-prose-env-else.md)
- [Correction pass: stress conditions](22-correction-pass-stress-conditions.md)
- ASCA 0.10.2: condensed env `#_, _#` vs [Environment Sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#environment-sets) for multi-match exceptions
