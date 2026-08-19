Type: spike
Status: resolved
Blocked by:

# Spike: `syntax_other` in ≤3-fail sections (backlog)

**Backlog** — do not start until after [62](62-correction-pass-tone-features.md) → [63](63-correction-pass-near-miss-unknown-character.md) and a re-review of section-completeness.

## Question

Among sections with **1–3** validation fails, `syntax_other` is the largest lever (**179** rules / **137** sections; **71** mono-class near-misses would go complete if the class cleared). What **subclusters** exist, and which are class-first correction passes vs manual_mappings / skip?

## What to research

1. Re-run inventory; filter sections with `fail_count ≤ 3` and `failure_class == syntax_other`.
2. Bucket by error message / shape (not by Levenshtein alone).
3. Rank buckets by **sections completed** if cleared (not raw rule count).
4. Recommend 1–3 correction-pass instance tickets (or manual_mapping batches).

## Acceptance criteria

- [x] Findings under `.scratch/cleaned-rule-corpus/research/`
- [x] Ranked subcluster table with section-complete impact
- [x] Follow-on correction-pass tickets filed **or** explicit defer/skip recommendation

## Answer

**Resolved 2026-08-19** (post-tickets 62/63 inventory baseline).

Findings: [`syntax-other-near-miss-sections.md`](../research/syntax-other-near-miss-sections.md), CSV [`syntax-other-near-miss-sections.csv`](../research/syntax-other-near-miss-sections.csv), script [`scan_syntax_other_near_miss.py`](../research/scan_syntax_other_near_miss.py).

### Post-63 near-miss metrics (`syntax_other`)

| Metric | Pre-pass sizing (2026-08-12) | Current |
|--------|---------------------------:|--------:|
| Rules in ≤3-fail sections | 179 | **172** |
| Sections hit | 137 | **133** |
| Mono-class near-miss sections | 71 | **85** |

### Top subclusters (sections-completed if cleared)

| complete | rules | subcluster | action |
|---------:|------:|------------|--------|
| 17 | 24 | `null_in_parallel_output_set` | → [81](81-correction-pass-parallel-output-null.md) |
| 9 | 23 | `missing_slash_output_env` | → [82](82-correction-pass-output-env-slash-boundary.md) |
| 4+2 | 23 | `insertion_wildcard_input` + `wildcard_in_correspondence_set` | → [83](83-correction-pass-australasian-wildcard-insertion.md) |
| 4 | 5 | `underscore_env_shorthand` | defer — batch with env-notation pass |
| 3 | 9 | `expected_range_dots` | defer — Yup'ik `V(..)V` |
| 2 | 9 | `word_edge_percent_hash` | defer — compile `%#` / `#%` |
| 2 | 9 | `click_or_exotic_ipa:ǃ` | defer/skip — manual_mappings batch |
| 3 | 5 | `floating_glottal_diacritic` | manual_mappings / skip (Chumash) |

**Filed correction passes:** [81](81-correction-pass-parallel-output-null.md), [82](82-correction-pass-output-env-slash-boundary.md), [83](83-correction-pass-australasian-wildcard-insertion.md).

## References

- [Correction pass template](13-correction-pass-template.md)
- [Inventory summary](../inventory/asca-rule-inventory-summary.md)
