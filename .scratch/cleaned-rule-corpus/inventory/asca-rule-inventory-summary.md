# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9688** (one per corpus rule)
- OK: **8253** (85.2%)
- Fail: **1375** (14.2%)
- Skipped: **60** (0.6%)
- Sections all OK: **328 / 711** (46.1%)
- Sections skipped: **3 / 714** (0.4%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 411 | `syntax_other` |
| 234 | `expected_underscore` |
| 186 | `unknown_character` |
| 130 | `runtime_other` |
| 111 | `unknown_grouping` |
| 88 | `unknown_feature` |
| 56 | `prose_or_expected_arrow` |
| 45 | `nested_brackets` |
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
| 23 | `ː` |
| 22 | `̣` |
| 14 | `₂` |
| 12 | `̊` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 22 | `open` | `ten` |
| 10 | `closed` | `cons` |
| 10 | `samePOA` | `lateral` |
| 9 | `fortis` | `contin` |
| 8 | `mid` | `man` |
| 6 | `lenis` | `tens` |
| 5 | `weak` | `man` |
| 3 | `palatalized` | `latrl` |
| 2 | `fricative` | `rhotic` |
| 1 | `highpitch` | `high` |
| 1 | `APOA` | `root` |
| 1 | `lowpitch` | `voice` |
| 1 | `intertonic` | `anterior` |
| 1 | `ejective` | `contin` |
| 1 | `aspirated` | `spread` |
| 1 | `alveolopalatal` | `consonantal` |
| 1 | `tonic` | `cons` |
| 1 | `glide` | `click` |
| 1 | `TR` | `rt` |
| 1 | `accent` | `cont` |
| 1 | `creakyvoice` | `voice` |
| 1 | `labiovelar` | `labiodental` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 28 | `R` |
| 15 | `U` |
| 14 | `E` |
| 10 | `B` |
| 7 | `M` |
| 7 | `T` |
| 7 | `K` |
| 6 | `X` |
| 5 | `H` |
| 3 | `Y` |
| 3 | `D` |
| 2 | `I` |
| 2 | `A` |
| 1 | `W` |
| 1 | `Q` |


## Field isolation blame (error rows)

| count | blame |
|------:|-------|
| 546 | `input` |
| 509 | `env` |
| 416 | `output` |
| 213 | `multi` |
| 130 | `exception` |

## Notes

- Inventory runs per corpus rule via `DiachronicSeries` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
- OK rows: [asca-rule-inventory-success.csv](asca-rule-inventory-success.csv)
- Fail rows: [asca-rule-inventory-error.csv](asca-rule-inventory-error.csv)
- `ok` flips (append-only): [asca-rule-inventory-changelog.csv](asca-rule-inventory-changelog.csv)
- Field blame (fails-only default): [asca-field-isolation.csv](asca-field-isolation.csv)
- Field blame OK rows: [asca-field-isolation-success.csv](asca-field-isolation-success.csv)
- Field blame fail rows: [asca-field-isolation-error.csv](asca-field-isolation-error.csv)
