# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `data/diachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9316** (one per corpus rule)
- OK: **6237** (66.9%)
- Fail: **3079** (33.1%)
- Sections all OK: **120 / 714** (16.8%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 1155 | `syntax_other` |
| 997 | `unknown_character` |
| 357 | `expected_underscore` |
| 248 | `unknown_feature` |
| 85 | `unknown_grouping` |
| 56 | `prose_or_expected_arrow` |
| 33 | `panic_other` |
| 30 | `expected_number` |
| 28 | `nested_brackets` |
| 25 | `diacritic_prereq` |
| 20 | `runtime_delete_only_segment` |
| 17 | `stuff_after_word_bound` |
| 16 | `runtime_other` |
| 10 | `malformed_comment` |
| 2 | `other` |

## Common Errors

### unknown_character

| count | error_token |
|------:|-------------|
| 242 | `ː` |
| 51 | `₁` |
| 49 | `₀` |
| 48 | `Š` |
| 44 | `”` |

### unknown_feature

| count | error_token |
|------:|-------------|
| 54 | `voiced` |
| 22 | `sibilant` |
| 18 | `dental` |
| 14 | `open` |
| 13 | `palatal` |

### unknown_grouping

| count | error_token |
|------:|-------------|
| 18 | `K` |
| 15 | `R` |
| 7 | `E` |
| 7 | `H` |
| 6 | `M` |

## Notes

- Inventory runs per corpus rule via `SoundChangeRuleSet` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
