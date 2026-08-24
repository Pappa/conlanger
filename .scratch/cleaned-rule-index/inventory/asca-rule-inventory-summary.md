# Cleaned rule index — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9686** (one per index rule)
- OK: **8273** (85.4%)
- Fail: **1304** (13.5%)
- Skipped: **109** (1.1%)
- Sections all OK: **339 / 708** (47.9%)
- Sections skipped: **6 / 714** (0.8%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 392 | `syntax_other` |
| 256 | `expected_underscore` |
| 170 | `unknown_character` |
| 130 | `runtime_other` |
| 114 | `unknown_grouping` |
| 55 | `prose_or_expected_arrow` |
| 43 | `nested_brackets` |
| 38 | `expected_number` |
| 32 | `diacritic_prereq` |
| 31 | `unknown_feature` |
| 21 | `runtime_delete_only_segment` |
| 14 | `stuff_after_word_bound` |
| 4 | `panic_other` |
| 2 | `format_error` |
| 2 | `other` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 37 | `́` |
| 22 | `̣` |
| 13 | `₂` |
| 12 | `̊` |
| 9 | `ː` |

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
| 28 | `R` |
| 15 | `U` |
| 13 | `E` |
| 10 | `B` |
| 9 | `X` |
| 7 | `K` |
| 7 | `M` |
| 7 | `T` |
| 5 | `H` |
| 4 | `D` |
| 3 | `Y` |
| 2 | `I` |
| 2 | `A` |
| 1 | `W` |
| 1 | `Q` |

## Notes

- Inventory runs per index rule via `DiachronicSeries` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
- OK rows: [asca-rule-inventory-success.csv](asca-rule-inventory-success.csv)
- Fail rows: [asca-rule-inventory-error.csv](asca-rule-inventory-error.csv)
- `ok` flips (append-only): [asca-rule-inventory-changelog.csv](asca-rule-inventory-changelog.csv)
- Field blame (fails-only default): [asca-field-isolation.csv](asca-field-isolation.csv)
- Field blame OK rows: [asca-field-isolation-success.csv](asca-field-isolation-success.csv)
- Field blame fail rows: [asca-field-isolation-error.csv](asca-field-isolation-error.csv)
