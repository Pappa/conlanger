# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9317** (one per corpus rule)
- OK: **6422** (68.9%)
- Fail: **2895** (31.1%)
- Sections all OK: **130 / 714** (18.2%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 1192 | `syntax_other` |
| 758 | `unknown_character` |
| 370 | `expected_underscore` |
| 251 | `unknown_feature` |
| 79 | `unknown_grouping` |
| 56 | `prose_or_expected_arrow` |
| 33 | `panic_other` |
| 31 | `expected_number` |
| 30 | `nested_brackets` |
| 26 | `diacritic_prereq` |
| 20 | `runtime_delete_only_segment` |
| 18 | `runtime_other` |
| 17 | `stuff_after_word_bound` |
| 12 | `malformed_comment` |
| 2 | `other` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 51 | `₁` |
| 49 | `₀` |
| 48 | `Š` |
| 42 | `”` |
| 40 | `ː` |

### unknown_feature

| count | error_token | suggested |
|------:|-------------|-----------|
| 56 | `voiced` | `voice` |
| 22 | `sibilant` | `sonorant` |
| 18 | `dental` | `ldental` |
| 14 | `open` | `ten` |
| 13 | `palatal` | `latrl` |
| 12 | `lowtone` | `contin` |
| 9 | `short` | `snrt` |
| 9 | `fortis` | `contin` |
| 9 | `sameC` | `sec` |
| 9 | `glottalized` | `contin` |
| 8 | `hightone` | `high` |
| 7 | `mid` | `man` |
| 6 | `lenis` | `tens` |
| 5 | `velar` | `delay` |
| 5 | `guttural` | `lateral` |
| 5 | `alveolar` | `delay` |
| 4 | `closed` | `cons` |
| 4 | `uvular` | `lar` |
| 4 | `weak` | `man` |
| 4 | `glottal` | `lateral` |
| 3 | `fallingtone` | `length` |
| 3 | `stressed` | `stress` |
| 3 | `AP` | `rt` |
| 2 | `lowfallingtone` | `continuant` |
| 2 | `highrisingtone` | `strident` |
| 2 | `fricative` | `rhotic` |
| 1 | `intertonic` | `anterior` |
| 1 | `close` | `cons` |
| 1 | `lowpitch` | `voice` |
| 1 | `highpitch` | `high` |
| 1 | `rounded` | `round` |
| 1 | `aspirated` | `spread` |
| 1 | `affricate` | `stridnt` |
| 1 | `tonic` | `cons` |
| 1 | `glide` | `click` |
| 1 | `RP` | `rt` |
| 1 | `palatalized` | `latrl` |
| 1 | `creakyvoice` | `voice` |
| 1 | `labiovelar` | `labiodental` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 15 | `R` |
| 12 | `E` |
| 9 | `U` |
| 7 | `H` |
| 6 | `B` |
| 6 | `M` |
| 5 | `K` |
| 5 | `T` |
| 3 | `D` |
| 3 | `Y` |
| 2 | `I` |
| 2 | `X` |
| 2 | `A` |
| 1 | `W` |
| 1 | `Q` |

## Notes

- Inventory runs per corpus rule via `SoundChangeRuleSet` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
