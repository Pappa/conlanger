# Cleaned rule index — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9840** (one per index rule)

## Rules
- OK: **8358** (84.9%)
- Fail: **870** (8.8%)
- Skipped: **612** (6.2%)

## Sections

- All OK: **408 / 714** (57.1%)
- Some OK: **277 / 714** (38.8%)
- None OK: **4 / 714** (0.6%)
- Sections skipped: **25 / 714** (3.5%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 309 | `syntax_other` |
| 139 | `runtime_other` |
| 123 | `unknown_character` |
| 114 | `expected_underscore` |
| 35 | `expected_number` |
| 33 | `prose_or_expected_arrow` |
| 32 | `diacritic_prereq` |
| 28 | `nested_brackets` |
| 23 | `unknown_feature` |
| 14 | `stuff_after_word_bound` |
| 11 | `unknown_grouping` |
| 3 | `panic_other` |
| 2 | `format_error` |
| 2 | `runtime_delete_only_segment` |
| 2 | `other` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 22 | `̣` |
| 13 | `₂` |
| 11 | `̊` |
| 6 | `ŕ` |
| 6 | `̺` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 5 | `weak` | `man` |
| 3 | `initial` | `nasal` |
| 3 | `palatalized` | `latrl` |
| 2 | `fricative` | `rhotic` |
| 1 | `highpitch` | `high` |
| 1 | `lowpitch` | `voice` |
| 1 | `posttonic` | `sonor` |
| 1 | `ejective` | `contin` |
| 1 | `alveolopalatal` | `consonantal` |
| 1 | `intertonic` | `anterior` |
| 1 | `tonic` | `cons` |
| 1 | `glide` | `click` |
| 1 | `accent` | `cont` |
| 1 | `labiovelar` | `labiodental` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 6 | `M` |
| 3 | `Y` |
| 1 | `I` |
| 1 | `X` |

## Notes

- Inventory runs per index rule via `DiachronicSeries` + `validate_asca`.
- OK rows: [asca-rule-inventory-success.csv](asca-rule-inventory-success.csv)
- Fail rows: [asca-rule-inventory-error.csv](asca-rule-inventory-error.csv)
- `ok` flips (append-only): [asca-rule-inventory-changelog.csv](asca-rule-inventory-changelog.csv)
- Field blame OK rows: [asca-field-isolation-success.csv](asca-field-isolation-success.csv)
- Field blame fail rows: [asca-field-isolation-error.csv](asca-field-isolation-error.csv)
- Grouping errors: [grouping_errors.csv](grouping_errors.csv)
- Character errors: [character_errors.csv](character_errors.csv)
- Underscore errors: [underscore_errors.csv](underscore_errors.csv)
- Nested-bracket errors: [nested_brackets_errors.csv](nested_brackets_errors.csv)
- Unknown features: [unknown_features.csv](unknown_features.csv)
