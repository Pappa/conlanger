Type: task
Status: ready-for-agent
Blocked by: 12

# Correction pass: Index tilde notation

Target cluster: `syntax_other` — Index **`~`** notation — **233** rules at current inventory baseline ([summary](../inventory/asca-rule-inventory-summary.md)); largest residual `syntax_other` cluster.

Spawned from [correction pass template](13-correction-pass-template.md) prioritisation (2026-08-08).

## Problem

Rules fail with tilde-related syntax errors across two bucket shapes:

| Bucket | count | example message |
|--------|------:|-----------------|
| `Expected … received '~'` | 112 | `ʃ(~ʃ:[+long]) ʒ > sʲ sʲ` |
| `Expected end of line, received '~'` | 82 | `{β,w} > bj~vj~v` |
| other `~` in description | ~39 | mixed |

Index uses `~` for optional segments, repetition, and output-chain glue. ASCA 0.10.2 rejects bare `~` in I/O segments.

## What to build

1. Identify dominant Index `~` patterns in the cluster (optional wrapper, chained outputs, env-adjacent repetition).
2. Implement a **class-first** compile and/or parse normaliser per [edit ladder](04-historical-fidelity-vs-validity.md) and ADR-0010 — expand toward ASCA-valid sets, optionals in env/structures, or compile-time chain splits where the phonological claim is preserved.
3. Hold out rules that cannot be expressed without meaning change (`status: skipped` + validation report reason).
4. Full inventory re-run; record before/after for `syntax_other` rows whose description contains `~`.

**Expected impact:** ~**81** ok uplift at ~35% recoverability (upper bound; overlaps with other clusters possible).

## Policy

- `raw` and `source` unchanged; transforms are mechanical class rewrites.
- Do not silently drop optional/repetition semantics — prefer env/structure placement or documented skip.
- One ticket for all `~` surface notation (do not split received-`~` vs EOL-`~` unless residual cluster forces Phase 2).

## Acceptance criteria

- [ ] Dominant `~` patterns documented with before/after compile examples
- [ ] Class-first handler(s) implemented with unit tests on representative inventory lines
- [ ] Full inventory re-baseline; ok/fail delta and residual `~` cluster size in **Answer**
- [ ] Fixtures updated for rules whose validation outcome changed

## Answer

_(pending)_

## References

- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: chain split](18-correction-pass-chain-split.md) — related multi-segment output handling
- [Inventory summary](../inventory/asca-rule-inventory-summary.md)
