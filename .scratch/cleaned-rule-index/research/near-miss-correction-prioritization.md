# Near-miss correction-pass prioritisation (spike 106)

Research for spike [106](../issues/106-spike-near-miss-correction-prioritization.md) (2026-09-01).

**Primary sources:**

- Inventory regen: `uv run create_index && uv run validate_rules` → [`asca-rule-inventory-summary.md`](../inventory/asca-rule-inventory-summary.md), [`asca-rule-inventory-success.csv`](../inventory/asca-rule-inventory-success.csv), [`asca-rule-inventory-error.csv`](../inventory/asca-rule-inventory-error.csv)
- Scan: [`scan_near_miss_all_classes.py`](./scan_near_miss_all_classes.py) → [`near-miss-all-classes.csv`](./near-miss-all-classes.csv)
- Auxiliary CSVs: [`underscore_errors.csv`](../inventory/underscore_errors.csv), [`nested_brackets_errors.csv`](../inventory/nested_brackets_errors.csv), [`character_errors.csv`](../inventory/character_errors.csv), [`unknown_features.csv`](../inventory/unknown_features.csv), [`asca-field-isolation-error.csv`](../inventory/asca-field-isolation-error.csv)
- Prior spike: [`syntax-other-near-miss-sections.md`](./syntax-other-near-miss-sections.md) (spike 64)

---

## 1. Executive summary

Re-ran the full inventory on 2026-09-01. **Headline metrics match the spike-106 spawn baseline** — no inventory drift on ok/fail/skipped or sections-all-OK. Near-miss failing-rule count is **375** (down from **412** cited at spawn; post-98/104 uplift).

**Top four correction-pass levers** (by sections-completed-if-cleared, mono-class):

| Rank | Bucket | Sections complete | Rules | Filed ticket |
|-----:|--------|------------------:|------:|--------------|
| 1 | `expected_underscore` / prose env missing `_` | **13** | 41 | [107](../issues/107-correction-pass-prose-env-positions.md) |
| 2 | `expected_underscore` / `//` env without `_` | **9** | 22 | [108](../issues/108-correction-pass-double-slash-env.md) |
| 3 | `syntax_other` / parallel `∅` residuals | **8** | 10 | [109](../issues/109-correction-pass-parallel-output-null-residual.md) |
| 4 | `diacritic_prereq` / voice prerequisite on lengthening | **5** | 10 | [110](../issues/110-correction-pass-diacritic-prerequisite-lengthening.md) |

**Next batch after 107–110:** `prose_or_expected_arrow` / `Vˀ` before arrow (**10** sections, **20** rules) — defer to `manual_mappings` / `status: skipped` (Athabaskan tone cluster; no class-first compile path without owner policy). `syntax_other` / `expected_range_dots` (**5** sections, **12** rules) — file when queue clears.

**Defer / manual / blocked:**

- `nested_brackets` (**9** mono-class sections) — Family A/B shapes blocked on [71 grill](../issues/71-grill-paren-and-parallel-set-notation.md) owner confirm
- Khoisan clicks (`click_or_exotic_ipa:*`) — `manual_mappings` / `status: skipped` (spike 64 policy unchanged)
- `unknown_character` (**31** mono-class sections) — token-scattered residuals after [63](../issues/63-correction-pass-near-miss-unknown-character.md); batch `ipa_mappings` when clusters warrant
- `runtime_other` / word-boundary-in-I/O — overlaps paused grill 71 Q4 (`#` in I/O → manual)

---

## 2. Baseline drift

| Metric | Issue 106 spawn | 2026-09-01 regen | Drift |
|--------|----------------:|-----------------:|------:|
| Rules OK / fail / skipped | 8123 / 942 / 612 | **8123 / 942 / 612** | none |
| Sections all-OK | 379 / 689 (53.1%) | **379 / 714** (53.1% active) | none on rate; denominator includes 25 skipped sections |
| Near-miss sections (1–3 fails) | 240 | **240** | none |
| Near-miss failing rules | 412 | **375** | **−37** (rules flipped ok by passes 98, 104, …) |
| Mono-class near-miss sections | 176 | **176** | none |

Near-miss failure-class mix (rules, current inventory):

