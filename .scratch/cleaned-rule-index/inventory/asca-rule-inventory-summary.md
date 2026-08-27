# Cleaned rule index — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9676** (one per index rule)
- OK: **8059** (83.3%)
- Fail: **1088** (11.2%)
- Skipped: **529** (5.5%)
- Sections all OK: **351 / 691** (50.8%)
- Sections skipped: **23 / 714** (3.2%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 381 | `syntax_other` |
| 211 | `expected_underscore` |
| 134 | `runtime_other` |
| 131 | `unknown_character` |
| 47 | `prose_or_expected_arrow` |
| 39 | `nested_brackets` |
| 38 | `expected_number` |
| 32 | `diacritic_prereq` |
| 31 | `unknown_feature` |
| 21 | `unknown_grouping` |
| 14 | `stuff_after_word_bound` |
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
| 10 | `ː` |
| 6 | `̺` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 8 | `samePOA` | `lateral` |
| 5 | `weak` | `man` |
| 3 | `initial` | `nasal` |
| 3 | `palatalized` | `latrl` |
| 2 | `fricative` | `rhotic` |
| 1 | `lowpitch` | `voice` |
| 1 | `highpitch` | `high` |
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
| 9 | `X` |
| 6 | `M` |
| 3 | `I` |
| 3 | `Y` |

## Notes

- Inventory runs per index rule via `DiachronicSeries` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
- OK rows: [asca-rule-inventory-success.csv](asca-rule-inventory-success.csv)
- Fail rows: [asca-rule-inventory-error.csv](asca-rule-inventory-error.csv)
- `ok` flips (append-only): [asca-rule-inventory-changelog.csv](asca-rule-inventory-changelog.csv)
- Field blame (fails-only default): [asca-field-isolation.csv](asca-field-isolation.csv)
- Field blame OK rows: [asca-field-isolation-success.csv](asca-field-isolation-success.csv)
- Field blame fail rows: [asca-field-isolation-error.csv](asca-field-isolation-error.csv)
