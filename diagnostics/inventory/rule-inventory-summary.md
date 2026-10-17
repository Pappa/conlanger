# Cleaned rule index — ASCA validation inventory

- Source YAML: `diagnostics/compile/asca_rules.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.3**
- Rows: **9570** (one per compile-expanded validation target; optional outputs use `alt_idx`, multi-stage chains use `step_idx`)

## Rules
- OK: **8272** (86.4%)
- Fail: **1257** (13.1%)
- Skipped: **41** (0.4%)


## Corrections

OK: **108/122**
Fail: **14/122**

### Failed corrections

- `Biblical-Hebrew-p-b-t-d-k-ɡ` — `other`
- `Cheyenne-W` — `unknown_grouping`
- `Dacian-kʷ,kw-ɡʷ,ɡw` — `unknown_grouping`
- `Guānhuà-jem,jen` — `other`
- `Old-Provençal-β_6` — `unknown_grouping`
- `Old-Russian-kt-ɡd` — `unknown_grouping`
- `Proto-Boreafrasian-z` — `other`
- `Proto-Erromango-r` — `other`
- `Proto-Indo-Iranian-s` — `unknown_character`
- `Proto-Mongolic-pʰ_3` — `unknown_grouping`
- `Proto-Slavic-Kʷ-ḱ-ɡ́` — `prose_or_expected_arrow`
- `Proto-Tungusic-U-long-+low-pitch-U+long-low-pitch` — `unknown_grouping`
- `Sebirwa-NC_2` — `other`
- `Zayse-Zergulla-x3` — `unknown_character`

## Sections

- All OK: **287 / 660** (43.5%)
- Some OK: **368 / 660** (55.8%)
- None OK: **5 / 660** (0.8%)
- Sections skipped: **0 / 660** (0.0%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 493 | `unknown_grouping` |
| 378 | `other` |
| 188 | `unknown_character` |
| 51 | `expected_underscore` |
| 32 | `expected_ipa` |
| 25 | `prose_or_expected_arrow` |
| 19 | `missing_slash_output_env` |
| 14 | `nested_brackets` |
| 11 | `syntax_other` |
| 10 | `unknown_feature` |
| 9 | `expected_number` |
| 9 | `empty_io_panic` |
| 4 | `stuff_after_word_bound` |
| 3 | `segments_before_word` |
| 2 | `panic_other` |
| 2 | `grouped_env_insertion` |
| 2 | `uneven_parallel_sets` |
| 2 | `multiple_underlines_env` |
| 1 | `incomplete_matrix` |
| 1 | `runtime_delete_only_segment` |
| 1 | `invalid_ipa` |

## Common Errors

### syntax_other (error_token)

| count | error_token |
|------:|-------------|
| 2 | `,` |
| 1 | `End Of Line` |
| 1 | `]` |
| 1 | `l` |
| 1 | `í` |
### syntax_other (description)

| count | description |
|------:|-------------|
| 1 | `Only a segment, matrix, group, or reference can be negated` |
| 1 | `Feature 'lost' has no modifier` |
| 1 | `Feature 'b' has no modifier` |
| 1 | `Feature 's' has no modifier` |
| 1 | `Feature 'truncated' has no modifier` |

### runtime_other (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### runtime_other (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### unknown_character (error_token)

| count | error_token |
|------:|-------------|
| 57 | `₂` |
| 45 | `₁` |
| 24 | `̣` |
| 17 | `Ḱ` |
| 16 | `₃` |
| 10 | `ː` |
| 4 | `ₙ` |
| 3 | `͡` |
| 2 | `ʝ` |
| 2 | `ₛ` |
### unknown_character (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### unknown_grouping (error_token)

| count | error_token |
|------:|-------------|
| 125 | `R` |
| 115 | `E` |
| 87 | `U` |
| 41 | `B` |
| 35 | `T` |
| 31 | `H` |
| 22 | `D` |
| 11 | `W` |
| 10 | `A` |
| 8 | `Z` |
### unknown_grouping (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### unknown_reference (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### unknown_reference (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### expected_underscore (error_token)

| count | error_token |
|------:|-------------|
| 11 | `,` |
| 2 | `/` |
| 2 | `ʷ` |
| 2 | `:` |
| 1 | `//` |
### expected_underscore (description)

| count | description |
|------:|-------------|
| 33 | `Expected '_', but received ''` |

### nested_brackets (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### nested_brackets (description)

| count | description |
|------:|-------------|
| 14 | `Cannot have nested brackets of the same type` |

### unknown_feature (error_token)

| count | error_token | suggested |
|------:|-------------|-----------|
| 3 | `initial` | `nasal` |
| 2 | `fricative` | `rhotic` |
| 1 | `posttonic` | `sonor` |
| 1 | `tonic` | `cons` |
| 1 | `glide` | `click` |
| 1 | `accent` | `cont` |
| 1 | `labiovelar` | `labiodental` |

### expected_number (error_token)

| count | error_token |
|------:|-------------|
| 4 | `d` |
| 2 | `r` |
| 1 | `ɡ` |
| 1 | `N` |
| 1 | `S` |
### expected_number (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### prose_or_expected_arrow (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### prose_or_expected_arrow (description)

| count | description |
|------:|-------------|
| 14 | `Expected '>', '->' or '=>', but received 'ʷ'` |
| 7 | `Expected '>', '->' or '=>', but received '̩'` |
| 2 | `Expected '>', '->' or '=>', but received '*'` |
| 1 | `Expected '>', '->' or '=>', but received '}'` |
| 1 | `Expected '>', '->' or '=>', but received '/'` |

