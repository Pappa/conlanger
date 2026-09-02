Type: spike
Status: resolved
Blocked by:

# Spike: near-miss correction-pass prioritisation (post-104 baseline)

Spawned from [wayfinder session 2026-08-31](../map.md): the map's correction-pass queue predates passes 81–83, 95–98, 99, 104, per-field blame, and the parse/validate split. **Do not file the next batch of ticket-13 instances until this spike resolves.**

Precedent: [Spike: `syntax_other` in ≤3-fail sections](64-spike-syntax-other-near-miss-sections.md) (2026-08-12) — same success metric, broader scope.

## Question

Given the **current** inventory, which failure-class **subclusters** in sections with **≤3** fails yield the highest **sections-all-OK** payoff — and which should become the next 2–4 correction-pass instances (vs `manual_mappings` / `status: skipped` / defer)?

## Baseline (inventory summary at ticket spawn)

| Metric | Value |
|--------|------:|
| Rules OK / fail / skipped | **8123** / **942** / **612** |
| Sections all-OK | **379 / 689** (53.1%) |
| Near-miss sections (1–3 fails) | **240** |
| Near-miss failing rules | **412** |

Near-miss failure-class mix (rules, not sections):

| count | `failure_class` |
|------:|-----------------|
| 108 | `syntax_other` |
| 89 | `expected_underscore` |
| 61 | `unknown_character` |
| 27 | `prose_or_expected_arrow` |
| 20 | `nested_brackets` |
| 16 | `expected_number` |
| 14 | `runtime_other` |
| 14 | `unknown_feature` |

Mono-class near-miss sections: **176** (largest: `syntax_other` 56, `expected_underscore` 34, `unknown_character` 31).

## What to research

1. Re-run `uv run create_index && uv run validate_rules`; confirm baseline matches or note drift.
2. Filter **all** failure classes in sections with `fail_count ≤ 3` (not `syntax_other` only).
3. Bucket by shape / error message / field blame — reuse and extend [`scan_syntax_other_near_miss.py`](../research/scan_syntax_other_near_miss.py) pattern; pull from [`expected_underscore_errors.csv`](../inventory/expected_underscore_errors.csv), [`nested_brackets_errors.csv`](../inventory/nested_brackets_errors.csv), [`unknown_character_errors.csv`](../inventory/unknown_character_errors.csv), [`asca-field-isolation-error.csv`](../inventory/asca-field-isolation-error.csv) where useful.
4. Rank buckets by **sections completed if cleared** (primary), rule-ok delta (secondary).
5. Cross-check against **resolved** spike-64 levers (81–83, 97 superseding 83) — mark stale recommendations.
6. Note dependencies on open decisions: [Grill: parenthetical + parallel-set notation](71-grill-paren-and-parallel-set-notation.md) (owner confirm → 48/51 re-scope), [Grill: inter-segment whitespace placement](45-grill-inter-segment-whitespace-placement.md).
7. Recommend **2–4** numbered correction-pass instance tickets **or** explicit defer/skip/manual batches.

## Acceptance criteria

- [x] Findings under `.scratch/cleaned-rule-index/research/` (markdown + CSV + scan script if new)
- [x] Ranked subcluster table with section-complete impact on **current** inventory
- [x] Follow-on correction-pass tickets filed **or** explicit defer/skip/manual recommendation
- [x] Map Notes / implementation plan updated with the chosen next queue

## Answer

**2026-09-01** — Findings: [near-miss-correction-prioritization.md](../research/near-miss-correction-prioritization.md). Scan: [scan_near_miss_all_classes.py](../research/scan_near_miss_all_classes.py) → [near-miss-all-classes.csv](../research/near-miss-all-classes.csv).

Baseline confirmed: **8123 / 942 / 612** rules; **379 / 689** sections all-OK; **240** near-miss sections; **375** near-miss failing rules (vs spawn **412**).

Filed correction passes [107](../issues/107-correction-pass-prose-env-positions.md)–[110](../issues/110-correction-pass-diacritic-prerequisite-lengthening.md). Defer: Athabaskan `Vˀ` (manual/skip), nested I/O ([71](../issues/71-grill-paren-and-parallel-set-notation.md)), Khoisan clicks.

## References

- [Correction pass template](13-correction-pass-template.md)
- [Inventory summary](../inventory/asca-rule-inventory-summary.md)
- [Spike 64 findings](../research/syntax-other-near-miss-sections.md) (superseded levers marked in new findings)
