# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9201** (one per corpus rule)
- OK: **7462** (81.1%)
- Fail: **1739** (18.9%)
- Sections all OK: **248 / 714** (34.7%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 553 | `syntax_other` |
| 313 | `unknown_character` |
| 285 | `expected_underscore` |
| 118 | `runtime_other` |
| 104 | `unknown_grouping` |
| 91 | `unknown_feature` |
| 80 | `prose_or_expected_arrow` |
| 45 | `nested_brackets` |
| 42 | `panic_other` |
| 37 | `expected_number` |
| 30 | `diacritic_prereq` |
| 21 | `runtime_delete_only_segment` |
| 14 | `stuff_after_word_bound` |
| 3 | `malformed_comment` |
| 2 | `other` |
| 1 | `missing_arrow` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 45 | `ı` |
| 42 | `ː` |
| 37 | `́` |
| 27 | `ṽ` |
| 20 | `̣` |

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
| 18 | `R` |
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
