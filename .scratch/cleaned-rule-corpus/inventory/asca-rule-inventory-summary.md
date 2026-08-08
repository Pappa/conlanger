# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9201** (one per corpus rule)
- OK: **7134** (77.5%)
- Fail: **2067** (22.5%)
- Sections all OK: **204 / 714** (28.6%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 637 | `syntax_other` |
| 414 | `expected_underscore` |
| 383 | `unknown_character` |
| 162 | `unknown_feature` |
| 116 | `runtime_other` |
| 100 | `unknown_grouping` |
| 67 | `prose_or_expected_arrow` |
| 41 | `nested_brackets` |
| 41 | `panic_other` |
| 37 | `expected_number` |
| 30 | `diacritic_prereq` |
| 21 | `runtime_delete_only_segment` |
| 14 | `stuff_after_word_bound` |
| 2 | `malformed_comment` |
| 2 | `other` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 49 | `ː` |
| 45 | `ı` |
| 42 | `”` |
| 37 | `́` |
| 27 | `ṽ` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 22 | `dental` | `ldental` |
| 18 | `open` | `ten` |
| 13 | `palatal` | `latrl` |
| 11 | `lowtone` | `contin` |
| 10 | `samePOA` | `lateral` |
| 9 | `fortis` | `contin` |
| 9 | `closed` | `cons` |
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
| 15 | `R` |
| 14 | `U` |
| 14 | `E` |
| 9 | `K` |
| 7 | `B` |
| 7 | `T` |
| 7 | `M` |
| 6 | `X` |
| 5 | `H` |
| 4 | `D` |
| 3 | `I` |
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
