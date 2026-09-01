Type: task
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

- [ ] Target cluster sized at claim time
- [ ] Parse-time transforms; `raw` unchanged
- [ ] Full inventory re-run; metrics in **Answer**
- [ ] Unit tests per supported `//` shape

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `expected_underscore` / `double_slash_no_underscore`
