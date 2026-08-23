# syntax_other in ≤3-fail sections (spike 64)

Research for spike [64](../issues/64-spike-syntax-other-near-miss-sections.md).

Primary sources:

- Inventory: [`asca-rule-inventory.csv`](../inventory/asca-rule-inventory.csv) (post-ticket-63 baseline: **8094 / 9639** ok, **299 / 713** sections all-OK)
- Scan script: [`scan_syntax_other_near_miss.py`](./scan_syntax_other_near_miss.py) → [`syntax-other-near-miss-sections.csv`](./syntax-other-near-miss-sections.csv)

---

## 1. Executive summary

| Metric | Count |
|--------|------:|
| Near-miss sections (1–3 fails) | 282 |
| `syntax_other` rules in near-miss band | 172 |
| Sections with ≥1 such rule | 133 |
| Mono-class near-miss (all fails = `syntax_other`) | 85 |

Pre-pass sizing (2026-08-12) cited **179** rules / **137** sections / **71** mono-class; post-62/63 inventory drift is expected.

## 2. Ranked subclusters (sections-completed if cleared)

| sections complete | sections | rules | subcluster | recommendation |
|------------------:|---------:|------:|------------|----------------|
| 17 | 23 | 24 | `null_in_parallel_output_set` | correction-pass → [81](../issues/81-correction-pass-parallel-output-null.md) |
| 9 | 23 | 23 | `missing_slash_output_env` | correction-pass → [82](../issues/82-correction-pass-output-env-slash-boundary.md) |
| 4 | 9 | 10 | `insertion_wildcard_input` | correction-pass → [83](../issues/83-correction-pass-australasian-wildcard-insertion.md) |
| 4 | 9 | 9 | `underscore_other` | triage / low leverage |
| 4 | 5 | 5 | `underscore_env_shorthand` | defer — correction-pass batched with env notation |
| 4 | 5 | 5 | `ejective_modifier_residual` | defer — overlaps [20](../issues/20-correction-pass-ejective-marks.md) residuals |
| 3 | 6 | 9 | `expected_range_dots` | correction-pass (Yup'ik `V(..)V` range) |
| 3 | 5 | 6 | `paren_in_segment_residual` | correction-pass (ticket 48 follow-on) |
| 3 | 4 | 5 | `floating_glottal_diacritic` | manual_mappings / skip (Chumash) |
| 2 | 12 | 13 | `wildcard_in_correspondence_set` | correction-pass → [83](../issues/83-correction-pass-australasian-wildcard-insertion.md) |
| 2 | 7 | 9 | `word_edge_percent_hash` | correction-pass (compile `%#` / `#%`) |
| 2 | 7 | 9 | `click_or_exotic_ipa:ǃ` | defer — manual_mappings batch or skip |
| 2 | 5 | 5 | `other_syntax` | triage / low leverage |
| 2 | 2 | 2 | `segments_before_word_beg_other` | defer — mixed shapes, low leverage |
| 1 | 6 | 7 | `superscript_segment_modifier` | correction-pass (ticket 50 follow-on) |
| 1 | 3 | 4 | `multiple_underlines_env` | triage / low leverage |
| 1 | 3 | 3 | `slash_in_segment` | triage / low leverage |
| 1 | 2 | 2 | `click_or_exotic_ipa:ǀ` | defer — manual_mappings batch or skip |
| 1 | 1 | 2 | `negation_in_output` | manual_mappings |
| 1 | 1 | 1 | `tone_negation` | manual_mappings (ticket 62 residual) |
| 1 | 1 | 1 | `ipa_received_other:,` | triage / low leverage |
| 0 | 4 | 5 | `ipa_received_other:` | triage / low leverage |
| 0 | 4 | 4 | `click_or_exotic_ipa:ⁿ` | defer — manual_mappings batch or skip |
| 0 | 4 | 4 | `chain_in_wrong_position` | triage / low leverage |
| 0 | 2 | 2 | `ipa_received_other://` | triage / low leverage |
| 0 | 1 | 1 | `ipa_received_other:…` | triage / low leverage |
| 0 | 1 | 1 | `ipa_received_other:ˀ` | triage / low leverage |
| 0 | 1 | 1 | `click_or_exotic_ipa:ǂ` | defer — manual_mappings batch or skip |

## 3. Top-three correction-pass tickets (filed)

1. **[81 — parallel output ∅ sets](../issues/81-correction-pass-parallel-output-null.md)** — **24** rules, **17** mono-class sections complete if cleared. Index writes `{m,∅}` / `{r,∅}` parallel outputs; ASCA wants deletion via `∅` segment or split rules.

2. **[82 — output/env slash boundary](../issues/82-correction-pass-output-env-slash-boundary.md)** — residual `Expected end of line… forget a '/'` after tickets 48/51; mostly `(` concat and env glue.

3. **[83 — Australasian `*X` wildcards](../issues/83-correction-pass-australasian-wildcard-insertion.md)** — `*R`/`*L`/`*j` insertion inputs and `{z,*Z,*D}` correspondence sets; overlaps series expansion policy.

## 4. Defer / skip

- **Khoisan clicks** (`ǃ`, `ǀ`, `ǂ`, `ⁿ` prefix): **16** near-miss rules across **~10** sections — no class-first compile path; batch `manual_mappings` or `status: skipped`.
- **Chumash floating glottal** (`ˀj`, `ˀN`, …): **5** rules, **3** sections — section-local rewrites only.
- **Iroquoian / Yup'ik `%#` env** and **range `..`**: medium leverage (**9+9** rules) but mixed with other failure classes in most sections — file after passes 81–83 land.

