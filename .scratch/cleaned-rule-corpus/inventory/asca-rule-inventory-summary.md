# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9638** (one per corpus rule)
- OK: **7956** (82.5%)
- Fail: **1682** (17.5%)
- Sections all OK: **263 / 714** (36.8%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 505 | `syntax_other` |
| 317 | `unknown_character` |
| 297 | `expected_underscore` |
| 121 | `runtime_other` |
| 109 | `unknown_grouping` |
| 91 | `unknown_feature` |
| 82 | `prose_or_expected_arrow` |
| 46 | `nested_brackets` |
| 37 | `expected_number` |
| 32 | `diacritic_prereq` |
| 21 | `runtime_delete_only_segment` |
| 14 | `stuff_after_word_bound` |
| 4 | `panic_other` |
| 3 | `malformed_comment` |
| 2 | `other` |
| 1 | `missing_arrow` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 46 | `ı` |
| 42 | `ː` |
| 37 | `́` |
| 27 | `ṽ` |
| 22 | `̣` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 22 | `open` | `ten` |
| 10 | `samePOA` | `lateral` |
| 10 | `closed` | `cons` |
| 9 | `fortis` | `contin` |
| 8 | `mid` | `man` |
| 6 | `lenis` | `tens` |
| 5 | `weak` | `man` |
| 3 | `palatalized` | `latrl` |
| 2 | `affricate` | `stridnt` |
| 2 | `fallingtone` | `length` |
| 2 | `fricative` | `rhotic` |
| 1 | `ejective` | `contin` |
| 1 | `APOA` | `root` |
| 1 | `lowpitch` | `voice` |
| 1 | `highpitch` | `high` |
| 1 | `aspirated` | `spread` |
| 1 | `intertonic` | `anterior` |
| 1 | `tonic` | `cons` |
| 1 | `alveolopalatal` | `consonantal` |
| 1 | `glide` | `click` |
| 1 | `TR` | `rt` |
| 1 | `creakyvoice` | `voice` |
| 1 | `labiovelar` | `labiodental` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 23 | `R` |
| 15 | `U` |
| 14 | `E` |
| 10 | `B` |
| 9 | `K` |
| 7 | `T` |
| 7 | `M` |
| 6 | `X` |
| 5 | `H` |
| 3 | `I` |
| 3 | `D` |
| 3 | `Y` |
| 2 | `A` |
| 1 | `W` |
| 1 | `Q` |

## Notes

- Inventory runs per corpus rule via `DiachronicSeries` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
- OK rows: [asca-rule-inventory-success.csv](asca-rule-inventory-success.csv)
- Fail rows: [asca-rule-inventory-error.csv](asca-rule-inventory-error.csv)
- `ok` flips (append-only): [asca-rule-inventory-changelog.csv](asca-rule-inventory-changelog.csv)
