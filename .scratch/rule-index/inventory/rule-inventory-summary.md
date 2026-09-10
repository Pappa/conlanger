# Cleaned rule index — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.3**
- Rows: **9877** (one per inventory row; optional-output alternatives emit extra rows with distinct `alt_idx`)

## Rules
- OK: **8881** (89.9%)
- Fail: **656** (6.6%)
- Skipped: **340** (3.4%)

## Sections

- All OK: **451 / 714** (63.2%)
- Some OK: **239 / 714** (33.5%)
- None OK: **3 / 714** (0.4%)
- Sections skipped: **21 / 714** (2.9%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 152 | `expected_underscore` |
| 137 | `unknown_character` |
| 52 | `syntax_other` |
| 51 | `expected_ipa` |
| 47 | `invalid_ipa` |
| 46 | `missing_slash_output_env` |
| 41 | `prose_or_expected_arrow` |
| 22 | `unknown_feature` |
| 17 | `nested_brackets` |
| 15 | `unknown_grouping` |
| 14 | `stuff_after_word_bound` |
| 12 | `expected_number` |
| 11 | `empty_io_panic` |
| 9 | `diacritic_prereq` |
| 8 | `segments_before_word` |
| 7 | `multiple_underlines_env` |
| 4 | `panic_other` |
| 2 | `grouped_env_insertion` |
| 2 | `uneven_parallel_sets` |
| 2 | `format_error` |
| 2 | `runtime_delete_only_segment` |
| 2 | `other` |
| 1 | `incomplete_matrix` |

## Common Errors

### syntax_other (error_token)

| count | error_token |
|------:|-------------|
| 6 | `E` |
| 2 | `,` |
| 1 | `{` |
| 1 | `End Of Line` |
| 1 | `α` |
| 1 | `]` |
| 1 | `:` |
| 1 | `l` |
| 1 | `í` |
### syntax_other (description)

| count | description |
|------:|-------------|
| 18 | `Negation cannot be used in the output` |
| 10 | `Output cannot be empty. Use `*` or '∅' to indicate deletion` |
| 2 | `Tones cannot be ±; they can only be used with numeric values.` |
| 1 | `/ cannot be placed inside a matrix. An element inside `[]` must a distinctive feature` |
| 1 | `Only a segment, matrix, group, or reference can be negated` |
| 1 | `Feature 'lost' has no modifier` |
| 1 | `Feature 'b' has no modifier` |
| 1 | `Feature 's' has no modifier` |
| 1 | `Feature 'long' has no modifier` |
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
| 22 | `+` |
| 22 | `̣` |
| 13 | `₂` |
| 8 | `̊` |
| 7 | `ː` |
| 6 | `͜` |
| 6 | `̺` |
| 6 | `ŕ` |
| 5 | `ₙ` |
| 4 | `̂` |
### unknown_character (description)

| count | description |
|------:|-------------|
| — | _(none)_ |

### unknown_grouping (error_token)

| count | error_token |
|------:|-------------|
| 6 | `M` |
| 4 | `B` |
| 3 | `Y` |
| 1 | `I` |
| 1 | `X` |
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
| 22 | `,` |
| 7 | `/` |
| 6 | `//` |
| 3 | `)` |
| 3 | `:` |
| 1 | `*` |
### expected_underscore (description)

| count | description |
|------:|-------------|
| 110 | `Expected '_', but received ''` |

### nested_brackets (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### nested_brackets (description)

| count | description |
|------:|-------------|
| 17 | `Cannot have nested brackets of the same type` |

### unknown_feature (error_token)

| count | error_token | suggested |
|------:|-------------|-----------|
| 5 | `weak` | `man` |
| 3 | `initial` | `nasal` |
| 3 | `palatalized` | `latrl` |
| 2 | `fricative` | `rhotic` |
| 1 | `highpitch` | `high` |
| 1 | `posttonic` | `sonor` |
| 1 | `lowpitch` | `voice` |
| 1 | `alveolopalatal` | `consonantal` |
| 1 | `intertonic` | `anterior` |
| 1 | `tonic` | `cons` |

### expected_number (error_token)

| count | error_token |
|------:|-------------|
| 4 | `d` |
| 2 | `r` |
| 1 | `l` |
| 1 | `ɡ` |
| 1 | `N` |
| 1 | `P` |
| 1 | `s` |
| 1 | `ʔ` |
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
| 20 | `Expected '>', '->' or '=>', but received 'ˀ'` |
| 7 | `Expected '>', '->' or '=>', but received '̩'` |
| 5 | `Expected '>', '->' or '=>', but received ':'` |
| 3 | `Expected '>', '->' or '=>', but received '*'` |
| 2 | `Expected '>', '->' or '=>', but received '̥'` |
| 1 | `Expected '>', '->' or '=>', but received 'ʱ'` |
| 1 | `Expected '>', '->' or '=>', but received '}'` |
| 1 | `Expected '>', '->' or '=>', but received 'ʷ'` |
| 1 | `Expected '>', '->' or '=>', but received '/'` |

### invalid_ipa (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### invalid_ipa (description)

| count | description |
|------:|-------------|
| 25 | `Could not get value of IPA 'ǃ'.` |
| 11 | `Could not get value of IPA 'ǀ'.` |
| 6 | `Could not get value of IPA 'ǁ'.` |
| 5 | `Could not get value of IPA 'ǂ'.` |

### expected_ipa (error_token)

| count | error_token |
|------:|-------------|
| 9 | `(` |
| 6 | `{` |
| 6 | `:` |
| 6 | `∅` |
| 5 | `>` |
| 3 | `*` |
| 3 | `ʷ` |
| 3 | `…` |
| 2 | `ʲ` |
| 2 | `_` |
### expected_ipa (description)

| count | description |
|------:|-------------|
| 1 | `Expected an IPA character, Primative or Matrix, but received ''` |

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
| 21 | `)` |
| 11 | `:` |
| 4 | `(` |
| 3 | `ʲ` |
| 2 | `_` |
| 1 | `&` |
| 1 | `*` |
| 1 | `#` |
| 1 | `ˀ` |
| 1 | `̥` |
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
| 7 | `Cannot have multiple underlines in an environment` |

### segments_before_word (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### segments_before_word (description)

| count | description |
|------:|-------------|
| 8 | `Cannot have segments before the beginning of a word` |

### stuff_after_word_bound (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### stuff_after_word_bound (description)

| count | description |
|------:|-------------|
| 14 | `Cannot have segments after the end of a word` |

### diacritic_prereq (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### diacritic_prereq (description)

| count | description |
|------:|-------------|
| 9 | `Segment does not have prerequisite properties to have this diacritic. Must be [-sonorant]` |

### empty_io_panic (error_token)

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### empty_io_panic (description)

| count | description |
|------:|-------------|
| 8 | `The output of a deletion rule must only contain `*` or `∅`` |
| 3 | `The input of an insertion rule must only contain `*` or `∅`` |

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


## Field isolation blame (error rows)

| count | blame |
|------:|-------|
| 260 | `env` |
| 204 | `input` |
| 177 | `output` |
| 61 | `exception` |
| 49 | `multi` |

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