| count | `failure_class` | spawn count |
|------:|-----------------|------------:|
| 108 | `syntax_other` | 108 |
| 89 | `expected_underscore` | 89 |
| 61 | `unknown_character` | 61 |
| 27 | `prose_or_expected_arrow` | 27 |
| 20 | `nested_brackets` | 20 |
| 16 | `expected_number` | 16 |
| 14 | `runtime_other` | 14 |
| 14 | `unknown_feature` | 14 |
| 10 | `diacritic_prereq` | — |
| 6 | `unknown_grouping` | — |
| 3 | `panic_other` | — |
| 2 | `runtime_delete_only_segment` | — |
| 1 | `other` | — |
| 1 | `format_error` | — |
| 1 | `stuff_after_word_bound` | — |

Mono-class near-miss sections by class (unchanged from spawn): `syntax_other` **56**, `expected_underscore` **34**, `unknown_character` **31**.

---

## 3. Ranked subclusters (sections-completed if cleared)

Primary metric: mono-class sections where **all** fails fall in the bucket. Secondary: rule count.

| complete | sections | rules | failure_class | subcluster | recommendation |
|---------:|---------:|------:|---------------|------------|----------------|
| 13 | 33 | 41 | `expected_underscore` | `missing_underscore_other` | correction-pass → [107](../issues/107-correction-pass-prose-env-positions.md) |
| 10 | 20 | 20 | `prose_or_expected_arrow` | `tone_or_voice_mark_as_arrow:ˀ` | **defer** — manual/skip (Athabaskan tone) |
| 9 | 20 | 22 | `expected_underscore` | `double_slash_no_underscore` | correction-pass → [108](../issues/108-correction-pass-double-slash-env.md) |
| 8 | 10 | 10 | `syntax_other` | `null_in_parallel_output_set` | correction-pass → [109](../issues/109-correction-pass-parallel-output-null-residual.md) |
| 6 | 15 | 16 | `nested_brackets` | `other_nested` | **defer** — [71](../issues/71-grill-paren-and-parallel-set-notation.md) |
| 5 | 7 | 12 | `syntax_other` | `expected_range_dots` | defer — next batch after 107–110 |
| 5 | 6 | 10 | `diacritic_prereq` | `voice_prerequisite_diacritic` | correction-pass → [110](../issues/110-correction-pass-diacritic-prerequisite-lengthening.md) |
| 4 | 5 | 5 | `unknown_character` | `letter:ŕ` | `ipa_mappings` batch |
| 4 | 5 | 5 | `syntax_other` | `ejective_modifier_residual` | defer — overlaps [20](../issues/20-correction-pass-ejective-marks.md) |
| 3 | 7 | 7 | `syntax_other` | `other_syntax` | triage |
| 3 | 6 | 6 | `unknown_character` | `diacritic:̊` | `ipa_mappings` / compile diacritic |
| 3 | 4 | 5 | `syntax_other` | `paren_in_segment_residual` | defer — [48](../issues/48-correction-pass-parenthetical-segment-notation.md) follow-on / [71](../issues/71-grill-paren-and-parallel-set-notation.md) |
| 3 | 3 | 3 | `syntax_other` | `floating_glottal_diacritic` | manual_mappings / skip (Chumash) |
| 2 | 9 | 10 | `expected_underscore` | `other_underscore` | fold into [107](../issues/107-correction-pass-prose-env-positions.md) triage |
| 2 | 9 | 9 | `expected_underscore` | `prose_position_env` | fold into [107](../issues/107-correction-pass-prose-env-positions.md) |
| 2 | 7 | 8 | `syntax_other` | `superscript_segment_modifier` | defer — [50](../issues/50-correction-pass-superscript-segment-modifiers.md) residual |
| 2 | 6 | 7 | `syntax_other` | `click_or_exotic_ipa:ⁿ` | defer — manual/skip |
| 2 | 3 | 3 | `nested_brackets` | `true_nested_braces` | defer — [71](../issues/71-grill-paren-and-parallel-set-notation.md) |
| 1 | 8 | 8 | `syntax_other` | `missing_slash_output_env` | residual after [82](../issues/82-correction-pass-output-env-slash-boundary.md) — low mono-class leverage |

