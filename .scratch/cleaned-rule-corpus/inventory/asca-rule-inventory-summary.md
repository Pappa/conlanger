# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9201** (one per corpus rule)
- OK: **5299** (57.6%)
- Fail: **3902** (42.4%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 1687 | `unknown_character` |
| 1204 | `syntax_other` |
| 355 | `expected_underscore` |
| 233 | `unknown_feature` |
| 106 | `unknown_grouping` |
| 83 | `prose_or_expected_arrow` |
| 55 | `stuff_after_word_bound` |
| 45 | `malformed_comment` |
| 31 | `diacritic_prereq` |
| 26 | `expected_number` |
| 26 | `nested_brackets` |
| 25 | `panic_other` |
| 15 | `runtime_other` |
| 9 | `runtime_delete_only_segment` |
| 2 | `other` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 266 | `—` |
| 241 | `“` |
| 233 | `ː` |
| 219 | `→` |
| 50 | `₁` |

### unknown_feature

| count | error_token |
|------:|-------------|
| 47 | `voiced` |
| 21 | `sibilant` |
| 18 | `dental` |
| 14 | `open` |
| 13 | `palatal` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 18 | `K` |
| 15 | `R` |
| 13 | `U` |
| 9 | `M` |
| 9 | `B` |

## Notes

- Inventory runs per corpus rule via `SoundChangeRuleSet` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
