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

### unknown_grouping

| count | error_token |
|------:|-------------|
| 15 | `R` |
| 12 | `E` |
| 9 | `U` |
| 7 | `H` |
| 6 | `B` |

## Notes

- Inventory runs per corpus rule via `SoundChangeRuleSet` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
