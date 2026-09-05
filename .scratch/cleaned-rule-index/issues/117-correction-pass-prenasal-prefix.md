Type: task
Status: resolved
Blocked by: None

# Correction pass: prenasal ⁿ prefix normalisation

Target cluster: `invalid_ipa` — Unicode prenasal prefix `ⁿ` on segments — **11** failing rules (**6** mono-class sections would complete if cleared). Spawned from [114 IPA prioritisation spike](../issues/114-spike-ipa-correction-prioritization.md) (2026-09-05). Findings: [ipa-correction-prioritization.md](../research/ipa-correction-prioritization.md).

## Problem

Rules use Index prenasal prefix notation where ASCA cannot resolve the `ⁿ` grapheme:

```
P > ⁿP / #NV_
s ʃ > ⁿs ⁿʃ / _ %[-nas]
NVP > VⁿP / #_
N[-tense] N[+tense] > N[+tense] ⁿP / _ C=2 position
```

Error: `Could not get value of IPA 'ⁿ'.`

Concentrated in §7.13 (Algonquian), §10.3.5.x (Austronesian), §24.1.5/7 (Paman), §30.1.1 (Bantu).

Distinct from Khoisan click notation (§20.x — defer per [spike 64](../research/syntax-other-near-miss-sections.md)).

## What to build

1. Classify `prenasal_prefix` segment shapes ([ipa-correction-classes.csv](../research/ipa-correction-classes.csv)).
2. Compile `normalize_prenasal_prefix()` — expand `ⁿP` → prenasal segment or `N` + `P` matrix form ASCA accepts; handle output-side `VⁿP`.
3. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [x] Target cluster sized at claim time from current inventory
- [x] Class-first compile normalisation; no silent meaning change
- [x] Full inventory re-run; metrics in **Answer**
- [x] Unit tests for input-side, output-side, and env-adjacent shapes

## Answer

**Shipped 2026-09-05.** Added `normalize_prenasal_prefix()` in `src/conlanger/tools/compile/asca/prenasal_prefix.py` (wired in `compile_asca_field_post_subscript`).

### Implementation

- **Class prefix:** `ⁿP` → `N P` (Index prenasal prefix on class letters).
- **Class infix:** `VⁿP` → `V N P` (Paman NVS output shape).
- **IPA prefix:** `ⁿs`, `ⁿʃ` → `N s`, `N ʃ` (two-segment form ASCA accepts).
- **Literal graphemes:** `ⁿd`, `ⁿt` left unchanged (ASCA-registered prenasal segments).
- **Bracket-safe:** feature matrices `[...]` untouched; `(ⁿ)` inside optionals not expanded.

### Inventory

Pre-pass summary: **8363 / 9827 ok (85.1%)**; `invalid_ipa` **58**; `prenasal_prefix` cluster **11** rules / **6** mono-class sections.

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK / total | 8363 / 9827 (85.1%) | **8374 / 9827 (85.2%)** | **+11 ok** |
| Fail | 692 | **681** | **−11** |
| All-OK sections | 431 / 714 | **437 / 714** | **+6** |
| `invalid_ipa` | 58 | **47** | **−11** |
| `prenasal_prefix` | 11 | **0** | **−11** |

**ok flips (+11):** Miami-Illinois `ⁿP`/`ⁿs ⁿʃ` ×2 (§7.13); Proto-New Caledonia `ⁿP`/`NP > ⁿP` (§10.3.5); Caaàc/Nixumwak/Nyelâyu/Proto-Yunaga `ⁿP > N` ×5 (§10.3.5.1/4.1/5/8); Mpalican/Yinwum `VⁿP` ×2 (§24.1.5/7); Proto-Bantu `ⁿP` (§30.1.1).

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan bucket: `invalid_ipa` / `prenasal_prefix`
