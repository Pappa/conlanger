Type: task
Status: resolved
Blocked by: 12

# Correction pass: parenthetical segment notation

Target cluster: `syntax_other` — parenthetical **`(`** in I/O segments — **144** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

Rules fail when Index wraps optional or alternation material in parentheses inside segments:

| Bucket | count | example |
|--------|------:|---------|
| `Expected end of line, received '('` | 87 | `z dz ɡ > ɡ {z,dz} ɡ(ʷ)` |
| `Expected … received '('` | 57 | `a > o / #Cw_{(d)l,f3}` |

ASCA rejects `(` in segment position outside env/structure optionals.

## What to build

1. Classify parenthetical uses: optional segment tail (`ɡ(ʷ)`), inline alternation `{(d)l,f3}`, output affix optionals, etc.
2. Implement parse and/or compile transforms — unwrap to ASCA sets `{…}`, move optionals into env/structures, or strip to `comment` when prose-only.
3. Full inventory re-run; record before/after for `syntax_other` rows whose description contains `received '('` or `received '(`.

**Expected impact:** ~**64** ok uplift at ~45% recoverability.

## Policy

- ADR-0010: no valid-but-inaccurate rewrites; `raw` preserved.
- Distinguish phonological optionals from editorial parentheticals (latter → `comment` per edit ladder).

## Acceptance criteria

- [x] Parenthetical pattern taxonomy documented with compile examples
- [x] Handler(s) + tests on representative lines from inventory
- [x] Full inventory re-baseline; metrics in **Answer**
- [x] Fixtures updated where outcomes change

## Answer

Baseline (pre-pass, HEAD inventory): **6792 / 9201** ok (73.8%); `syntax_other` rows with `received '('` in description: **144**.

After parenthetical compile handler (`expand_index_parenthetical_notation`, wired via `expand_meta_notation` after tilde expansion):

- **7066 / 9201** ok (**76.8%**, **+274** vs pre-pass baseline — includes ticket 47 tilde uplift landed in the same regen)
- `received '('` cluster: **144 → 35** (**109** recovered, **75.7%** recoverability; expected ~64 at ~45%)
- Residual 35: editorial prose tails (`(Whimemsz says…)`, `(rare?)`), multi-modifier nests (`{tɕ(ʼ),tɕʷ(ʼ),…}`), `(C)` class-letter optionals in output (`{u,i}(C)`), ASCA env-structure parens (`(C,0)`), and output-side identity alternations (`k > {k(ʼ),q}`)

Taxonomy and compile examples: module docstring in `src/conlanger/tools/asca_compile/parenthetical.py`.

## References

- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: input optionals to env](51-correction-pass-input-optionals-to-env.md) — related options placement
