# Cleaned rule index — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9688** (one per index rule)
- OK: **8299** (85.7%)
- Fail: **1329** (13.7%)
- Skipped: **60** (0.6%)
- Sections all OK: **338 / 711** (47.5%)
- Sections skipped: **3 / 714** (0.4%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 391 | `syntax_other` |
| 259 | `expected_underscore` |
| 172 | `unknown_character` |
| 131 | `runtime_other` |
| 115 | `unknown_grouping` |
| 56 | `prose_or_expected_arrow` |
| 48 | `unknown_feature` |
| 43 | `nested_brackets` |
| 38 | `expected_number` |
| 32 | `diacritic_prereq` |
| 22 | `runtime_delete_only_segment` |
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
| 14 | `₂` |
| 12 | `̊` |
| 9 | `ː` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 9 | `fortis` | `contin` |
| 8 | `samePOA` | `lateral` |
| 6 | `lenis` | `tens` |
| 5 | `weak` | `man` |
| 3 | `initial` | `nasal` |
| 3 | `palatalized` | `latrl` |
| 2 | `fricative` | `rhotic` |
| 1 | `lowpitch` | `voice` |
| 1 | `highpitch` | `high` |
| 1 | `APOA` | `root` |
| 1 | `ejective` | `contin` |
| 1 | `intertonic` | `anterior` |
| 1 | `posttonic` | `sonor` |
| 1 | `alveolopalatal` | `consonantal` |
| 1 | `tonic` | `cons` |
| 1 | `glide` | `click` |
| 1 | `TR` | `rt` |
| 1 | `accent` | `cont` |
| 1 | `labiovelar` | `labiodental` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 28 | `R` |
| 15 | `U` |
| 14 | `E` |
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
