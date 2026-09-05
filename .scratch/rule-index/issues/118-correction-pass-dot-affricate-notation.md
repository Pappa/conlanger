Type: task
Status: resolved
Blocked by: None

# Correction pass: dot-affricate and cluster notation

Target cluster: `expected_range_dots` — European dot-separated affricates and consonant clusters — **35** failing rules (**3** mono-class sections would complete if cleared; **+1** with `dot_inside_set` fold-in). Spawned from [114 IPA prioritisation spike](../issues/114-spike-ipa-correction-prioritization.md) (2026-09-05). Findings: [ipa-correction-prioritization.md](../research/ipa-correction-prioritization.md).

## Problem

Rules use Index dot notation for affricates or cluster splits where ASCA expects `..` range syntax or bare segments:

```
ttʃ ddʒʱ > t.ʃ d.ʒʱ
s:[+long] ʂ:[+long] > t.s t.ʂ
p çp b > p. ç.w p
t st tr d > t. s.d tr.
```

Error: `Expected '..'` (ASA range-dot parser) on `.` inside segments.

Concentrated in §17.10 (Indo-Iranian affricates) and §36.3.2.x (Tibeto-Burman cluster notation). Yup'ik §24.x geminate `V.V` shapes are **not** in this cluster on current inventory.

## What to build

1. Classify `european_dot_affricate` and `dot_inside_set` shapes ([ipa-correction-classes.csv](../research/ipa-correction-classes.csv)).
2. Compile pass: expand `C1.C2` dot clusters to ASCA-parseable segment sequences or matrices (policy: affricate `t.ʃ` → `tʃ` or `t ʃ` per ASCA segment model).
3. Defer Yup'ik `..` range shapes (0 active rows) and mixed-failure §36.3 sections until mono-class leverage warrants.
4. Full inventory re-run; before/after in **Answer**.

## Acceptance criteria

- [x] Target cluster sized at claim time from current inventory
- [x] Class-first compile transforms; `raw` unchanged
- [x] Full inventory re-run; metrics in **Answer**
- [x] Unit tests for Indo-Iranian affricate and Tibeto-Burman cluster families

## Answer

**Shipped 2026-09-05.** Added `normalize_dot_affricate_notation()` in `src/conlanger/tools/compile/asca/dot_affricate.py` (wired in `compile_asca_field_post_subscript`).

### Implementation

- **Affricate / cluster join:** `t.ʃ`, `s.d`, `n.br` → concatenate (`tʃ`, `sd`, `nbr`).
- **Trailing dot:** `p.`, `tr.`, `kj.` → drop dot (`p`, `tr`, `kj`).
- **After feature matrix:** `je:[+stress].o` → `je:[+stress]o`.
- **Before set / optional:** `s.{ts,pj}`, `(ç.)tr` → `s{ts,pj}`, `(ç)tr`.
- **Inside sets / env:** `{s.ts,br}`, `_{ŋ.nj}`, `{i3.ə3}` → `{sts,br}`, `_{ŋnj}`, `{i3ə3}`.
- **Subscript digits:** segment tail allows Index tone/subscript digits (`i3`, `ə3`).
- **Range dots preserved:** `..` left unchanged (Yup'ik geminate ranges).

### Inventory

Pre-pass summary: **8379 / 9827 ok (85.3%)**; `expected_range_dots` **41**; cluster **35** rules / **3** mono-class sections (+1 with `dot_inside_set` fold-in).

| Metric | Before | After | Δ |
|--------|-------:|------:|--:|
| OK / total | 8379 / 9827 (85.3%) | **8418 / 9827 (85.7%)** | **+39 ok** |
| Fail | 676 | **637** | **−39** |
| All-OK sections | 437 / 714 | **442 / 714** | **+5** |
| `expected_range_dots` | 41 | **0** | **−41** |

**ok flips (+39):** §17.10 PIIr affricates; §17.10.1.5 Vedic `t.s`/`t.ʂ`/`t.C` ×2; §17.12.1.1.10 Spanish stress+dot; §36.3.2.1 bTshan La env; §36.3.2.1.1 Chos Kia ×14; §36.3.2.1.2 Hanniu ×3; §36.3.2.2.1 Kham To ×3; §36.3.2.2.3 Pati; §36.3.2.2.4 Suo Mo ×6; §36.3.2.2.6 Tsa Ku Nao ×4; §36.3.2.2.7 Tzu Ta; §36.3.2.2.8 Wassu ×2.

**Residual:** §35.1.7 Nooksack `{i3.ə3}` dot cleared but rule still fails `unknown_reference` on subscript digits (out of scope).

## References

- [Correction pass template](13-correction-pass-template.md)
- Scan buckets: `expected_range_dots` / `european_dot_affricate`, `dot_inside_set`
