Type: task
Status: ready-for-agent
Blocked by:

# Correction pass: Index tone features → ASCA `[tone: N]`

Target cluster: `unknown_feature` tone tokens — **`lowtone`** (11), **`hightone`** (8), **`fallingtone`** (3), **`lowfallingtone`** (2), **`highrisingtone`** (2) ≈ **26** rules ([inventory summary](../inventory/asca-rule-inventory-summary.md)).

Priority: **first** under the 2026-08-12 section-completeness re-prioritisation (then [63](63-correction-pass-near-miss-unknown-character.md), then re-review).

## Decision inputs (grill 2026-08-12)

- Use **global Chinese-style** defaults (ASCA doc convention): high=`5`, low=`1`, falling=`51`, low-falling=`21`, high-rising=`35`.
- Override via `manual_mappings` / section comment when a citation disagrees.
- ASCA tone syntax is **`[tone: N]`** — **no** `±`; cannot be negated. Index `V[-tone]` (at least one rule) needs a separate rewrite (drop / manual map), not a CSV rename.

## Open before coding (short probe, ~15–30 min)

ASCA docs do not spell out how `[tone: N]` composes with other matrix features on the same segment/syllable (e.g. `V:[+long][+falling tone]` → ?). **Probe ASCA 0.10.2** with mixed matrices before locking transform shape; record examples on this ticket.

## What to build

1. Probe composition of `[tone: N]` with length/stress/other features; note legal forms.
2. Ingest or compile normaliser: Index `[+high tone]` / `[+low tone]` / … (and collapsed `hightone` tokens) → ASCA `[tone: N]` per global table.
3. Handle `[-tone]` hold-out or manual map (do not invent `[-tone: N]`).
4. Re-run full inventory; record section-complete delta (≤3-fail near-misses preferred) and residual tone tokens.

## Acceptance criteria

- [ ] Composition probe recorded (legal / illegal examples)
- [ ] Global tone table applied; residuals listed
- [ ] Full inventory re-run; before/after ok **and** sections-all-OK counts
- [ ] Fixtures updated for intentionally changed outcomes

## References

- [Spike: Index feature matrices → ASCA targets](29-spike-index-feature-matrices-to-asca-targets.md) — Kind 4 defer; `[tone: N]`
- ASCA 0.10.2 Tone / Suprasegmental features
- [Correction pass template](13-correction-pass-template.md)