Full row-level data: [`near-miss-all-classes.csv`](./near-miss-all-classes.csv) (375 rows).

---

## 4. Stale spike-64 recommendations

From [`syntax-other-near-miss-sections.md`](./syntax-other-near-miss-sections.md) — status per [`map.md`](../map.md):

| Spike-64 lever | Ticket | Status |
|----------------|--------|--------|
| `null_in_parallel_output_set` | [81](../issues/81-correction-pass-parallel-output-null.md) | **resolved** — 10 near-miss residuals remain → [109](../issues/109-correction-pass-parallel-output-null-residual.md) |
| `missing_slash_output_env` | [82](../issues/82-correction-pass-output-env-slash-boundary.md) | **resolved** — 8 near-miss rules residual, 1 mono-class section |
| `insertion_wildcard_input` / `wildcard_in_correspondence_set` | [83](../issues/83-correction-pass-australasian-wildcard-insertion.md) | **wontfix** — superseded by [97 `section_mappings`](../issues/97-implement-parser-config-section-mappings.md) |
| `expected_range_dots` | — | still open — defer next batch after 107–110 |
| `word_edge_percent_hash` | — | defer — mixed failure classes |
| Khoisan clicks | — | defer — manual/skip (unchanged) |
| Chumash floating glottal | — | manual/skip (unchanged) |
| Group-mapping passes | [95](../issues/95-correction-pass-group-mapping-boundaries-unglued.md) / [96](../issues/96-correction-pass-group-mapping-residual.md) | **resolved** |
| `#U`/`U#` syllable position | [98](../issues/98-correction-pass-syllable-position-u-hash.md) | **resolved** |
| `(ː)` optional length | [104](../issues/104-correction-pass-parenthesized-optional-length-marker.md) | **resolved** |

---

## 5. Open decision blockers

### [71 — parenthetical + parallel-set notation](../issues/71-grill-paren-and-parallel-set-notation.md) (paused 2026-08-29)

Blocks **9** mono-class `nested_brackets` near-miss sections and follow-on taxonomy for [48](../issues/48-correction-pass-parenthetical-segment-notation.md) / [51](../issues/51-correction-pass-input-optionals-to-env.md). Spike [100](../issues/100-spike-io-optionals-asca-and-convention.md) resolved Q2/Q4/Q9; grill awaits **owner confirm** before filing implementation tickets. Near-miss scan shows `other_nested` (6 sections), `optional_prefix_parallel_column`, `segment_template_parallel_set` — do not file correction passes until 71 closes.

### [45 — inter-segment whitespace placement](../issues/45-grill-inter-segment-whitespace-placement.md) (ready-for-human)

Compile-only Brassica spacing policy from [spike 44](../issues/44-spike-inter-segment-whitespace.md). Prototype [46](../issues/46-prototype-parse-time-inter-segment-whitespace.md) leans no-go on parse-time SoT mutation. Not a near-miss top lever today, but whitespace-sensitive parallel sets in `nested_brackets` rows may need this decision before mechanical flatten passes.

---

## 6. Recommended next queue

Filed correction-pass instances (ticket-13 shape):

1. **[107 — prose env positions](../issues/107-correction-pass-prose-env-positions.md)** — **13** mono-class sections
2. **[108 — double-slash env shorthand](../issues/108-correction-pass-double-slash-env.md)** — **9** mono-class sections
3. **[109 — parallel `∅` residuals](../issues/109-correction-pass-parallel-output-null-residual.md)** — **8** mono-class sections
4. **[110 — diacritic prerequisite lengthening](../issues/110-correction-pass-diacritic-prerequisite-lengthening.md)** — **5** mono-class sections

**Explicit defer:** Athabaskan `Vˀ` / `tone_or_voice_mark_as_arrow:ˀ` (**10** sections — manual/skip), `expected_range_dots` (**5** sections — next batch), `nested_brackets` (71), Khoisan clicks, Chumash glottal, scattered `unknown_character` tokens.

**Estimated ceiling** if passes 107–110 land without regression: **+35** sections-all-OK (sum of mono-class subcluster impacts; some overlap possible across 107/108).
