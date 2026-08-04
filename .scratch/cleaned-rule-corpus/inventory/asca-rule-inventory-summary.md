# Cleaned rule corpus — ASCA validation inventory

- Source YAML: `datadiachronica/index_diachronica_parsed.yml`
- Probe words: `tests/fixtures/asca_probe_words.wsca`
- Checker: `validate_asca` / asca **asca 0.10.2**
- Rows: **9201** (one per corpus rule)
- OK: **4466** (48.5%)
- Fail: **4735** (51.5%)

## Failure classes

| count | failure_class |
|------:|---------------|
| 2615 | `unknown_character` |
| 1058 | `syntax_other` |
| 317 | `unknown_grouping` |
| 292 | `expected_underscore` |
| 200 | `unknown_feature` |
| 57 | `prose_or_expected_arrow` |
| 45 | `stuff_after_word_bound` |
| 31 | `malformed_comment` |
| 27 | `nested_brackets` |
| 25 | `diacritic_prereq` |
| 23 | `panic_other` |
| 21 | `expected_number` |
| 13 | `runtime_other` |
| 9 | `runtime_delete_only_segment` |
| 2 | `other` |

## Notes

- Inventory runs per corpus rule via `SoundChangeRuleSet` + `validate_asca`.
- Full rows: [asca-rule-inventory.csv](asca-rule-inventory.csv)