### invalid_ipa (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### invalid_ipa (description)

| count | description |
|------:|-------------|
| 1 | `Could not get value of IPA 'k͡'.` |

### expected_ipa (error_token)

| count | error_token |
|------:|-------------|
| 8 | `(` |
| 4 | `ʷ` |
| 4 | `∅` |
| 3 | `*` |
| 3 | `{` |
| 3 | `…` |
| 2 | `ʲ` |
| 2 | `_` |
| 1 | `,` |
| 1 | `>` |
### expected_ipa (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### expected_range_dots (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### expected_range_dots (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### missing_slash_output_env (error_token)

| count | error_token |
|------:|-------------|
| 4 | `(` |
| 4 | `)` |
| 3 | `ʲ` |
| 3 | `ʷ` |
| 2 | `:` |
| 1 | `*` |
| 1 | `#` |
| 1 | `_` |
### missing_slash_output_env (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### floating_diacritic (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### floating_diacritic (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### multiple_underlines_env (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### multiple_underlines_env (description)

| count | description |
|------:|-------------|
| 2 | `Cannot have multiple underlines in an environment` |

### segments_before_word (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### segments_before_word (description)

| count | description |
|------:|-------------|
| 3 | `Cannot have segments before the beginning of a word` |

### stuff_after_word_bound (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### stuff_after_word_bound (description)

| count | description |
|------:|-------------|
| 4 | `Cannot have segments after the end of a word` |

### diacritic_prereq (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### diacritic_prereq (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### empty_io_panic (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### empty_io_panic (description)

| count | description |
|------:|-------------|
| 5 | `The input of an insertion rule must only contain `*` or `∅`` |
| 4 | `The output of a deletion rule must only contain `*` or `∅`` |

### incomplete_matrix (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### incomplete_matrix (description)

| count | description |
|------:|-------------|
| 1 | `An incomplete matrix cannot be inserted` |

### grouped_env_insertion (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### grouped_env_insertion (description)

| count | description |
|------:|-------------|
| 2 | `Grouped Environments cannot (yet) be used in insertion rules` |

### uneven_parallel_sets (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### uneven_parallel_sets (description)

| count | description |
|------:|-------------|
| 2 | `Two matched sets must have the same number of elements` |

### word_boundary_in_io (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### word_boundary_in_io (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

## Notes

- Inventory runs per index rule via `DiachronicSeries` + `validate_asca`.
- OK rows: [rule-inventory-success.csv](rule-inventory-success.csv)
- Fail rows: [rule-inventory-error.csv](rule-inventory-error.csv)
- Skipped rows: [rule-inventory-skipped.csv](rule-inventory-skipped.csv)
- `ok` flips (append-only): [rule-inventory-changelog.csv](rule-inventory-changelog.csv)
- Field blame OK rows: [field-isolation-success.csv](field-isolation-success.csv)
- Field blame fail rows: [field-isolation-error.csv](field-isolation-error.csv)
- Field blame skipped rows: [field-isolation-skipped.csv](field-isolation-skipped.csv)
- syntax_other: [syntax_other_errors.csv](syntax_other_errors.csv)
- runtime_other: [runtime_other_errors.csv](runtime_other_errors.csv)
- unknown_character: [unknown_character_errors.csv](unknown_character_errors.csv)
- unknown_grouping: [unknown_grouping_errors.csv](unknown_grouping_errors.csv)
- unknown_reference: [unknown_reference_errors.csv](unknown_reference_errors.csv)
- expected_underscore: [expected_underscore_errors.csv](expected_underscore_errors.csv)
- nested_brackets: [nested_brackets_errors.csv](nested_brackets_errors.csv)
- unknown_feature: [unknown_features_errors.csv](unknown_features_errors.csv)
- expected_number: [expected_number_errors.csv](expected_number_errors.csv)
- prose_or_expected_arrow: [prose_or_expected_arrow_errors.csv](prose_or_expected_arrow_errors.csv)
- invalid_ipa: [invalid_ipa_errors.csv](invalid_ipa_errors.csv)
- expected_ipa: [expected_ipa_errors.csv](expected_ipa_errors.csv)
- expected_range_dots: [expected_range_dots_errors.csv](expected_range_dots_errors.csv)
- missing_slash_output_env: [missing_slash_output_env_errors.csv](missing_slash_output_env_errors.csv)
- floating_diacritic: [floating_diacritic_errors.csv](floating_diacritic_errors.csv)
- multiple_underlines_env: [multiple_underlines_env_errors.csv](multiple_underlines_env_errors.csv)
- segments_before_word: [segments_before_word_errors.csv](segments_before_word_errors.csv)
- stuff_after_word_bound: [stuff_after_word_bound_errors.csv](stuff_after_word_bound_errors.csv)
- diacritic_prereq: [diacritic_prereq_errors.csv](diacritic_prereq_errors.csv)
- empty_io_panic: [empty_io_panic_errors.csv](empty_io_panic_errors.csv)
- incomplete_matrix: [incomplete_matrix_errors.csv](incomplete_matrix_errors.csv)
- grouped_env_insertion: [grouped_env_insertion_errors.csv](grouped_env_insertion_errors.csv)
- uneven_parallel_sets: [uneven_parallel_sets_errors.csv](uneven_parallel_sets_errors.csv)
- word_boundary_in_io: [word_boundary_in_io_errors.csv](word_boundary_in_io_errors.csv)
