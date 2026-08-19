Type: task
Status: ready-for-agent
Blocked by:

# Correction pass: Australasian `*X` wildcard insertion / correspondence

Target cluster: `syntax_other` — **`*R`/`*L`/`*j`/`*D`/`*Z` in insertion inputs and correspondence sets** — **23** rules in ≤3-fail sections (**6** mono-class sections would complete if cleared). Full-corpus count TBD at claim time ([inventory summary](../inventory/asca-rule-inventory-summary.md)).

Spawned from [64 syntax_other near-miss spike](../issues/64-spike-syntax-other-near-miss-sections.md) (2026-08-19).

## Context

Two related subclusters in Austronesian / Vanuatu sections:

| Subcluster | rules | example |
|------------|------:|---------|
| Insertion input `*X` | 10 | `*R > ∅`, `*L > r`, `*j > ɡ / _#` |
| Wildcard in correspondence set | 13 | `{z,*Z,*D,*j} > d`, `{s,*R} > r / _#` |

ASCA insertion rules require input `*` or `∅` only; `*R` is a correspondence-series placeholder. Overlaps [series mappings policy](../series-mappings-coverage-backlog.md) — prefer `series_expansions` / collective expand over ad-hoc IPA hacks when `*X` is a known series index.

## What to build

1. Inventory which `*X` tokens map to known series (R, L, D, Z, j, …) vs one-off.
2. Parse/compile rewrite: expand series to concrete sets, or rewrite `*X` insertion → bare `*` + env/structure when faithful.
3. Full inventory re-run; record before/after for both subclusters.
4. Coordinate with [65 series coverage](65-series-mappings-coverage-pass.md) — do not duplicate series CSV work.

## Policy

- Series-first when `*X` is a documented correspondence index.
- Compile/parse fix; `raw` unchanged.

## Acceptance criteria

- [ ] `*X` token inventory with series vs ad-hoc classification
- [ ] Transform implemented for dominant tokens
- [ ] Full inventory re-run; before/after in **Answer**
- [ ] Fixtures updated where validation outcomes change

## References

- [Spike: syntax_other near-miss sections](64-spike-syntax-other-near-miss-sections.md)
- [Series mappings coverage pass](65-series-mappings-coverage-pass.md)
- [Correction pass template](13-correction-pass-template.md)
