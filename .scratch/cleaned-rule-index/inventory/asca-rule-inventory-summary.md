# Cleaned rule index — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9841** (one per index rule)

## Rules
- OK: **8400** (85.4%)
- Fail: **829** (8.4%)
- Skipped: **612** (6.2%)

## Sections

- All OK: **417 / 714** (58.4%)
- Some OK: **268 / 714** (37.5%)
- None OK: **4 / 714** (0.6%)
- Sections skipped: **25 / 714** (3.5%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 251 | `syntax_other` |
| 126 | `unknown_character` |
| 123 | `runtime_other` |
| 116 | `expected_underscore` |
| 58 | `invalid_ipa` |
| 36 | `expected_number` |
| 33 | `prose_or_expected_arrow` |
| 23 | `unknown_feature` |
| 20 | `nested_brackets` |
| 14 | `stuff_after_word_bound` |
| 11 | `unknown_grouping` |
| 9 | `diacritic_prereq` |
| 3 | `panic_other` |
| 2 | `format_error` |
| 2 | `runtime_delete_only_segment` |
| 2 | `other` |

## Common Errors

### syntax_other

| count | error_token |
|------:|-------------|
| 19 | `)` |
| 18 | `ʷ` |
| 15 | `(` |
| 12 | ` ` |
| 10 | `:` |
| 9 | `''` |
| 8 | `/` |
| 6 | `∅` |
| 6 | `>` |
| 6 | `ʼ` |
### syntax_other

| count | description |
|------:|-------------|
| 14 | `Floating diacritic. Diacritics can only be used to modify IPA Segments` |
| 8 | `Cannot have segments before the beginning of a word` |
| 8 | `The output of a deletion rule must only contain `*` or `∅`` |
| 8 | `Cannot have multiple underlines in an environment` |
| 6 | `Expected an IPA character, Primative or Matrix, but received '//'` |
| 6 | `Feature 'anything' has no modifier` |
| 4 | `Output cannot be empty. Use `*` or '∅' to indicate deletion` |
| 3 | `Options can only be used in Environments or Structures` |
| 3 | `The input of an insertion rule must only contain `*` or `∅`` |
| 3 | `Feature 'alveolar' has no modifier` |

### runtime_other

| count | error_token |
|------:|-------------|
| 75 | `3` |
| 32 | `1` |
### runtime_other

| count | description |
|------:|-------------|
| 11 | `An incomplete matrix cannot be inserted` |
| 2 | `Grouped Environments cannot (yet) be used in insertion rules` |
| 2 | `Two matched sets must have the same number of elements` |
| 1 | `Word Boundaries cannot be in the input or output` |

### unknown_character

| count | error_token |
|------:|-------------|
| 22 | `̣` |
| 13 | `₂` |
| 11 | `̊` |
| 8 | `ː` |
| 6 | `ŕ` |
| 6 | `̺` |
| 5 | `͜` |
| 5 | `ₙ` |
| 4 | `̻` |
| 4 | `̂` |
### unknown_character

| count | description |
|------:|-------------|
| — | _(none)_ |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 6 | `M` |
| 3 | `Y` |
| 1 | `I` |
| 1 | `X` |
### unknown_grouping

| count | description |
|------:|-------------|
| — | _(none)_ |

### expected_underscore

| count | error_token |
|------:|-------------|
| 73 | `''` |
| 17 | `,` |
| 17 | `/` |
| 2 | `*` |
| 2 | `ʷ` |
| 1 | `:` |
### expected_underscore

| count | description |
|------:|-------------|
| 4 | `Expected '_', but received '//'` |

### nested_brackets

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### nested_brackets

| count | description |
|------:|-------------|
| 20 | `Cannot have nested brackets of the same type` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 5 | `weak` | man |
| 3 | `initial` | nasal |
| 3 | `palatalized` | latrl |
| 2 | `fricative` | rhotic |
| 1 | `alveolopalatal` | consonantal |
| 1 | `accent` | cont |
| 1 | `highpitch` | high |
| 1 | `glide` | click |
| 1 | `ejective` | contin |
| 1 | `intertonic` | anterior |

### expected_number

| count | error_token |
|------:|-------------|
| — | _(none)_ |
### expected_number

| count | description |
|------:|-------------|
| — | _(none)_ |

### prose_or_expected_arrow

| count | error_token |
|------:|-------------|
| 21 | `ˀ` |
| 2 | `*` |
| 2 | `/` |
| 2 | `̥` |
| 2 | `)` |
| 1 | `ʱ` |
| 1 | `:` |
| 1 | `}` |
| 1 | `ʷ` |
### prose_or_expected_arrow

| count | description |
|------:|-------------|
| — | _(none)_ |


## Field isolation blame (error rows)

| count | blame |
|------:|-------|
| 268 | `env` |
| 220 | `input` |
| 183 | `output` |
| 172 | `multi` |
| 82 | `exception` |

## Notes

- Inventory runs per index rule via `DiachronicSeries` + `validate_asca`.
- OK rows: [asca-rule-inventory-success.csv](asca-rule-inventory-success.csv)
- Fail rows: [asca-rule-inventory-error.csv](asca-rule-inventory-error.csv)
- `ok` flips (append-only): [asca-rule-inventory-changelog.csv](asca-rule-inventory-changelog.csv)
- Field blame OK rows: [asca-field-isolation-success.csv](asca-field-isolation-success.csv)
- Field blame fail rows: [asca-field-isolation-error.csv](asca-field-isolation-error.csv)
- syntax_other: [syntax_other_errors.csv](syntax_other_errors.csv)
- runtime_other: [runtime_other_errors.csv](runtime_other_errors.csv)
- unknown_character: [unknown_character_errors.csv](unknown_character_errors.csv)
- unknown_grouping: [unknown_grouping_errors.csv](unknown_grouping_errors.csv)
- expected_underscore: [expected_underscore_errors.csv](expected_underscore_errors.csv)
- nested_brackets: [nested_brackets_errors.csv](nested_brackets_errors.csv)
- unknown_feature: [unknown_features_errors.csv](unknown_features_errors.csv)
- expected_number: [expected_number_errors.csv](expected_number_errors.csv)
- prose_or_expected_arrow: [prose_or_expected_arrow_errors.csv](prose_or_expected_arrow_errors.csv)
