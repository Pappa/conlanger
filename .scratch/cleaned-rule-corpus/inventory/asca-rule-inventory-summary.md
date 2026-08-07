# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9201** (one per corpus rule)
- OK: **6578** (71.5%)
- Fail: **2623** (28.5%)
- Sections all OK: **145 / 714** (20.3%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 1082 | `syntax_other` |
| 648 | `unknown_character` |
| 386 | `expected_underscore` |
| 162 | `unknown_feature` |
| 86 | `unknown_grouping` |
| 55 | `prose_or_expected_arrow` |
| 34 | `expected_number` |
| 34 | `panic_other` |
| 32 | `nested_brackets` |
| 29 | `diacritic_prereq` |
| 22 | `runtime_other` |
| 20 | `runtime_delete_only_segment` |
| 18 | `stuff_after_word_bound` |
| 13 | `malformed_comment` |
| 2 | `other` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 49 | `ː` |
| 48 | `Š` |
| 42 | `”` |
| 35 | `(` |
| 34 | `ã` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 19 | `dental` | `ldental` |
| 14 | `open` | `ten` |
| 13 | `palatal` | `latrl` |
| 11 | `lowtone` | `contin` |
| 9 | `glottalized` | `contin` |
| 9 | `samePOA` | `lateral` |
| 9 | `fortis` | `contin` |
| 8 | `hightone` | `high` |
| 8 | `mid` | `man` |
| 6 | `lenis` | `tens` |
| 5 | `alveolar` | `delay` |
| 5 | `weak` | `man` |
| 5 | `guttural` | `lateral` |
| 5 | `velar` | `delay` |
| 4 | `closed` | `cons` |
| 4 | `uvular` | `lar` |
| 4 | `glottal` | `lateral` |
| 3 | `fallingtone` | `length` |
| 2 | `affricate` | `stridnt` |
| 2 | `fricative` | `rhotic` |
| 2 | `lowfallingtone` | `continuant` |
| 2 | `highrisingtone` | `strident` |
| 1 | `intertonic` | `anterior` |
| 1 | `highpitch` | `high` |
| 1 | `lowpitch` | `voice` |
| 1 | `APOA` | `root` |
| 1 | `close` | `cons` |
| 1 | `glide` | `click` |
| 1 | `palatalized` | `latrl` |
| 1 | `alveolopalatal` | `consonantal` |
| 1 | `tonic` | `cons` |
| 1 | `aspirated` | `spread` |
| 1 | `TR` | `rt` |
| 1 | `creakyvoice` | `voice` |
| 1 | `labiovelar` | `labiodental` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 15 | `R` |
| 14 | `U` |
| 12 | `E` |
| 7 | `H` |
| 6 | `B` |
| 6 | `M` |
| 5 | `K` |
| 5 | `T` |
| 3 | `D` |
| 3 | `Y` |
| 3 | `X` |
| 2 | `A` |
| 2 | `Q` |
| 2 | `I` |
| 1 | `W` |

## Notes

- Inventory runs per corpus rule via `SoundChangeRuleSet` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
- OK rows: [asca-rule-inventory-success.csv](asca-rule-inventory-success.csv)
- Fail rows: [asca-rule-inventory-error.csv](asca-rule-inventory-error.csv)
- `ok` flips (append-only): [asca-rule-inventory-changelog.csv](asca-rule-inventory-changelog.csv)
