# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9201** (one per corpus rule)
- OK: **4655** (50.6%)
- Fail: **4546** (49.4%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 2605 | `unknown_character` |
| 1085 | `syntax_other` |
| 308 | `expected_underscore` |
| 202 | `unknown_feature` |
| 90 | `unknown_grouping` |
| 49 | `stuff_after_word_bound` |
| 48 | `prose_or_expected_arrow` |
| 32 | `malformed_comment` |
| 26 | `nested_brackets` |
| 25 | `diacritic_prereq` |
| 25 | `expected_number` |
| 25 | `panic_other` |
| 15 | `runtime_other` |
| 9 | `runtime_delete_only_segment` |
| 2 | `other` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 1251 | `ː` |
| 266 | `—` |
| 204 | `“` |
| 194 | `→` |
| 49 | `₁` |

### unknown_feature

| count | error_token |
|------:|-------------|
| 41 | `voiced` |
| 20 | `sibilant` |
| 13 | `dental` |
| 13 | `palatal` |
| 11 | `lowtone` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 17 | `K` |
| 15 | `R` |
| 11 | `U` |
| 8 | `T` |
| 7 | `B` |

## Notes

- Inventory runs per corpus rule via `SoundChangeRuleSet` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
