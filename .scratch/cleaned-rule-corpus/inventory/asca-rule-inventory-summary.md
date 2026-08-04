# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9201** (one per corpus rule)
- OK: **5456** (59.3%)
- Fail: **3745** (40.7%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 1470 | `unknown_character` |
| 1239 | `syntax_other` |
| 359 | `expected_underscore` |
| 242 | `unknown_feature` |
| 109 | `unknown_grouping` |
| 83 | `prose_or_expected_arrow` |
| 57 | `stuff_after_word_bound` |
| 46 | `malformed_comment` |
| 31 | `diacritic_prereq` |
| 30 | `expected_number` |
| 26 | `panic_other` |
| 26 | `nested_brackets` |
| 15 | `runtime_other` |
| 10 | `runtime_delete_only_segment` |
| 2 | `other` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 254 | `“` |
| 239 | `ː` |
| 223 | `→` |
| 51 | `₁` |
| 49 | `’` |

### unknown_feature

| count | error_token |
|------:|-------------|
| 51 | `voiced` |
| 22 | `sibilant` |
| 18 | `dental` |
| 14 | `open` |
| 13 | `palatal` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 18 | `K` |
| 17 | `R` |
| 13 | `U` |
| 10 | `B` |
| 9 | `M` |

## Notes

- Inventory runs per corpus rule via `SoundChangeRuleSet` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
