Type: task
Status: ready-for-agent
Blocked by:

# Correction pass: output/env slash boundary (residual)

Target cluster: `syntax_other` — **`Expected end of line… Did you forget a '/' between the output and environment?`** — **23** rules in ≤3-fail sections (**9** mono-class sections would complete if cleared). Full-corpus count TBD at claim time ([inventory summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [64 syntax_other near-miss spike](../issues/64-spike-syntax-other-near-miss-sections.md) (2026-08-19).

## Context

Residual output/environment boundary failures after [48 parenthetical](48-correction-pass-parenthetical-segment-notation.md) and [51 input optionals](51-correction-pass-input-optionals-to-env.md).

| Received token | near-miss count | typical shape |
|---------------:|----------------:|---------------|
| `(` | 12 | output/env glue with unclosed paren |
| `∅` | 3 | deletion concat before `/` |
| `#` | 2 | env anchor in wrong position |
| other | 6 | `&`, `ʲ`, `:`, `̥`, `ˀ`, `_` |

## What to build

1. Sample failing rules; group by fix pattern (insert missing `/`, move paren to env, split output).
2. Parse/compile rewrite for dominant patterns.
3. Full inventory re-run; record before/after for rows matching the exact error message.
4. Unit tests.

## Policy

- Class-first mechanical transforms per edit ladder.
- Do not re-open resolved 48/51 clusters — only residual shapes.

## Acceptance criteria

- [ ] Dominant patterns documented
- [ ] Transform implemented for ≥60% of near-miss cluster
- [ ] Full inventory re-run; before/after in **Answer**
- [ ] Fixtures updated where validation outcomes change

## References

- [Spike: syntax_other near-miss sections](64-spike-syntax-other-near-miss-sections.md)
- [Correction pass: parenthetical segment notation](48-correction-pass-parenthetical-segment-notation.md)
- [Correction pass: input optionals to env](51-correction-pass-input-optionals-to-env.md)
- [Correction pass template](13-correction-pass-template.md)
