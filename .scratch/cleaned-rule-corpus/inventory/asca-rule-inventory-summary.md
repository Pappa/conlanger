# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9201** (one per corpus rule)
- OK: **7218** (78.4%)
- Fail: **1983** (21.6%)
- Sections all OK: **216 / 714** (30.3%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 616 | `syntax_other` |
| 416 | `expected_underscore` |
| 324 | `unknown_character` |
| 168 | `unknown_feature` |
| 117 | `runtime_other` |
| 101 | `unknown_grouping` |
| 49 | `prose_or_expected_arrow` |
| 43 | `nested_brackets` |
| 41 | `panic_other` |
| 37 | `expected_number` |
| 30 | `diacritic_prereq` |
| 21 | `runtime_delete_only_segment` |
| 14 | `stuff_after_word_bound` |
| 2 | `missing_arrow` |
| 2 | `malformed_comment` |
| 2 | `other` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 47 | `ː` |
| 45 | `ı` |
| 37 | `́` |
| 27 | `ṽ` |
| 19 | `̣` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 23 | `dental` | `ldental` |
| 22 | `open` | `ten` |
| 13 | `palatal` | `latrl` |
| 11 | `lowtone` | `contin` |
| 10 | `samePOA` | `lateral` |
| 10 | `closed` | `cons` |
| 9 | `fortis` | `contin` |
| 8 | `hightone` | `high` |
| 8 | `mid` | `man` |
| 6 | `lenis` | `tens` |
| 5 | `alveolar` | `delay` |
| 5 | `weak` | `man` |
| 5 | `velar` | `delay` |
| 5 | `guttural` | `lateral` |
| 4 | `uvular` | `lar` |
| 3 | `fallingtone` | `length` |
| 2 | `lowfallingtone` | `continuant` |
| 2 | `fricative` | `rhotic` |
| 2 | `affricate` | `stridnt` |
| 2 | `highrisingtone` | `strident` |
| 1 | `intertonic` | `anterior` |
| 1 | `highpitch` | `high` |
| 1 | `ejective` | `contin` |
| 1 | `lowpitch` | `voice` |
| 1 | `APOA` | `root` |
| 1 | `glide` | `click` |
| 1 | `tonic` | `cons` |
| 1 | `palatalized` | `latrl` |
| 1 | `alveolopalatal` | `consonantal` |
| 1 | `aspirated` | `spread` |
| 1 | `TR` | `rt` |
| 1 | `creakyvoice` | `voice` |
| 1 | `labiovelar` | `labiodental` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 16 | `R` |
| 14 | `U` |
| 14 | `E` |
| 9 | `K` |
| 8 | `M` |
| 7 | `T` |
| 7 | `B` |
| 6 | `X` |
| 5 | `H` |
| 3 | `I` |
| 3 | `D` |
| 3 | `Y` |
| 2 | `W` |
| 2 | `Q` |
| 2 | `A` |

## Notes

- Inventory runs per corpus rule via `SoundChangeRuleSet` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
- OK rows: [asca-rule-inventory-success.csv](asca-rule-inventory-success.csv)
- Fail rows: [asca-rule-inventory-error.csv](asca-rule-inventory-error.csv)
- `ok` flips (append-only): [asca-rule-inventory-changelog.csv](asca-rule-inventory-changelog.csv)
